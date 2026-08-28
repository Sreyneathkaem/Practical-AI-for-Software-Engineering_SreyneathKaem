"""
config.py — defaults and personas for the Configurable Text Assistant.

Keeping behaviour here (as data) instead of hard-coding strings throughout
the program is the whole point of Step 2: personas and defaults become
configuration you can change in one place.
"""

# ---- generation defaults -------------------------------------------------
DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 500

# The model name is intentionally a placeholder. Set it to whatever model
# your course environment provides (e.g. via the OPENAI_MODEL env var).
DEFAULT_MODEL = "YOUR_MODEL"

# ---- retry / backoff -----------------------------------------------------
MAX_RETRIES = 3          # Step 8: never retry more than this many times
BACKOFF_BASE = 1.0       # seconds; delay = BACKOFF_BASE * 2 ** attempt
BACKOFF_MAX = 30.0       # cap the wait so we never sleep absurdly long

# ---- personas (system prompts) ------------------------------------------
DEFAULT_PERSONA = """\
You are a helpful programming assistant.
Explain concepts clearly to a Year 3 software engineering student.
"""

PERSONAS = {
    "tutor": """\
You are a programming tutor.
Explain concepts step by step.
Do not immediately provide complete solutions.
""",
    "reviewer": """\
You are a strict code reviewer.
Identify bugs, maintainability issues, and possible improvements.
""",
    "interviewer": """\
You are a software engineering interviewer.
Ask one question at a time.
Do not reveal the answer immediately.
""",
    "default": DEFAULT_PERSONA,
}


def get_persona(name: str) -> str:
    """Return the system prompt for a named persona, falling back to default."""
    return PERSONAS.get(name, DEFAULT_PERSONA)
