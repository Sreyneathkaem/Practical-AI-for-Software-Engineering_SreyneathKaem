# Lab 2: Spec-Driven Development on Your Capstone

Practical AI for Software Engineering · Week 4 · Individual deliverable

## Overview

Up to now you have written code yourself and used an LLM as an API you call
from inside it. This lab flips that relationship for one feature: you write
a specification, and an AI coding agent writes the code.

That only works if the spec is good enough for an agent to build against
without you standing over its shoulder. This lab is where you practice
that discipline, called Spec-Driven Development (SDD): you write an
executable specification for one feature of your own capstone, hand it to
an AI coding agent, and verify what comes back against the contract you
wrote, not against your gut feeling about whether it looks right.

This is Lab 2, your first real capstone feature. Everyone on your team
builds toward the same capstone, but this deliverable is individual: you
each pick your own slice and write your own spec, so the discipline is
yours, not just something your team lead did.

**Headline lesson:** a specification written for an AI agent has to resolve
ambiguity itself, in writing, before the agent starts. A spec that still
needs a conversation to interpret isn't done yet.

## Learning goals

- Understand why a specification written for an AI agent differs from a PRD or a design document written for humans.
- Write all six elements of an executable AI specification: Outcomes, Boundaries, Constraints, Prior Decisions, Task Breakdown, Verification Criteria.
- Apply the spec-overhead decision matrix to judge, honestly, when writing a full spec is actually worth it.
- Experience firsthand how an AI coding agent behaves against a spec, including where it drifts, and how verification catches that.

## Your project, not a fixed scenario

There is no shared case study this time. Your "scenario" is your own
team's capstone, as defined in your Week 3 Capstone Concept v1.

Before this lab starts:

1. As a team, look at your Capstone Concept v1's core functional requirements and pick 2 to 4 small, independent features, one per team member. "Independent" matters: if two people spec the same piece of logic, you can't tell whose spec actually drove the outcome.
2. Each teammate claims one feature. A good feature for this lab is small enough to implement in the lab session, but real enough that a bad spec would actually cause a bad outcome. Examples: one API endpoint, one data-validation rule, one retrieval step, one UI interaction. Not "the whole chatbot."
3. Confirm with your team which AI coding agent you'll use (Claude Code, GitHub Copilot Workspace, Cursor, or similar). Use whatever your team has already set up for the capstone; this lab is about the spec, not about learning a new tool.

## Tasks

**Task 1 — Select your feature.** Write down, in one sentence, which feature you're specifying and why it's yours to specify (not overlapping a teammate's).

**Task 2 — Write the six-element specification.** For your feature, write:
- **Outcomes:** the precise end state, in the form "X persists/returns/blocks Y," not "build the X feature."
- **Boundaries:** what this feature explicitly does *not* do. Be specific; an agent will expand scope on its own if you leave a door open.
- **Constraints:** the technology stack limits, API/rate limits, and performance rules that apply. If your team already has an `AGENTS.md` or equivalent context file, reference it instead of repeating it.
- **Prior Decisions:** anything already decided elsewhere in your capstone that this feature must respect (a chosen schema, a library, an existing pattern), documented before you delegate, not discovered after.
- **Task Breakdown:** the feature broken into discrete sub-tasks small enough for an agent to execute without flooding its own context.
- **Verification Criteria:** the exact, checkable rules you (not the agent) will use to decide whether the output is acceptable.

**Task 3 — Run the decision matrix on yourself.** Using the skip-the-spec vs. write-the-spec criteria from Session 1, state honestly whether this feature actually warranted a full spec. If you conclude it didn't, say so and explain why you're writing one anyway (this is a graded exercise; that's a legitimate reason, but say it).

**Task 4 — Execute.** Hand your spec to your AI coding agent and have it implement the feature, in full or as far as the lab time allows. Keep a short log of what you gave it and what it produced.

**Task 5 — Verify.** Check the agent's output against every one of your Verification Criteria, one at a time, pass or fail. Separately, note any place the agent tried to cross a Boundary or violate a Constraint, even if you caught it before it landed.

**Task 6 — Reflect.** In a few sentences: did the agent stay inside your spec? Where did it drift, if anywhere? What would you tighten in the spec next time, specifically?

## Deliverable

Submit your report as a single PDF, with each section clearly labeled
(ideally starting on a new page):

1. **Feature & Outcomes** (0.5 page max): which feature, and the precise Outcomes statement.
2. **The Specification** (1.5 page max): all six elements, in full.
3. **Execution Log** (0.5 page max): what you gave the agent and what it returned. A link to the actual diff or commit is welcome in addition to the description.
4. **Verification Results** (1 page max): each Verification Criterion, checked pass or fail against the real output, plus any Boundary/Constraint violations you caught.
5. **Reflection** (0.5 page max): the decision-matrix judgment from Task 3, and what you'd change about the spec next time.

Page limits are a guide, not a hard cap. If a section genuinely needs more room, take it. Precise and concise beats long and padded either way.

`SDD_Spec_Report_Template.docx` in this folder gives you a starting structure for all five sections.

## Grading

This lab is worth 100 points, graded individually. For full credit:

- [ ] 10 points: the chosen feature and its Outcomes statement are specific and non-overlapping with a teammate's.
- [ ] 10 points: Boundaries are explicit and would actually stop an agent from expanding scope.
- [ ] 10 points: Constraints are precise enough that violating one would be unambiguous.
- [ ] 10 points: Prior Decisions are documented, not assumed or discovered mid-task.
- [ ] 10 points: Task Breakdown is genuinely discrete, not one undivided block of work.
- [ ] 15 points: Verification Criteria are exact and checkable, the way an automated Verifier agent could apply them, not vague ("works well").
- [ ] 10 points: an execution log shows the spec was actually run through an AI coding agent, not written and then never used.
- [ ] 15 points: every Verification Criterion is explicitly checked against the real output, with a stated pass/fail and evidence, including any Boundary or Constraint violations.
- [ ] 10 points: the reflection meaningfully engages with the decision-matrix judgment and names a specific change to make next time, not a generic "it went well."

## Troubleshooting

| Symptom | Likely fix |
| --- | --- |
| The agent produced something reasonable-looking that still fails a Verification Criterion | This is expected and worth reporting exactly as it happened; "looks right" and "passes verification" are different claims, and the gap is the point of this lab |
| Two teammates picked overlapping features | Re-split before you start Task 2; overlapping specs make it impossible to tell whose spec drove the outcome |
| The agent didn't finish the feature in the lab time | Report what it completed and verify only that; note the incomplete parts in your Execution Log rather than padding the spec to look finished |
| You genuinely can't tell if a Verification Criterion passed | The criterion wasn't precise enough; rewrite it now and note the rewrite in your Reflection, that's a real finding |

---
*Course: Practical AI for Software Engineering · Week 4, Lab 2*
