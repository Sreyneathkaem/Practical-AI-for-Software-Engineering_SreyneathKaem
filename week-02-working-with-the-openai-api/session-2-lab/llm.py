"""
llm.py — the LLM service wrapper.

This is the single most important idea in Lab 2: instead of scattering API
calls, error handling, retries and token tracking across every feature, we
put all of that in ONE place. Every part of the application talks to the
model through LLMService, and nowhere else.

Responsibilities (mapped to the lab requirements):
  R1  API integration        -> ask() / stream()
  R6  Error handling         -> _classify_error() + friendly messages
  R7  Token tracking         -> Usage + last_usage / total_usage
  R8  Streaming              -> stream()
  Step 8  Retry w/ backoff   -> _call_with_retries()
"""

from __future__ import annotations

import os
import random
import time
from dataclasses import dataclass, field

import config


# --------------------------------------------------------------------------
# Errors — we distinguish failures we can retry from failures we cannot.
# --------------------------------------------------------------------------
class LLMError(Exception):
    """Base class for all errors raised by the service. Carries a message
    that is safe (and friendly) to show to an end user."""

    user_message = "Something went wrong contacting the AI service."


class ConfigurationError(LLMError):
    """Terminal — a missing/invalid key or bad setup. Retrying will not help."""

    user_message = "Error: API key is not configured.\nPlease check your .env file."


class InvalidRequestError(LLMError):
    """Terminal — the request itself is malformed (e.g. context too large)."""

    user_message = "The request could not be processed. Please adjust your input."


class RateLimitError(LLMError):
    """Transient — the service is busy. Safe to retry with backoff."""

    user_message = "The AI service is temporarily busy.\nPlease wait and try again."


class ServiceUnavailableError(LLMError):
    """Transient — network error, timeout, or temporary server fault."""

    user_message = "Unable to contact the AI service.\nPlease try again later."


# --------------------------------------------------------------------------
# Token usage (R7)
# --------------------------------------------------------------------------
@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.input_tokens + self.output_tokens

    def __add__(self, other: "Usage") -> "Usage":
        return Usage(
            self.input_tokens + other.input_tokens,
            self.output_tokens + other.output_tokens,
        )

    def format(self) -> str:
        return (
            f"[Usage: {self.input_tokens} input + {self.output_tokens} output "
            f"= {self.total_tokens} tokens]"
        )


@dataclass
class LLMService:
    """A thin, resilient wrapper around the Chat Completions API."""

    model: str = config.DEFAULT_MODEL
    temperature: float = config.DEFAULT_TEMPERATURE
    max_tokens: int = config.DEFAULT_MAX_TOKENS
    max_retries: int = config.MAX_RETRIES

    last_usage: Usage = field(default_factory=Usage)
    total_usage: Usage = field(default_factory=Usage)
    _client: object = field(default=None, repr=False)

    # ---- setup -----------------------------------------------------------
    def _get_client(self):
        """Create the OpenAI client lazily so importing this module never
        requires a key or the network. Raises ConfigurationError if the key
        is missing (R9 / Step 7 Case A)."""
        if self._client is not None:
            return self._client

        if not os.environ.get("OPENAI_API_KEY"):
            raise ConfigurationError()

        try:
            from openai import OpenAI  # imported here so tests can run without it
        except ImportError as exc:  # pragma: no cover
            raise ConfigurationError(
                "The 'openai' package is not installed. Run: pip install openai"
            ) from exc

        self._client = OpenAI()  # reads OPENAI_API_KEY from the environment
        return self._client

    # ---- public API ------------------------------------------------------
    def ask(self, messages: list[dict], *, temperature=None, max_tokens=None) -> str:
        """Send a conversation and return the assistant's full reply.
        Handles retries, classifies errors, and records token usage."""
        response = self._call_with_retries(
            messages,
            temperature=self._pick(temperature, self.temperature),
            max_tokens=self._pick(max_tokens, self.max_tokens),
            stream=False,
        )
        self._record_usage(response)
        return self._extract_text(response)

    def stream(self, messages: list[dict], *, temperature=None, max_tokens=None):
        """Yield chunks of the assistant's reply as they are generated (R8).

        Note: usage is not always available on streamed responses, so token
        tracking may be approximate here — check your SDK/model version."""
        stream = self._call_with_retries(
            messages,
            temperature=self._pick(temperature, self.temperature),
            max_tokens=self._pick(max_tokens, self.max_tokens),
            stream=True,
        )
        for chunk in stream:
            try:
                delta = chunk.choices[0].delta
                piece = getattr(delta, "content", None)
            except (AttributeError, IndexError):
                piece = None
            if piece:
                yield piece

    # ---- retry loop (Step 8) --------------------------------------------
    def _call_with_retries(self, messages, *, temperature, max_tokens, stream):
        attempt = 0
        while True:
            try:
                client = self._get_client()
                return client.chat.completions.create(
                    model=self.model,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                )
            except LLMError as err:
                # Configuration/request errors are terminal — do NOT retry.
                if isinstance(err, (ConfigurationError, InvalidRequestError)):
                    raise
                self._sleep_or_raise(err, attempt)
                attempt += 1
            except Exception as raw:  # noqa: BLE001 — classify SDK/network errors
                err = self._classify_error(raw)
                if isinstance(err, (ConfigurationError, InvalidRequestError)):
                    raise err
                self._sleep_or_raise(err, attempt)
                attempt += 1

    def _sleep_or_raise(self, err: LLMError, attempt: int):
        """Wait using exponential backoff + jitter, or give up if we've
        exhausted our retries."""
        if attempt >= self.max_retries - 1:
            raise err
        delay = min(config.BACKOFF_BASE * (2 ** attempt), config.BACKOFF_MAX)
        delay += random.uniform(0, config.BACKOFF_BASE)  # jitter
        time.sleep(delay)

    # ---- helpers ---------------------------------------------------------
    @staticmethod
    def _classify_error(raw: Exception) -> LLMError:
        """Map a raw SDK/network exception onto our retry policy by name.
        We match on class name so we don't hard-depend on a specific SDK
        version's exception hierarchy."""
        name = type(raw).__name__.lower()
        text = str(raw).lower()

        if "authentication" in name or "permission" in name or "invalid api key" in text:
            return ConfigurationError()
        if "ratelimit" in name or "rate limit" in text or "429" in text:
            return RateLimitError()
        if "badrequest" in name or "invalidrequest" in name or "context length" in text:
            return InvalidRequestError()
        if any(k in name for k in ("timeout", "connection", "apierror", "internalserver")):
            return ServiceUnavailableError()
        return ServiceUnavailableError()

    def _record_usage(self, response) -> None:
        usage = getattr(response, "usage", None)
        # Field names can vary by model/API version — read defensively.
        inp = _first_attr(usage, ("prompt_tokens", "input_tokens"))
        out = _first_attr(usage, ("completion_tokens", "output_tokens"))
        self.last_usage = Usage(inp, out)
        self.total_usage = self.total_usage + self.last_usage

    @staticmethod
    def _extract_text(response) -> str:
        try:
            return response.choices[0].message.content or ""
        except (AttributeError, IndexError):
            return ""

    @staticmethod
    def _pick(value, default):
        return default if value is None else value


def _first_attr(obj, names, default=0):
    for n in names:
        val = getattr(obj, n, None)
        if val is not None:
            return int(val)
    return default
