"""
Academic MCP Server  — INSTRUCTOR SOLUTION
===================================================================
Completed version of servers/academic_server.py:
  * TODO 1  -> get_schedule implemented (Lab Part 2)
  * Challenge 1 -> check_prerequisite tool added
===================================================================
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP

from data.courses import COURSES, normalize_code
from data.schedules import SCHEDULES
from data.policies import POLICIES, resolve_topic

mcp = FastMCP("academic", host="127.0.0.1", port=8001)


@mcp.tool()
def search_course(course_code: str) -> dict:
    """Look up a university course by its code (e.g. 'FESE307')."""
    code = normalize_code(course_code)
    course = COURSES.get(code)
    if course is None:
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


@mcp.tool()
def search_policy(topic: str) -> dict:
    """Look up a university policy by topic."""
    key = resolve_topic(topic)
    if key is None:
        return {
            "error": f"No policy found for topic '{topic}'.",
            "available_topics": sorted(POLICIES.keys()),
        }
    return {"topic": key, "policy": POLICIES[key]}


@mcp.tool()
def get_schedule(course_code: str) -> dict:
    """Return the class schedule (day, time, room) for a course code."""
    # ---- TODO 1 completed ----
    code = normalize_code(course_code)
    slot = SCHEDULES.get(code)
    if slot is None:
        return {
            "error": f"No schedule found for '{course_code}'.",
            "available_courses": sorted(SCHEDULES.keys()),
        }
    return {
        "course_code": code,
        "day": slot["day"],
        "time": slot["time"],
        "room": slot["room"],
    }


@mcp.tool()
def check_prerequisite(course_code: str) -> dict:
    """Return the prerequisite for a course (Challenge 1)."""
    code = normalize_code(course_code)
    course = COURSES.get(code)
    if course is None:
        return {
            "error": f"Course '{course_code}' was not found.",
            "available_courses": sorted(COURSES.keys()),
        }
    return {
        "course_code": code,
        "prerequisite": course["prerequisite"],  # may be None
    }


if __name__ == "__main__":
    print("[academic-mcp] serving on http://127.0.0.1:8001/mcp  (Ctrl+C to stop)")
    mcp.run(transport="streamable-http")
