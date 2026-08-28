# Instructor Solution — completed reference

This folder is a **self-contained, completed** version of the project. Students
do **not** need it to do the lab; use it to check answers or to run a known-good
version.

It runs exactly like the student project (same commands, same ports):

```bash
# from inside solution/
python servers/academic_server.py     # Terminal 1  (:8001)
python servers/math_server.py         # Terminal 2  (:8002)
python app.py --demo                  # Terminal 3
```

## What is completed here

| Lab step | Completed in |
|---|---|
| **TODO 1** — `get_schedule` implemented | `servers/academic_server.py` |
| **Challenge 1 / TODO 2** — `check_prerequisite` registered as a tool | `servers/academic_server.py` |
| **Challenge 2 / TODO 3** — `connect_all` degrades gracefully | `agent/student_agent.py` |
| **Challenge 3** — multi-step tool calls | already supported by the agent loop |

Everything else is identical to the student version.
