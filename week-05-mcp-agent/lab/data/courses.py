"""
Static course catalogue for the AI Student Assistant lab.

This is deliberately small, local, in-memory data. There is no database on
purpose: the lab is about *architecture* (agents, tools, MCP), not data storage.

Each course record has:
    name          -> human-readable course title
    credits       -> integer credit value
    prerequisite  -> a course code, a course name, or None
"""

COURSES = {
    "FESE307": {
        "name": "Practical AI for Software Engineering",
        "credits": 3,
        "prerequisite": "Introduction to Artificial Intelligence",
    },
    "ICT303": {
        "name": "Mobile App Cross Platform Development I",
        "credits": 3,
        "prerequisite": None,
    },
    "ICT304": {
        "name": "Mobile App Cross Platform Development II",
        "credits": 3,
        "prerequisite": "ICT303",
    },
    "ICT305": {
        "name": "Software Architecture and Design Patterns",
        "credits": 3,
        "prerequisite": "ICT304",
    },
    "FESE201": {
        "name": "Data Structures and Algorithms",
        "credits": 4,
        "prerequisite": None,
    },
}


def normalize_code(course_code: str) -> str:
    """Normalize a course code the way a student might type it (case/space)."""
    return (course_code or "").strip().upper().replace(" ", "")
