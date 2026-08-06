"""
main.py — CLI and conversation loop for the Configurable Text Assistant.

main.py owns the user experience: parsing flags, keeping the conversation
history, printing output, and handling interactive commands. Everything that
touches the API lives in llm.py — main.py never calls the model directly.

Usage:
    python main.py --persona tutor --temperature 0.4 --max-tokens 500 --stream

Type /help inside the session for interactive commands.
"""

from __future__ import annotations


import argparse
import json
import sys
from pathlib import Path

import config
from llm import LLMService, LLMError, ConfigurationError

# Load variables from a local .env file if python-dotenv is available (R9).
try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass  # dotenv is optional; the env var may already be set another way.


def parse_args(argv=None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Configurable Text Assistant")
    p.add_argument("--persona", default="default",
                   help="tutor | reviewer | interviewer | default")
    p.add_argument("--temperature", type=float, default=config.DEFAULT_TEMPERATURE)
    p.add_argument("--max-tokens", type=int, default=config.DEFAULT_MAX_TOKENS,
                   dest="max_tokens")
    p.add_argument("--model", default=config.DEFAULT_MODEL,
                   help="override the model name")
    p.add_argument("--stream", action="store_true",
                   help="stream the response progressively")
    return p.parse_args(argv)


def print_banner(args) -> None:
    print("+------------------------------------+")
    print("|       Practical AI Assistant       |")
    print("+------------------------------------+")
    print(f"Persona: {args.persona}")
    print(f"Temperature: {args.temperature}")
    print(f"Max tokens: {args.max_tokens}")
    print(f"Streaming: {'enabled' if args.stream else 'disabled'}")
    print("Type /help for commands.  Type /quit to exit.\n")


HELP_TEXT = """\
Commands:
  /help                 show this help
  /persona <name>       switch persona (resets the conversation)
  /temperature <value>  change temperature (0.0 - 2.0)
  /tokens <n>           change the maximum output tokens
  /usage                show total tokens used this session
  /clear                clear the conversation history
  /save <file>          save the conversation to a JSON file
  /load <file>          load a conversation from a JSON file
  /quit                 exit
"""


class Session:
    """Holds the mutable state of one chat session: the service, the current
    persona, and the conversation history (R5)."""

    def __init__(self, args):
        self.args = args
        self.service = LLMService(
            model=args.model,
            temperature=args.temperature,
            max_tokens=args.max_tokens,
        )
        self.persona_name = args.persona
        self.reset_conversation()

    # ---- conversation state ---------------------------------------------
    def reset_conversation(self) -> None:
        system_prompt = config.get_persona(self.persona_name)
        # The conversation is just data — a list of role/content messages.
        self.messages = [{"role": "system", "content": system_prompt}]

    def save_messages(self, file_path: str) -> bool:
        try:
            with Path(file_path).open("w", encoding="utf-8") as handle:
                json.dump(self.messages, handle, indent=2)
        except OSError as exc:
            print(f"Could not save conversation to {file_path}: {exc}")
            return False

        print(f"Conversation saved to {file_path}.")
        return True

    def load_messages(self, file_path: str) -> bool:
        try:
            with Path(file_path).open("r", encoding="utf-8") as handle:
                payload = json.load(handle)
        except FileNotFoundError:
            print(f"Could not find conversation file: {file_path}")
            return False
        except json.JSONDecodeError:
            print(f"Could not read conversation file: {file_path}")
            return False
        except OSError as exc:
            print(f"Could not read conversation file: {file_path}: {exc}")
            return False

        if not isinstance(payload, list):
            print("Conversation file is invalid. Expected a list of messages.")
            return False

        for item in payload:
            if not isinstance(item, dict):
                print("Conversation file is invalid. Each message must be a dict.")
                return False
            if "role" not in item or "content" not in item:
                print("Conversation file is invalid. Each message must have role and content.")
                return False
            if not isinstance(item["role"], str) or not isinstance(item["content"], str):
                print("Conversation file is invalid. Message role and content must be strings.")
                return False

        self.messages = payload
        print(f"Conversation loaded from {file_path}.")
        return True

    # ---- command handling -----------------------------------------------
    def handle_command(self, line: str) -> bool:
        """Return True if the app should keep running, False to quit."""
        parts = line.strip().split(maxsplit=1)
        cmd = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if cmd in ("/quit", "/exit"):
            print("Goodbye.")
            return False
        if cmd == "/help":
            print(HELP_TEXT)
        elif cmd == "/persona":
            if arg:
                self.persona_name = arg
                self.reset_conversation()
                print(f"Persona changed to '{arg}' (conversation reset).")
            else:
                print("Usage: /persona <tutor|reviewer|interviewer|default>")
        elif cmd == "/temperature":
            self._set_float("temperature", arg, 0.0, 2.0)
        elif cmd == "/tokens":
            self._set_int("max_tokens", arg)
        elif cmd == "/usage":
            print(self.service.total_usage.format())
        elif cmd == "/clear":
            self.reset_conversation()
            print("Conversation cleared.")
        elif cmd == "/save":
            if arg:
                self.save_messages(arg)
            else:
                print("Usage: /save <file>")
        elif cmd == "/load":
            if arg:
                self.load_messages(arg)
            else:
                print("Usage: /load <file>")
        else:
            print(f"Unknown command: {cmd}. Type /help.")
        return True

    def _set_float(self, attr, raw, lo, hi):
        try:
            value = float(raw)
        except ValueError:
            print("Please provide a number.")
            return
        if not lo <= value <= hi:
            print(f"Value must be between {lo} and {hi}.")
            return
        old = getattr(self.service, attr)
        setattr(self.service, attr, value)
        print(f"{attr.capitalize()} changed from {old} -> {value}")

    def _set_int(self, attr, raw):
        try:
            value = int(raw)
        except ValueError:
            print("Please provide a whole number.")
            return
        old = getattr(self.service, attr)
        setattr(self.service, attr, value)
        print(f"{attr} changed from {old} -> {value}")

    # ---- one turn --------------------------------------------------------
    def ask_turn(self, user_input: str) -> None:
        self.messages.append({"role": "user", "content": user_input})
        try:
            if self.args.stream:
                reply = self._stream_reply()
            else:
                reply = self.service.ask(self.messages)
                print(reply)
        except LLMError as err:
            # Friendly, user-facing message — never a raw traceback (R6).
            print(err.user_message)
            # Roll back the unanswered user message so history stays clean.
            self.messages.pop()
            return

        # Remember the assistant's reply so the next turn has context (R5).
        self.messages.append({"role": "assistant", "content": reply})
        # Show token usage after each request (R7).
        print(self.service.last_usage.format())

    def _stream_reply(self) -> str:
        print("Assistant:")
        collected = []
        for piece in self.service.stream(self.messages):
            collected.append(piece)
            sys.stdout.write(piece)
            sys.stdout.flush()
        print()  # newline after the streamed text
        return "".join(collected)


def main(argv=None) -> int:
    args = parse_args(argv)
    session = Session(args)
    print_banner(args)

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0

        if not user_input:
            continue
        if user_input.startswith("/"):
            if not session.handle_command(user_input):
                return 0
            continue

        session.ask_turn(user_input)


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except ConfigurationError as err:
        # Fail clearly if the key is missing before we even start (R9).
        print(err.user_message)
        raise SystemExit(1)