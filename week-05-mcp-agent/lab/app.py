"""
AI Student Assistant — command-line app
===================================================================
This is the entry point students run (Terminal 3).

It:
    1. loads configuration,
    2. connects the MCP CLIENT to the academic + math MCP SERVERS,
    3. starts one AGENT that answers questions using the discovered tools.

A fresh connection is made for each question (connect -> discover -> call
-> close), which keeps the flow easy to follow and makes failures obvious.

Usage (from the project root, with the two servers already running):
    python app.py                      # interactive chat
    python app.py "How many credits is FESE307?"   # one question, then exit
    python app.py --demo               # run a set of example questions

Set OFFLINE=1 (or leave OPENAI_API_KEY blank) to use the offline mock model.
===================================================================
"""

import asyncio
import sys

from agent.config import load_settings
from agent.student_agent import MCPClient, StudentAssistantAgent, make_llm

DEMO_QUESTIONS = [
    "What is FESE307?",
    "How many credits is ICT304?",
    "When is ICT305?",
    "What is the attendance policy?",
    "Calculate my GPA for A, B+, B, and C.",
]

BANNER = r"""
==============================================
   AI Student Assistant  (Session 7 — MCP)
==============================================
"""


async def answer(settings, question: str):
    """Connect to the MCP servers, answer one question, then disconnect."""
    async with MCPClient(settings) as client:
        await client.connect_all()
        agent = StudentAssistantAgent(client, make_llm(settings))
        await agent.ask(question)


async def run(questions: list[str] | None):
    settings = load_settings()
    print(BANNER)
    print(f"LLM mode : {settings.mode}")
    print(f"Academic MCP : {settings.academic_url}")
    print(f"Math MCP     : {settings.math_url}")

    if questions is not None:
        for q in questions:
            await answer(settings, q)
            print()
        return

    print("\nType a question (or 'quit' to exit).")
    loop = asyncio.get_event_loop()
    while True:
        try:
            question = await loop.run_in_executor(None, input, "\nYou: ")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break
        except asyncio.CancelledError:
            # Windows can occasionally deliver a stray cancellation left over
            # from the previous question's MCP connection cleanup, right as
            # we're idling at input(). It's harmless — clear it and keep going.
            task = asyncio.current_task()
            if task is not None:
                task.uncancel()
            continue
        question = question.strip()
        if not question:
            continue
        if question.lower() in {"quit", "exit", "q"}:
            print("Goodbye!")
            break
        try:
            await answer(settings, question)
        except Exception as exc:  # noqa: BLE001
            # In the STARTER code, a DOWN MCP server makes connect_all raise,
            # and the raw error lands here. Lab Challenge 2 (TODO 3) asks you to
            # handle it inside connect_all so this ugly path never triggers.
            print(f"\n[unexpected error] {type(exc).__name__}: {exc}")


def main():
    args = sys.argv[1:]
    if args and args[0] == "--demo":
        asyncio.run(run(DEMO_QUESTIONS))
    elif args:
        asyncio.run(run([" ".join(args)]))
    else:
        asyncio.run(run(None))


if __name__ == "__main__":
    main()
