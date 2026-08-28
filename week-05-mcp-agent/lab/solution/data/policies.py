"""
A few simple university policies for the AI Student Assistant lab.

Keyed by a short topic. `ALIASES` lets students ask in natural language
("late", "cheating", "attendance") and still reach the right policy.
"""

POLICIES = {
    "attendance": (
        "Students must attend at least 80% of scheduled sessions. Three or more "
        "unexcused absences may result in a grade penalty."
    ),
    "late_submission": (
        "Late assignments lose 10% per day and are not accepted more than "
        "3 days after the deadline without prior approval."
    ),
    "academic_integrity": (
        "All submitted work must be your own. Plagiarism or unauthorized "
        "collaboration may result in a zero for the assessment and referral "
        "to the academic committee."
    ),
}

# Map natural-language words to a policy key.
ALIASES = {
    "attendance": "attendance",
    "absent": "attendance",
    "absence": "attendance",
    "late": "late_submission",
    "late submission": "late_submission",
    "deadline": "late_submission",
    "submission": "late_submission",
    "integrity": "academic_integrity",
    "plagiarism": "academic_integrity",
    "cheating": "academic_integrity",
    "academic integrity": "academic_integrity",
}


def resolve_topic(topic: str):
    """Return a canonical policy key for a free-text topic, or None."""
    t = (topic or "").strip().lower()
    if t in POLICIES:
        return t
    if t in ALIASES:
        return ALIASES[t]
    # loose contains-match so "what is the late policy" still resolves
    for word, key in ALIASES.items():
        if word in t:
            return key
    return None
