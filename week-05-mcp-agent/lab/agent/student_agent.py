"""
Student Assistant Agent  +  MCP Client  +  LLM providers
===================================================================
This file wires the AI system together. Read it top-to-bottom:

    1. Data shapes         ToolCall, LLMResponse
    2. MCPClient           connects to the MCP servers, discovers tools,
                           and calls tools over the MCP protocol
    3. LLM providers       RealLLM (OpenAI)  and  MockLLM (offline)
                           -- both return the SAME shape, so the agent
                              loop below never changes
    4. StudentAssistantAgent
                           the control loop: ask the model, run any tool
                           calls, feed results back, produce an answer

Vocabulary (used consistently everywhere):
    Tool        a deterministic capability (runs on an MCP server)
    Agent       the component that uses an LLM to decide what to do
    MCP Server  exposes tools using the Model Context Protocol
    MCP Client  connects this app to the MCP servers

Connection model:
    We open a fresh connection to the MCP servers for each question
    (connect -> discover tools -> call tools -> close). This keeps the
    code easy to trace and makes failure handling simple: if a server is
    down, connecting to it fails in one obvious place.
===================================================================
"""

from __future__ import annotations

import asyncio
import json
import re
import time
import uuid
from contextlib import AsyncExitStack
from dataclasses import dataclass, field
from urllib.parse import urlparse

from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

from agent.config import Settings


# ==================================================================
# 1. DATA SHAPES  (the common language between the LLM and the agent)
# ==================================================================
@dataclass
class ToolCall:
    id: str
    name: str
    arguments: dict


@dataclass
class LLMResponse:
    content: str | None
    tool_calls: list[ToolCall] = field(default_factory=list)


class ToolUnavailableError(Exception):
    """Raised when a tool's MCP server is not connected."""


# ==================================================================
# 2. MCP CLIENT  (connects to MCP servers and calls their tools)
# ==================================================================
class MCPClient:
    """Connects to the MCP servers over HTTP and routes tool calls.

    Usage:
        async with MCPClient(settings) as client:
            await client.connect_all()
            schemas = client.openai_tools()          # discovered tools
            text = await client.call_tool(name, args)
    """

    def __init__(self, settings: Settings):
        self.settings = settings
        self._server_stacks: list[AsyncExitStack] = []
        self._tool_to_session: dict[str, ClientSession] = {}
        self._tool_schemas: list[dict] = []
        self.unavailable: list[str] = []

    def _targets(self) -> list[tuple[str, str]]:
        return [
            ("academic", self.settings.academic_url),
            ("math", self.settings.math_url),
        ]

    async def __aenter__(self) -> "MCPClient":
        return self

    async def __aexit__(self, *exc):
        # Closing a connection to a server that has gone away can raise noisy
        # teardown errors that are not useful to students. We close what we can
        # and ignore cleanup-only failures.
        for stack in self._server_stacks:
            try:
                await stack.aclose()
            except BaseException:  # noqa: BLE001 (cleanup only)
                pass

    async def connect_all(self):
        """Connect to every MCP server and discover its tools.

        A server that is unreachable is recorded in `self.unavailable`
        instead of crashing the whole assistant; other servers still work.
        """
        for name, url in self._targets():
            try:
                await self._connect_one(name, url)
            except Exception as exc:
                self.unavailable.append(name)
                print(f"  [warning] '{name}' MCP server unavailable: {exc}")

    async def _connect_one(self, name: str, url: str):
        # First, a quick reachability check. If the server is not accepting
        # connections we fail fast with ONE clear error, instead of letting a
        # noisy low-level async error escape when a server simply isn't running.
        await self._probe(name, url)

        # Each server gets its own connection scope, kept open for the lifetime
        # of this client and closed in __aexit__.
        stack = AsyncExitStack()
        read, write, _ = await stack.enter_async_context(streamablehttp_client(url))
        session = await stack.enter_async_context(ClientSession(read, write))
        await session.initialize()
        listed = await session.list_tools()
        self._server_stacks.append(stack)

        # ---- TOOL DISCOVERY ----
        # Ask the MCP server which tools it offers. This is how the agent learns
        # what capabilities exist without hard-coding them.
        for tool in listed.tools:
            self._tool_to_session[tool.name] = session
            self._tool_schemas.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description or "",
                    "parameters": tool.inputSchema or {"type": "object", "properties": {}},
                },
            })
        tool_names = ", ".join(t.name for t in listed.tools)
        print(f"  [connected] {name} MCP server  ->  tools: {tool_names}")

    async def _probe(self, name: str, url: str):
        """Fail fast (with a clean error) if the server port isn't listening."""
        parsed = urlparse(url)
        host = parsed.hostname or "127.0.0.1"
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        try:
            _, writer = await asyncio.wait_for(
                asyncio.open_connection(host, port), timeout=2.0)
            writer.close()
            try:
                await writer.wait_closed()
            except Exception:  # noqa: BLE001
                pass
        except Exception:  # noqa: BLE001 (connection refused / timeout)
            raise ToolUnavailableError(
                f"Could not reach the '{name}' MCP server at {url}."
            ) from None

    def openai_tools(self) -> list[dict]:
        """Return discovered tools in the format an LLM tool-caller expects."""
        return self._tool_schemas

    async def call_tool(self, name: str, arguments: dict) -> str:
        """Call a tool on whichever MCP server owns it. Returns JSON text."""
        session = self._tool_to_session.get(name)
        if session is None:
            raise ToolUnavailableError(
                f"Tool '{name}' is not available (its MCP server may be down)."
            )
        result = await session.call_tool(name, arguments)
        if result.content:
            return result.content[0].text
        return "{}"


# ==================================================================
# 3. LLM PROVIDERS  (both return an LLMResponse)
# ==================================================================
class RealLLM:
    """Talks to a real OpenAI-compatible chat model with tool calling."""

    def __init__(self, settings: Settings):
        from openai import OpenAI  # imported lazily so offline mode needs no key
        self.client = OpenAI(
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
        )
        self.model = settings.openai_model

    def complete(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            tools=tools or None,
            tool_choice="auto",
        )
        msg = resp.choices[0].message
        if msg.tool_calls:
            calls = [
                ToolCall(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=json.loads(tc.function.arguments or "{}"),
                )
                for tc in msg.tool_calls
            ]
            return LLMResponse(content=None, tool_calls=calls)
        return LLMResponse(content=msg.content or "", tool_calls=[])


class MockLLM:
    """A tiny OFFLINE stand-in for an LLM so the lab runs with no API key.

    IMPORTANT: this is NOT real reasoning. It is a small keyword router that
    imitates how a model would *select tools* and *phrase an answer*, purely
    so students can run and trace the architecture without credentials.
    The real intelligence path is RealLLM above.
    """

    GRADE_RE = re.compile(r"(?<![A-Za-z])([ABCDF][+]?)(?![A-Za-z])", re.IGNORECASE)
    CODE_RE = re.compile(r"[A-Za-z]{2,4}\s?\d{3}")

    def complete(self, messages: list[dict], tools: list[dict]) -> LLMResponse:
        available = {t["function"]["name"] for t in tools}
        # If tools have already run this turn, compose the final answer.
        if any(m.get("role") == "tool" for m in messages):
            return LLMResponse(content=self._compose(messages), tool_calls=[])
        user_text = self._last_user(messages)
        calls = self._plan(user_text, available)
        if not calls:
            if self._has_outage(messages):
                return LLMResponse(content=(
                    "Sorry — an information service is currently unavailable. "
                    "Please try again later."))
            return LLMResponse(content=(
                "I can help with courses, schedules, policies, GPA and averages. "
                "Try: 'How many credits is FESE307?' or "
                "'Calculate my GPA for A, B+, B, C.'"))
        return LLMResponse(content=None, tool_calls=calls)

    # ---- helpers ----
    @staticmethod
    def _last_user(messages: list[dict]) -> str:
        for m in reversed(messages):
            if m.get("role") == "user":
                return m.get("content") or ""
        return ""

    @staticmethod
    def _has_outage(messages: list[dict]) -> bool:
        for m in messages:
            if m.get("role") == "system" and "unavailable" in (m.get("content") or "").lower():
                return True
        return False

    def _codes(self, text: str) -> list[str]:
        seen, out = set(), []
        for raw in self.CODE_RE.findall(text):
            code = raw.upper().replace(" ", "")
            if code not in seen:
                seen.add(code)
                out.append(code)
        return out

    def _grades(self, text: str) -> list[str]:
        return [g.upper() for g in self.GRADE_RE.findall(text)]

    @staticmethod
    def _mk(name: str, args: dict) -> ToolCall:
        return ToolCall(id="call_" + uuid.uuid4().hex[:8], name=name, arguments=args)

    def _plan(self, text: str, available: set[str]) -> list[ToolCall]:
        low = text.lower()
        codes = self._codes(text)

        if "gpa" in low and "calculate_gpa" in available:
            return [self._mk("calculate_gpa", {"grades": self._grades(text)})]

        if "average" in low and "calculate_average" in available:
            nums = [float(x) for x in re.findall(r"-?\d+(?:\.\d+)?", text)]
            return [self._mk("calculate_average", {"values": nums})]

        if ("prerequisite" in low or "prereq" in low or "can i take" in low) \
                and "check_prerequisite" in available and codes:
            return [self._mk("check_prerequisite", {"course_code": codes[0]})]

        policy_words = ("policy", "attendance", "absent", "late", "deadline",
                        "submission", "integrity", "plagiarism", "cheat")
        if any(w in low for w in policy_words) and "search_policy" in available:
            return [self._mk("search_policy", {"topic": text})]

        if ("schedule" in low or "when is" in low or "when's" in low
                or "what time" in low) and "get_schedule" in available and codes:
            return [self._mk("get_schedule", {"course_code": c}) for c in codes]

        if codes and "search_course" in available:
            return [self._mk("search_course", {"course_code": c}) for c in codes]

        return []

    def _compose(self, messages: list[dict]) -> str:
        id_to_name: dict[str, str] = {}
        for m in messages:
            if m.get("role") == "assistant" and m.get("tool_calls"):
                for tc in m["tool_calls"]:
                    id_to_name[tc["id"]] = tc["function"]["name"]

        user_text = self._last_user(messages).lower()
        lines: list[str] = []
        course_credits: list[int] = []

        for m in messages:
            if m.get("role") != "tool":
                continue
            name = id_to_name.get(m.get("tool_call_id"), "")
            try:
                data = json.loads(m.get("content") or "{}")
            except json.JSONDecodeError:
                data = {"error": m.get("content")}

            if "error" in data:
                hint = f" ({data['hint']})" if data.get("hint") else ""
                lines.append(f"{data['error']}{hint}")
                continue

            if name == "search_course":
                course_credits.append(int(data["credits"]))
                lines.append(
                    f"{data['course_code']} — {data['name']} is a "
                    f"{data['credits']}-credit course.")
            elif name == "get_schedule":
                lines.append(
                    f"{data['course_code']} meets on {data['day']} "
                    f"({data['time']}) in {data['room']}.")
            elif name == "search_policy":
                lines.append(f"Policy on {data['topic'].replace('_', ' ')}: "
                             f"{data['policy']}")
            elif name == "calculate_gpa":
                lines.append(f"Your GPA is {data['gpa']} "
                             f"(based on {data['count']} course(s)).")
            elif name == "calculate_average":
                lines.append(f"The average is {data['average']}.")
            elif name == "check_prerequisite":
                if data.get("prerequisite"):
                    lines.append(f"{data['course_code']} requires "
                                 f"{data['prerequisite']}.")
                else:
                    lines.append(f"{data['course_code']} has no prerequisite.")
            else:
                lines.append(json.dumps(data))

        if len(course_credits) > 1 and ("total" in user_text or "sum" in user_text):
            lines.append(f"Total credits: {sum(course_credits)}.")

        return " ".join(lines) if lines else "I could not find an answer."


def make_llm(settings: Settings):
    """Pick the LLM provider based on configuration."""
    return MockLLM() if settings.use_mock else RealLLM(settings)


# ==================================================================
# 4. THE AGENT  (control loop + visible tracing)
# ==================================================================
BASE_SYSTEM_PROMPT = (
    "You are the Student Assistant for the course FESE307. "
    "Answer university questions by calling the available tools. "
    "You must NEVER calculate a GPA or an average yourself — always use the "
    "math tools for any calculation. Use search_course, get_schedule and "
    "search_policy for academic questions. Base your final answer only on the "
    "tool results. If a tool returns an error, explain it to the student simply."
)


def _hr(title: str):
    print(f"\n──────── {title} ────────")


class StudentAssistantAgent:
    """One AI agent that reasons with an LLM and acts through MCP tools."""

    def __init__(self, client: MCPClient, llm, max_steps: int = 5):
        self.client = client
        self.llm = llm
        self.max_steps = max_steps

    def _system_prompt(self) -> str:
        if self.client.unavailable:
            names = ", ".join(self.client.unavailable)
            return (BASE_SYSTEM_PROMPT + f"\nSERVICE STATUS: the following "
                    f"information service(s) are currently unavailable: {names}. "
                    f"If the question needs one, tell the student it is "
                    f"temporarily unavailable and to try again later.")
        return BASE_SYSTEM_PROMPT

    async def ask(self, question: str) -> str:
        _hr("USER QUERY")
        print(question)

        messages = [
            {"role": "system", "content": self._system_prompt()},
            {"role": "user", "content": question},
        ]
        tools = self.client.openai_tools()

        for _ in range(self.max_steps):
            response = await asyncio.to_thread(self.llm.complete, messages, tools)

            if not response.tool_calls:
                _hr("FINAL RESPONSE")
                print(response.content)
                return response.content or ""

            messages.append(self._assistant_message(response.tool_calls))
            for call in response.tool_calls:
                _hr("AGENT DECISION")
                print(f"selected tool : {call.name}")
                print(f"arguments     : {json.dumps(call.arguments)}")

                # A tool call can still fail at runtime (bad server, timeout).
                # We convert failures into a normal tool result so the agent
                # can explain them, instead of crashing.
                started = time.time()
                try:
                    result_text = await self.client.call_tool(
                        call.name, call.arguments)
                except ToolUnavailableError as exc:
                    result_text = json.dumps({"error": str(exc)})
                except Exception as exc:  # noqa: BLE001 (network/tool failure)
                    result_text = json.dumps({
                        "error": "That information service is currently "
                                 "unavailable. Please try again later.",
                        "detail": type(exc).__name__,
                    })
                elapsed_ms = int((time.time() - started) * 1000)

                _hr("TOOL RESULT")
                print(f"{result_text}\n(took {elapsed_ms} ms)")

                messages.append({
                    "role": "tool",
                    "tool_call_id": call.id,
                    "name": call.name,
                    "content": result_text,
                })

        _hr("FINAL RESPONSE")
        msg = "Stopped after too many tool calls. Please simplify your question."
        print(msg)
        return msg

    @staticmethod
    def _assistant_message(tool_calls: list[ToolCall]) -> dict:
        return {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments),
                    },
                }
                for tc in tool_calls
            ],
        }