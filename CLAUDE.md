# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

Teaching materials for **Practical AI for Software Engineering** — a 10-week, Year-3 undergraduate course at CamTech on building LLM-powered applications from an engineer's perspective (APIs, prompting, RAG, orchestration, deployment). It is **not** a single application: it is a course repo where each week is a self-contained folder of slides plus one or more hands-on labs. New weeks are added as the course progresses.

Build context for authors lives in `.context/` — a program tracker (status of all 10 weeks), course reference (env/provider conventions, naming rules), authoring guidelines, and skeleton templates for new material. Consult it when adding or changing a week, and update the tracker when you do.

Because these are labs, expect two distinct kinds of code:
- **Starter code with `TODO`s left unimplemented** (e.g. `week-01/.../askbot.py`, where `chat_loop()` raises `NotImplementedError`). Students fill these in. Do not "complete" them unprivileged — only touch them when explicitly asked.
- **Reference implementations** meant to be complete and correct (e.g. `week-02/.../session-2-lab/`). These demonstrate the target design and can be edited/extended.

## Running the labs

Each lab is an independent Python project with its own `requirements.txt` and `.env`. There is no repo-wide build, test suite, or dependency manifest. Work from inside the specific lab folder:

```bash
cd week-02-working-with-the-openai-api/session-2-lab
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then add a real key
python main.py --persona tutor --temperature 0.4 --stream
```

Week 1's lab uses `venv/` and `askbot.py` (`python askbot.py --once "..."`); Week 2's uses `.venv/` and `main.py`. Check the lab's own `README.md` for its exact flags and setup.

There are no automated tests in the repo. `llm.py` is deliberately written so it can be imported without a key or network (the OpenAI client is created lazily), which makes it unit-testable — but no test files exist yet.

## Provider configuration — the key detail

Labs target an **OpenAI-compatible** API and are provider-agnostic (Groq, OpenAI, or local Ollama) — only `.env` changes, never the code. **The two labs use different environment-variable conventions**, so don't assume one applies to the other:

- **Week 1** (`askbot.py`): reads `LLM_API_KEY`, `LLM_BASE_URL`, `LLM_MODEL`. Passing `base_url` explicitly is what enables Groq/Ollama. Default model `llama-3.3-70b-versatile`.
- **Week 2** (`llm.py`): reads `OPENAI_API_KEY` (and optional `OPENAI_MODEL`) via the SDK's default env lookup; model otherwise comes from `config.DEFAULT_MODEL`, which ships as the placeholder `"YOUR_MODEL"` and must be set for the code to run.

`.env` and `*.key` are git-ignored at the repo root. Never commit a real key or hard-code one in source — the labs teach this as an explicit requirement (R9).

## Architecture of the Week 2 reference lab

This is the repo's canonical example of the design students are meant to reach, and its central lesson is worth knowing before editing:

**All API concerns live in one place.** `main.py` never calls the model directly. The flow is a straight line: `main.py → Session → LLMService (llm.py) → OpenAI API`.

- `llm.py` — the `LLMService` wrapper. It owns error handling, retries, and token tracking. Raw SDK/network exceptions are mapped to a small hierarchy of `LLMError` subclasses via `_classify_error()`, which matches on exception **class name and message substrings** (not the SDK's concrete types) so it survives SDK version changes. Errors are split into **terminal** (`ConfigurationError`, `InvalidRequestError` — never retried) vs **transient** (`RateLimitError`, `ServiceUnavailableError` — retried with exponential backoff + jitter, capped by `config.MAX_RETRIES`). Every `LLMError` carries a `user_message` safe to print to end users. Token counts are read defensively (`prompt_tokens`/`input_tokens`, etc.) because field names vary by model.
- `config.py` — behaviour-as-data: generation defaults, retry/backoff constants, and the `PERSONAS` dict (system prompts). Changing a persona or a default means editing data here, not logic elsewhere.
- `main.py` — owns the UX only: arg parsing, the `Session` object holding conversation `messages` (the list of role/content dicts that gives the bot memory), interactive `/`-commands, and streaming display. On an error it prints `err.user_message` and rolls back the unanswered user message so history stays clean.

When extending this lab, preserve that separation: model interaction goes in `llm.py`, tunable behaviour in `config.py`, user interaction in `main.py`.

## Conventions

When writing prose for this repo (READMEs, handouts, comments), write like a person, not a machine. Do not use em dashes or en dashes anywhere; use a comma, colon, period, or parentheses instead, and keep the hyphen only for compound words. Prefer short, direct sentences, cut filler, and address the student as "you". Full guidance lives in `.context/authoring-guidelines.md`.

Lab `README.md` files map lettered requirements (R1–R10) to the code that satisfies them and often contain reflection questions students answer inline — treat those as part of the deliverable, not stray prose. `NOTES.md` files are student submission artifacts. The `.docx`/`.pptx` files are the lab handouts and lecture decks (source of truth for lab instructions); read them when you need the full assignment spec rather than inferring it from starter code.
