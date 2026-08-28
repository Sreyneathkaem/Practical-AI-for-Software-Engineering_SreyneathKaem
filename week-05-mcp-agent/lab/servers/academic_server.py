"""
Academic MCP Server
===================================================================
This is a REAL Model Context Protocol (MCP) server built with the
official MCP Python SDK (FastMCP). It exposes *tools* that the AI agent
can discover and call over the MCP protocol.

What lives here:
    - MCP server definition            -> FastMCP("academic", ...)
    - Tool definitions                 -> functions decorated with @mcp.tool()
    - Deterministic Python logic        -> plain dictionary lookups (no AI here)

The agent (the LLM side) NEVER runs this code directly. It asks the MCP
client to call a tool by name; this server executes the tool and returns
structured data.

Run it (Terminal 1):
    python servers/academic_server.py
It will serve MCP over HTTP at:  http://127.0.0.1:8001/mcp
===================================================================
"""

import os
import sys

# Make the project root importable so `from data.courses import ...` works
# no matter which directory you launch the server from.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP

from data.courses import COURSES, normalize_code
from data.schedules import SCHEDULES
from data.policies import POLICIES, resolve_topic

# The MCP server. host/port make it reachable by the MCP client over HTTP.
mcp = FastMCP("academic", host="127.0.0.1", port=8001)


# ------------------------------------------------------------------
# TOOL: search_course
# ------------------------------------------------------------------
@mcp.tool()
def search_course(course_code: str) -> dict:
    """Look up a university course by its code (e.g. 'FESE307').

    Returns the course name, credit value, and prerequisite.
    """
    code = normalize_code(course_code)
    course = COURSES.get(code)
    if course is None:
        # Deterministic, friendly error the agent can explain to the user.
        return {
            "error": f"Course '{course_code}' was not found.",
            "available_courses": sorted(COURSES.keys()),
        }
    return {
        "course_code": code,
        "name": course["name"],
        "credits": course["credits"],
        "prerequisite": course["prerequisite"],
    }


# ------------------------------------------------------------------
# TOOL: search_policy
# ------------------------------------------------------------------
@mcp.tool()
def search_policy(topic: str) -> dict:
    """Look up a university policy by topic.

    Supported topics include: attendance, late_submission, academic_integrity
    (natural wording like 'late' or 'plagiarism' also works).
    """
    key = resolve_topic(topic)
    if key is None:
        return {
            "error": f"No policy found for topic '{topic}'.",
            "available_topics": sorted(POLICIES.keys()),
        }
    return {"topic": key, "policy": POLICIES[key]}


# ------------------------------------------------------------------
# TOOL: get_schedule   <-- LAB PART 2 (TODO 1)
# ------------------------------------------------------------------
@mcp.tool()
def get_schedule(course_code: str) -> dict:
    """Return the class schedule (day, time, room) for a course code.

    Expected input:
        course_code: str   e.g. "ICT304"

    Expected output (on success), a dict shaped like:
        {
            "course_code": "ICT304",
            "day": "Wednesday",
            "time": "10:00-12:00",
            "room": "Lab B-106"
        }
    On an unknown code, return a dict with an "error" key, similar to
    search_course above.
    """
    # ==============================================================
    # TODO 1  (Lab Part 2 — ~10 minutes)
    # Implement this tool using the SCHEDULES dictionary imported above.
    #
    # Steps:
    #   1. Normalize the incoming course_code with normalize_code(...).
    #   2. Look it up in SCHEDULES.
    #   3. If not found, return {"error": "...", "available_courses": [...]}.
    #   4. If found, return the success dict shown in the docstring.
    #
    # Tip: look at how search_course() above does the same pattern.
    # ==============================================================
    return {
        "error": "get_schedule is not implemented yet.",
        "hint": "Complete TODO 1 in servers/academic_server.py (Lab Part 2).",
    }


# ------------------------------------------------------------------
# CHALLENGE 1 (TODO 2): add a new tool -> check_prerequisite
# ------------------------------------------------------------------
# The function body is written for you. Your job (Challenge 1) is to turn it
# into a real MCP tool so the agent can discover and call it.
#
#   TODO 2:
#     1. Add the  @mcp.tool()  decorator directly above the function below
#        (look at search_course / get_schedule for the exact pattern).
#     2. Restart the academic server and confirm the agent can now answer
#        "Can I take ICT304?".
#
# Until you add the decorator, this is just a plain Python function and the
# MCP server will NOT expose it as a tool.
def check_prerequisite(course_code: str) -> dict:
    """Return the prerequisite for a course code (may be None)."""
    code = normalize_code(course_code)
    course = COURSES.get(code)
    if course is None:
        return {
            "error": f"Course '{course_code}' was not found.",
            "available_courses": sorted(COURSES.keys()),
        }
    return {"course_code": code, "prerequisite": course["prerequisite"]}


if __name__ == "__main__":
    # Serve MCP over streamable HTTP so a separate MCP client process can connect.
    print("[academic-mcp] serving on http://127.0.0.1:8001/mcp  (Ctrl+C to stop)")
    mcp.run(transport="streamable-http")
