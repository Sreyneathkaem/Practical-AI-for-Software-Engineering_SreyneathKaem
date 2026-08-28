"""
Math MCP Server
===================================================================
A second, separate MCP server that exposes *deterministic* math tools.

Why a whole separate server just for math?
    To make one architectural point unmissable:

        Agent  = reasoning        (decides WHICH tool, and WHY)
        Tool   = deterministic    (computes the exact answer)

    The LLM must NOT calculate a GPA in its head. Numbers must come from
    real, testable code — not from a language model's guess. This server
    is where that guarantee lives.

Run it (Terminal 2):
    python servers/math_server.py
It will serve MCP over HTTP at:  http://127.0.0.1:8002/mcp
===================================================================
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("math", host="127.0.0.1", port=8002)

# A simple, documented grade -> grade-point mapping.
GRADE_POINTS = {
    "A": 4.0,
    "B+": 3.5,
    "B": 3.0,
    "C+": 2.5,
    "C": 2.0,
    "D": 1.0,
    "F": 0.0,
}


# ------------------------------------------------------------------
# TOOL: calculate_gpa
# ------------------------------------------------------------------
@mcp.tool()
def calculate_gpa(grades: list[str]) -> dict:
    """Calculate a GPA from a list of letter grades, e.g. ["A", "B+", "B", "C"].

    Uses this fixed mapping:
        A=4.0  B+=3.5  B=3.0  C+=2.5  C=2.0  D=1.0  F=0.0
    GPA = average of the grade points (each course weighted equally).
    """
    if not grades:
        return {"error": "No grades were provided."}

    points = []
    unknown = []
    for g in grades:
        key = str(g).strip().upper()
        if key in GRADE_POINTS:
            points.append(GRADE_POINTS[key])
        else:
            unknown.append(g)

    if unknown:
        return {
            "error": f"Unknown grade(s): {unknown}.",
            "valid_grades": sorted(GRADE_POINTS.keys()),
        }

    gpa = round(sum(points) / len(points), 2)
    return {
        "grades": grades,
        "grade_points": points,
        "count": len(points),
        "gpa": gpa,
    }


# ------------------------------------------------------------------
# TOOL: calculate_average
# ------------------------------------------------------------------
@mcp.tool()
def calculate_average(values: list[float]) -> dict:
    """Calculate the arithmetic mean of a list of numbers."""
    if not values:
        return {"error": "No values were provided."}
    try:
        nums = [float(v) for v in values]
    except (TypeError, ValueError):
        return {"error": f"All values must be numbers. Got: {values}"}
    average = round(sum(nums) / len(nums), 2)
    return {"values": nums, "count": len(nums), "average": average}


if __name__ == "__main__":
    print("[math-mcp] serving on http://127.0.0.1:8002/mcp  (Ctrl+C to stop)")
    mcp.run(transport="streamable-http")
