# AI Student Assistant — Session 7 (MCP)

**Course:** Practical AI for Software Engineering (FESE307)
**Topic:** Agentic Software Architecture — AI Agents, Tool Calling, Workflows, Multi-Agent Systems, and the Model Context Protocol (MCP)

A tiny, readable example of an **AI agent** that answers university questions by
calling **tools** exposed over the **Model Context Protocol (MCP)**. The business
problem is deliberately simple so you can focus on the *architecture*.

> You can run the whole thing **without an API key** — see [Offline mode](#offline-mode).

---

## Project Overview

The Student Assistant answers questions like *"How many credits is FESE307?"* or
*"Calculate my GPA for A, B+, B, C."*

It does this the way real agentic systems do:

1. one **AI agent** decides *what the user wants* and *which tool to use*;
2. the tool runs on an **MCP server** and does the actual, deterministic work;
3. the agent turns the tool's structured result into a natural-language answer.

The AI never does the maths itself — a real Python tool computes the GPA. That
separation (reasoning vs. deterministic execution) is the whole point of the lab.

---

## Learning Architecture

```text
User
  ↓
Student Assistant Agent      (uses an LLM to decide + phrase)
  ↓
MCP Client                   (discovers + calls tools over MCP)
  │
  ├───────────────┐
  ↓               ↓
Academic MCP    Math MCP
Server          Server
(:8001)         (:8002)
  │               │
  ↓               ↓
Academic Tools  Math Tools
search_course   calculate_gpa
search_policy   calculate_average
get_schedule
```

We start with **one agent** on purpose. One agent with a few well-designed tools
is usually enough. Multi-agent architecture appears later, as a *design* question.

---

## Components

| Term | In this project | Responsibility |
|---|---|---|
| **Tool** | functions in `servers/*.py` | a deterministic capability (a lookup, a calculation) |
| **MCP Server** | `academic_server.py`, `math_server.py` | exposes tools using MCP |
| **MCP Client** | `MCPClient` in `agent/student_agent.py` | connects to servers, discovers + calls tools |
| **Agent** | `StudentAssistantAgent` | uses an LLM to choose tools and phrase the answer |
| **LLM** | `RealLLM` / `MockLLM` | the reasoning engine (or an offline stand-in) |

- **Student Assistant Agent** — the brain. Decides which tool to call, then explains the result.
- **MCP Client** — the connector. Speaks MCP to both servers and performs tool discovery.
- **Academic MCP Server** — course, schedule, and policy tools (port 8001).
- **Math MCP Server** — GPA and average tools (port 8002).
- **Tools** — plain Python functions doing one job each.

---

## Prerequisites

- Python 3.10+
- `pip`
- (Optional) an OpenAI or OpenAI-compatible API key. Not required — see below.

---

## Setup

```bash
# 1. Get the code
cd session-07-mcp-agent

# 2. Create and activate a virtual environment
python -m venv .venv
source .venv/bin/activate           # macOS / Linux
# .venv\Scripts\activate            # Windows (PowerShell / cmd)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create your .env file
cp .env.example .env                 # macOS / Linux
# copy .env.example .env             # Windows
```

Open `.env` and either:

- paste your key into `OPENAI_API_KEY=...` (real LLM), **or**
- leave it blank to use **offline mock mode** (recommended for a first run).

Your key is read from `.env` only — it is never hard-coded and `.env` is
git-ignored.

---

## Running the Application

You need **three terminals**, all started from the **project root** with the
virtual environment activated.

**Terminal 1 — Academic MCP server**
```bash
python servers/academic_server.py
# serves MCP at http://127.0.0.1:8001/mcp
```

**Terminal 2 — Math MCP server**
```bash
python servers/math_server.py
# serves MCP at http://127.0.0.1:8002/mcp
```

**Terminal 3 — the assistant**
```bash
python app.py            # interactive chat
# or:
python app.py --demo     # run the example questions once
python app.py "How many credits is FESE307?"   # one question, then exit
```

Type `quit` to leave the interactive chat.

### Offline mode

If `OPENAI_API_KEY` is blank (or you set `OFFLINE=1`), Terminal 3 prints:

```
LLM mode : MOCK (offline, no API key needed)
```

The mock is a small keyword router that imitates tool selection so the whole
architecture runs and can be traced without any credentials. It is **not** real
reasoning — the real path is the OpenAI model in `RealLLM`.

---

## Example Questions

```text
What is FESE307?
How many credits is ICT304?
When is ICT305?
What is the attendance policy?
Calculate my GPA for A, B+, B, and C.
```

For each question the app prints the full trace:

```text
──────── USER QUERY ────────
──────── AGENT DECISION ────────   selected tool + arguments
──────── TOOL RESULT ────────      structured JSON + timing
──────── FINAL RESPONSE ────────   the natural-language answer
```

That trace is the point: you can see exactly **which part was the LLM** (decision
+ phrasing) and **which part was deterministic Python** (the tool result).

---

## Project Structure

```text
session-07-mcp-agent/
├── README.md              # this file
├── LAB.md                 # the 90-minute guided lab
├── requirements.txt
├── .env.example
├── .gitignore
│
├── data/                  # small, local sample data (no database)
│   ├── courses.py
│   ├── schedules.py
│   └── policies.py
│
├── servers/               # MCP servers (expose tools)
│   ├── academic_server.py
│   └── math_server.py
│
├── agent/                 # the agent, MCP client, and LLM providers
│   ├── student_agent.py
│   └── config.py
│
├── app.py                 # command-line entry point
│
└── solution/              # instructor reference (completed). Not needed to do the lab.
```

---

## Troubleshooting

- **"Could not reach the 'academic' MCP server"** — Terminal 1 isn't running, or is on a different port. Start it, then retry.
- **`ModuleNotFoundError: mcp`** — activate the venv and re-run `pip install -r requirements.txt`.
- **Port already in use** — another process holds 8001/8002. Stop it, or change `ACADEMIC_MCP_URL` / `MATH_MCP_URL` in `.env` and the matching port in the server file.
- **Nothing happens with a real key** — check the key and `OPENAI_MODEL` in `.env`; try offline mode (`OFFLINE=1`) to confirm the servers work.

---

## Where to go next

Open **`LAB.md`** and follow the 90-minute guided exercise.
