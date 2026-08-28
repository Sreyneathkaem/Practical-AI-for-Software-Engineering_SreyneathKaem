# Practical AI for Software Engineering

Course materials for **Practical AI for Software Engineering** — a hands-on,
project-driven course that teaches software engineers how to build real
applications powered by large language models (LLMs). Rather than the maths of
machine learning, the focus is the engineer's view: integrating AI through APIs
and open-source libraries, designing reliable prompts, grounding models in your
own data, and deploying AI systems in production.

- **Level:** Year 3, Undergraduate — Software Engineering
- **Duration:** 10 weeks · 2 sessions per week
- **Prerequisites:** Programming fundamentals & Python; basic APIs and Git. No prior AI/ML experience required.
- **Aligned with:** DataCamp's *Associate AI Engineer for Developers* track.

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
└── README.md
```

More weeks will be added here as the course progresses.

## What's covered

| Weeks | Theme |
|-------|-------|
| 1 | Foundations of Applied AI — the AI engineer role, the LLM stack, first API call |
| 2 | Working with the OpenAI API |
| 3 | Prompt engineering |
| 4 | Building interactive AI apps (function calling) |
| 5 | Open-source models with Hugging Face |
| 6 | Embeddings & semantic search |
| 7 | Vector databases & RAG |
| 8 | Orchestration with LangChain |
| 9 | Production AI — LLMOps, software engineering, MCP |
| 10 | Capstone |

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
