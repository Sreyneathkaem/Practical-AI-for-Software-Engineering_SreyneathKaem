# Week 4 — Production Integration

This is the first week your capstone becomes real code. Weeks 1-3 built API
fluency and a plan; Week 4 is where that plan turns into a working feature,
integrated into a backend rather than living in a CLI script.

## Contents

```
lab-2-spec-driven-development/   Lab 2 — built (SDD spec-writing + AI-agent execution)
slides/                          Session 1 & 2 decks — not yet built
```

## Sessions

- **Session 1 — Backend integration, context handling:** not yet built. Planned per `.context/course-reference.md`: how an AI feature sits behind a real backend, and how application context gets assembled and handed to the model.
- **Session 2 — Security & secrets, graceful fallbacks:** not yet built. Planned: secrets management beyond `.env`, and designing what happens when the AI call fails or returns something unusable.
- **Lab 2 — Spec-Driven Development on Your Capstone:** built. Individually, you pick one feature of your team's capstone, write an executable specification for it (Outcomes, Boundaries, Constraints, Prior Decisions, Task Breakdown, Verification Criteria), hand it to an AI coding agent, and verify what comes back against your own spec. See `lab-2-spec-driven-development/README.md`.

## Why the lab exists before the lectures

Lab 2 was built first because it answers a concrete request: give students a
structured way to explore Spec-Driven Development on their own capstone
before they're deep into backend/security content. It stands on its own
(it assumes Weeks 1-3, not the not-yet-built Session 1/2 lecture content),
so it doesn't block on the lectures being written. When Sessions 1 and 2
are developed, revisit this README to connect their content explicitly to
the SDD workflow (e.g., where a Constraint in the spec maps to a security
requirement from Session 2).

## Learning goals (Lab 2)

- Understand why a specification written for an AI agent differs from a PRD or design document written for humans.
- Write all six elements of an executable AI specification.
- Apply the spec-overhead decision matrix honestly, not performatively.
- Experience how an AI coding agent behaves against a spec, including where it drifts, and how verification catches that.

Start with `lab-2-spec-driven-development/README.md`.
