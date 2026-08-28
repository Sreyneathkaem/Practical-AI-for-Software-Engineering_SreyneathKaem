# Lab 7 — Build an AI Student Assistant with MCP

**Course:** Practical AI for Software Engineering (FESE307)
**Duration:** ~90 minutes, guided
**Format:** read code → run code → modify code → observe behavior

You will build and extend a small AI agent that answers university questions by
calling tools over the **Model Context Protocol (MCP)**. Most of your time is
spent *running and modifying* a working system, not writing it from scratch.

> **Before you start:** finish [README.md → Setup](README.md#setup). You should
> be able to run the three terminals. You do **not** need an API key — offline
> mock mode is fine for the whole lab.

**Vocabulary (use these words precisely today):**

| Term | Meaning |
|---|---|
| **Tool** | a deterministic capability (a lookup or calculation) |
| **Agent** | the component that uses an LLM to decide what to do and which tools to use |
| **MCP Server** | exposes tools using MCP |
| **MCP Client** | connects the app to the MCP servers |
| **Workflow** | a developer-controlled sequence of steps |
| **Orchestrator** | a component that coordinates agents / workflows / tools |

---

## Part 0 — Understand the Architecture  *(5–10 min)*

Look at this picture before touching any code:

```text
User
 ↓
Agent          ← reasoning (LLM): what does the user want? which tool?
 ↓
MCP Client     ← connects + discovers + calls tools
 ↓
MCP Server     ← exposes tools over MCP
 ↓
Tool           ← deterministic Python: does the actual work
```

**Answer these (out loud or in a comment):**

1. Where does **reasoning** happen?
2. Where does **deterministic execution** happen?
3. What does **MCP** connect?

Keep your answers in mind — the trace you see later will confirm them.

---

## Part 1 — Run the Academic MCP Server  *(~15 min)*

Open `servers/academic_server.py`. Find these four things:

- the **server**: `mcp = FastMCP("academic", host="127.0.0.1", port=8001)`
- a **tool definition**: any function decorated with `@mcp.tool()`
- the **tool name**: the function name (e.g. `search_course`)
- the **parameters**: the typed arguments (e.g. `course_code: str`)
- the **returned data**: the `dict` each tool returns

Now run it (**Terminal 1**):

```bash
python servers/academic_server.py
```

Leave it running. In **Terminal 3**, ask a question that uses it:

```bash
python app.py "What is FESE307?"
```

> If Terminal 2 (math server) isn't running yet, you'll see a warning that the
> math server is unavailable — that's fine for this step. Start it when you reach
> Part 3.

Read the trace. Notice the agent selected `search_course`, passed
`{"course_code": "FESE307"}`, and got back structured data.

---

## Part 2 — Add an Academic Tool  *(~10 min)*  — **TODO 1**

The `get_schedule` tool is **registered but not implemented**. Ask:

```bash
python app.py "When is ICT305?"
```

You'll see:

```text
{ "error": "get_schedule is not implemented yet.", ... }
```

Open `servers/academic_server.py` and find **`TODO 1`** inside `get_schedule`.

- **Input:** `course_code: str` (e.g. `"ICT305"`)
- **Output (success):**
  ```python
  {"course_code": "ICT305", "day": "Thursday",
   "time": "14:00-16:00", "room": "Room C-310"}
  ```
- Use the `SCHEDULES` dictionary already imported at the top of the file.
- Copy the *pattern* from `search_course` (normalize the code, look it up,
  return an `error` dict if it isn't found).

When done, **restart Terminal 1** (Ctrl+C, then run it again) and re-ask
*"When is ICT305?"*. You should now get a real schedule.

> **Why restart?** The server loads your code at startup. New tool code takes
> effect only after a restart.

---

## Part 3 — Run the Math MCP Server  *(~10 min)*

Open `servers/math_server.py` and read `calculate_gpa`.

**Discuss:** *Why should GPA be a deterministic Python tool instead of asking the
LLM to "just calculate it"?*
(Hint: correctness, repeatability, and testability. A language model can
mis-add; a function cannot.)

Start it (**Terminal 2**):

```bash
python servers/math_server.py
```

Then test it (**Terminal 3**):

```bash
python app.py "Calculate my GPA for A, B+, B, C."
```

Check the trace: the **tool** produced the number, and the **agent** only
explained it.

---

## Part 4 — Connect the Agent  *(~10 min)*

With **all three terminals** running, start an interactive session:

```bash
python app.py
```

Ask:

```text
What is FESE307?
```

Watch the five sections of the trace:

```text
USER QUERY  →  AGENT DECISION  →  TOOL ARGUMENTS  →  TOOL RESULT  →  FINAL RESPONSE
```

**Answer:**

- Which part was performed by the **LLM**?
- Which part was performed by **normal Python**?

---

## Part 5 — Test Different Tools  *(~10 min)*

Ask each of these and **record which tool was selected**:

```text
What is the attendance policy?
When is ICT304?
Calculate my GPA for A, B+, B, C.
```

| Question | Tool selected |
|---|---|
| attendance policy | |
| when is ICT304 | |
| GPA | |

You've now seen one agent route to several tools across two servers. That is the
core idea of the whole session.

---

## Challenge 1 — Add a New Tool  *(hints only)*  — **TODO 2**

Goal: let the assistant answer *"Can I take ICT304?"* using a prerequisite tool.

```text
User:  Can I take ICT304?
Agent: → check_prerequisite("ICT304")
Tool:  { "course_code": "ICT304", "prerequisite": "ICT303" }
```

In `servers/academic_server.py` there is already a `check_prerequisite(...)`
function — but it is **not** a tool yet. Find **`TODO 2`**.

**Hints:**

- A plain function is not an MCP tool until it is *registered*.
- Look at how `search_course` becomes a tool. What one line makes the
  difference?
- After changing the server, **restart Terminal 1**.
- Confirm with: `python app.py "Can I take ICT304?"`

*(Stuck? The completed version is in `solution/servers/academic_server.py` — try
it yourself first.)*

---

## Challenge 2 — Handle Failure  — **TODO 3**

Simulate an outage: go to **Terminal 1** and press **Ctrl+C** to stop the
academic server. Leave the math server running.

Now ask (in Terminal 3):

```bash
python app.py "What is ICT304?"
```

**Observe:** the assistant fails with a raw technical error instead of a helpful
message. That's the bug.

Open `agent/student_agent.py`, find **`TODO 3`** in `MCPClient.connect_all`, and
make one unavailable server **not** crash the whole assistant.

**What "fixed" looks like:** the app prints a warning, keeps the tools that *did*
connect, and answers outage-affected questions with something like:

```text
Sorry — an information service is currently unavailable. Please try again later.
```

Re-run the same question with the academic server still stopped — you should now
get the friendly message, and math questions should still work.

**Connect the idea:** this is **graceful degradation**. In production you'd also
add **timeouts**, **retries**, and **fallbacks** at these boundaries (Weeks 5–6).

Restart Terminal 1 when you're done.

---

## Challenge 3 — Multi-Step Request

Ask:

```bash
python app.py "Find the credits for ICT304 and FESE307 and tell me the total."
```

Watch the trace, then answer:

1. Which tools are required?
2. How many tool calls occurred?
3. Who decided which tools to call?
4. Where was the final result produced (which component)?

> The agent loop already supports multiple tool calls per question. Trace how the
> results are gathered before the final answer is composed. (If you later switch
> to a real LLM, the same loop handles multi-step reasoning automatically.)

---

## Final Architecture Challenge  *(design, not code)*

Suppose the Student Assistant grows to include:

```text
Academic support · Finance · Student records · Course registration · Technical support
```

Sketch a redesigned architecture. One option:

```text
                     Orchestrator
                         │
          ┌──────────────┼──────────────┐
          ↓              ↓              ↓
     Academic         Finance       Support
       Agent           Agent          Agent
          │              │              │
         MCP            MCP            MCP
```

**Then answer honestly:** *Do you actually need three agents?*

Justify your decision. Multiple agents are worth it only when there is a **real**
reason: different responsibilities, different tool permissions, different domain
expertise, different models, independent scaling, or separate security
boundaries. "It sounds more advanced" is not a reason.

---

## Capstone Connection — Architecture Design v1

This is the **Session 7 milestone**. Sketch the architecture of *your own*
capstone:

```text
User
 ↓
Application
 ↓
Agent / Workflow / Orchestrator
 ↓
Tools / MCP
 ↓
Database / API / External Service
```

Label, for your system:

- **Agent** — where reasoning happens
- **Workflow** — where the sequence is fixed by you
- **Tool** — what capabilities the AI can invoke
- **MCP server** — your integration boundaries
- **External system** — your authoritative data sources
- **Failure boundary** — where timeouts / fallbacks / errors are handled

Then answer in 3–5 sentences:

> **Why is this architecture appropriate for your application?**

Start with the **simplest** architecture that satisfies your requirements, and
add complexity only when a requirement forces it.

---

## What you changed today

| File | What you edited |
|---|---|
| `servers/academic_server.py` | TODO 1 (`get_schedule`), TODO 2 (register `check_prerequisite`) |
| `agent/student_agent.py` | TODO 3 (`connect_all` error handling) |

Everything else you **read and ran** — you didn't need to rewrite it. That's the
lesson: a small, well-separated architecture is easy to extend one tool at a
time.
