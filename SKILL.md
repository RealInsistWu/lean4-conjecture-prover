---
name: lean4-conjecture-prover
description: Prove, disprove, or audit difficult mathematical conjectures through adaptive independent search, exact proof contracts, adversarial review, and Lean 4 verification. Use for research-level proofs, counterexamples, stalled arguments, and formalization.
---

# Lean 4 Conjecture Prover

Prefer mathematical discovery to orchestration. Do not assume the conjecture is true or confuse plausible progress with proof.

## Contract and mode

- Fix the exact statement, domains, definitions, quantifiers, hypotheses, edge cases, and acceptance criteria. Preserve these through every reformulation; prove equivalence when needed.
- Default to **isolated**: use background definitions and standard theorems only; never search for the target, its status, solutions, or equivalent-strength results. Apply the boundary to agents, tools, and library searches. Stop and log accidental exposure.
- Use **research** only when requested: relevant literature is allowed, with checked citations. Use **hybrid** only when requested: begin isolated, then switch at the agreed checkpoint or after genuine stagnation; record the switch. Never override a user restriction.

## Discover and iterate

Start with the simplest useful cases and several genuinely different mechanisms when difficulty warrants. Seek structural explanations, invariants, new constructions, dualities, sharp obstructions, and surprising connections. Explore the logical negation too. Let the mathematics select the techniques.

For substantial problems, use independent agents when available and authorized. Give them distinct mechanisms and the same contract, without anchoring them to the favored route. Scale by useful work, not quotas; obey runtime limits and never exceed 64 concurrent agents. Otherwise explore sequentially and disclose the limitation.

Test new lemmas against edge cases and counterexamples; distinguish experiments from proof. Combine checked insights. Track distinct mechanisms, proved claims, and actual gaps. A target-strength reduction without a new mechanism is blocked, not nearly solved. Reopen it only with new mathematical evidence. Redirect effort from duplicate or stalled routes. Continue while useful work and authorized resources remain.

## Verify and report

- For a serious candidate, trace the dependency graph to proved lemmas or applicable theorems; reject circularity, hidden assumptions, invalid witnesses, and unproved global steps.
- Independently attack material claims as they arise. Before acceptance, give the exact contract and raw proof to a fresh auditor without a suggested verdict, if possible; otherwise perform a separate skeptical review and disclose that independence is unavailable.
- When Lean 4 is available, check vulnerable lemmas and formalize a surviving result. Read `references/lean.md` before claiming formal verification. Freeze and review the statement; check the actual theorem and transitive axioms. Never substitute a weaker statement or rely on unchecked placeholders.
- Report **PROVED**, **DISPROVED**, **PARTIAL PROGRESS**, or **UNRESOLVED**. A disproof must establish the exact logical negation. Complete results require closed dependencies and successful audit. Label Lean status separately: `PASS`, `NOT RUN`, `FAILED`, or `STATEMENT NOT VALIDATED`. If Lean is explicitly required, do not claim the requested task is complete without a validated formal result.
- Return the proof or disproof, scope, checked dependencies, sources, and first unresolved gap as relevant. Respect requests for no partial report.

## Load only on demand

- Hard or multi-round search, agents, or resumption: `references/search.md`.
- Literature or contamination questions: `references/sources.md`.
- Lean verification: `references/lean.md`.
- Long runs: copy `assets/checkpoint.md` into a task-local workspace; update only on material changes and before handoff. Do not preload all references, read the entire ledger each round, or spend tokens on ceremonial status reports.
