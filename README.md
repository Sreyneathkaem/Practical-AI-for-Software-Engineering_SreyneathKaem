# Practical AI for Software Engineering

Course materials for **FESE307 Practical AI for Software Engineering** — a
hands-on, capstone-integrated course that teaches software engineers how to
build real applications powered by large language models (LLMs). Rather than
the maths of machine learning, the focus is the engineer's view: integrating
AI through APIs, prompting reliably, engineering for production concerns
(security, evaluation, scaling, deployment), and applying it all to a
capstone project you plan in Week 3 and build for the rest of the course.

- **Level:** Year 3, Undergraduate — Faculty of Engineering, CamTech
- **Duration:** 10 weeks · 2 sessions per week · about 4.5 hours/week (45 learning hours)
- **Prerequisites:** Programming fundamentals & Python; basic APIs and Git. No prior AI/ML experience required.
- **Full syllabus:** `syllabus/FESE307 Course Syllabus (Practical AI for Software Engineering).docx`

## Repository structure

```
.
├── syllabus/                                # full course syllabus
├── week-01-foundations-of-applied-ai/
│   ├── slides/                              # lecture deck
│   └── session-1-lab/                       # hands-on coding lab (AskBot)
├── week-02-working-with-the-openai-api/
│   ├── slides/                              # lecture decks (Session 1 & 2)
│   └── session-2-lab/                       # lab (Configurable Text Assistant)
├── week-03-designing-ai-enabled-software-capstone-kickoff/
│   ├── slides/                              # Session 1 & 2 decks
│   ├── lab-3-capstone-discovery-planning/   # capstone kickoff workshop + Concept v1 deliverable
│   └── archive/                             # retired Prompt Engineering material
└── README.md
```

More weeks will be added here as the course progresses. `.context/` holds the
live build tracker and authoring conventions for anyone (human or AI) adding
new material.

## What's covered

Themes and deliverables follow the official FESE307 syllabus (see
`.context/course-reference.md` for the full map):

| Week | Theme | Lab / Milestone |
|------|-------|------------------|
| 1 | Foundations of Applied AI | Lab 0 — environment setup & first API call |
| 2 | Working with the OpenAI API | Lab 1 — configurable text assistant |
| 3 | Designing AI-Enabled Software & Capstone Kick-off | Lab 3 — Capstone Discovery & Planning → Capstone Concept v1 |
| 4 | Production Integration | Lab 2 — first capstone AI feature |
| 5 | Evaluation & Testing | Milestone — test plan & evaluation harness |
| 6 | Scaling & Performance | Lab 3 — scale/optimize, monitoring & fallback |
| 7 | Design Patterns (multi-agent, workflows, event-driven, MCP) | Milestone — architecture design |
| 8 | Deployment & Ops | Lab 4 — deploy a beta, user test, gather metrics |
| 9 | Systems Review | Milestone — demo dry-run & tech-debt triage |
| 10 | Capstone Showcase | Capstone showcase & technical presentation |

## Getting started

Clone the repo and open the syllabus for the full schedule and assessment
breakdown. Each week's folder contains the slides and any labs. Lab setup
instructions live in each lab's own `README.md`.

```bash
git clone <your-repo-url>
cd "Practical AI for Software Engineering"
```

## For students

Work through the labs in order — each builds on the last. Never commit your API
keys: labs use a `.env` file that is already git-ignored.

---

*CamTech · Department of Software Engineering*
