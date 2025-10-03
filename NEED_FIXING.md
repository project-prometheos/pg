# Python ↔ Perl Parity Plan (NEED_FIXING)

## Goal
Achieve 1:1 behavior with the Perl PG reference (Value::* and PGML macros), focusing first on Formula->cmp(...) and adjacent answer checking paths. Keep scope surgical and incremental with tests per change.

## Principles
- Mirror Perl semantics and option names; no ad‑hoc shortcuts.
- Prefer unification over duplication (one checker path).
- Add tests alongside each change (Perl tutorial examples as truth). 

## Workstream 1 — Unify Formula Checking (Highest Priority)
- Changes:
  - Route all formula checks through `pg_answer.FormulaEvaluator` / `pg_math.Formula.cmp`.
  - Deprecate ad‑hoc parsing in `pg_renderer/checkers/formula.py` (retain only as thin wrapper if needed).
- Files: `packages/pg_renderer/pg_renderer/answer_checker.py`, `packages/pg_renderer/pg_renderer/checkers/formula.py`, `packages/pg_math/pg_math/formula.py`, `packages/pg_answer/pg_answer/evaluators/formula.py`.
- Acceptance:
  - One codepath for formula comparison; all formula tests green.

## Workstream 2 — Setup‑Side Method Chaining + cmp Parity
- Changes:
  - Extend evaluator to support `$ans = Formula('...')->cmp(...)` in setup (not only PGML).
  - Represent cmp as an evaluator spec (type, variables, options) usable by renderer and backend.
- Files: `packages/pg_renderer/pg_renderer/evaluator.py`, `packages/pg_renderer/pg_renderer/__init__.py`, `packages/pg_renderer/pg_renderer/pgml.py`.
- Acceptance:
  - A PG using setup‑side `$ans->cmp(...)` renders with correct checker/options.

## Workstream 3 — cmp(...) Options Coverage (Parity Set A)
- Options: `upToConstant` (additive), `numPoints`, `test_at`/`testAtZero`, `limits`, `checkUndefined`, fraction flags (`studentsMustReduceFractions`, `reduceFractions`, `allowMixedNumbers`).
- Changes:
  - Parse Perl‑style `key => value` into canonical context.
  - Wire to `FormulaEvaluator` and `Formula.compare()` behaviors.
- Files: `pgml.py` (option parse), `answer_checker.py` (pass-through), `pg_answer/…/formula.py`, `pg_math/…/formula.py`.
- Acceptance:
  - Tutorial: `IndefiniteIntegrals.pg`, `FractionAnswer.pg` pass targeted tests.

## Workstream 4 — Context Semantics (Minimal Parity)
- Changes:
  - Implement core Context flags/vars used by above options; share with `pg_parser` context when available.
- Files: `packages/pg_renderer/pg_renderer/context.py`, `packages/pg_parser/pg_parser/context.py`.
- Acceptance:
  - Flags influence evaluation (e.g., reduce rules, allowed functions) in tests.

## Workstream 5 — Intervals, Inequalities, Sets, Vectors
- Changes:
  - Add dedicated checkers using parsing vs. string normalization.
- Files: `packages/pg_renderer/pg_renderer/checkers/*`, `answer_checker.py`.
- Acceptance:
  - Basic parity tests for interval/set/vector, inequality canonicalization.

## Workstream 6 — PGML Robustness (Targeted)
- Changes:
  - Validate and parse a minimal, deterministic subset (tables, lists, withPostFilter hook placeholder, AnswerHints passthrough).
- Files: `pgml.py`.
- Acceptance:
  - Do not silently drop constructs; warn or handle. Unit tests for representative PGML.

## Workstream 7 — Tests, CI, and Samples
- Add tests mapped to Perl tutorial PGs:
  - Algebra: `AnswerUpToMultiple.pg`, `FractionAnswer.pg`
  - Calc: `IndefiniteIntegrals.pg`
  - DiffEq: `GeneralSolutionODE.pg` (custom checker: mark unsupported with clear error for now)
- Files: `packages/pg_renderer/tests/*`, `packages/pg_math/tests/*`.
- CI: ensure `pnpm test` runs them and remains green.

## Workstream 8 — Deprecations & Docs
- Document removed shortcuts and the new single checker path.
- Update QUICKSTART and AGENTS notes for how to add cmp options.

## Milestones & Order
1) Unify formula path (WS1)
2) Setup method chaining (WS2)
3) cmp options set A (WS3)
4) Context flags used by WS3 (WS4)
5) Interval/inequality checkers (WS5)
6) PGML improvements (WS6)
7) Tests + CI hardening (WS7)
8) Deprecations/docs (WS8)

## Validation Checklist
- [ ] All formula tests pass using unified path
- [ ] `$var->cmp(upToConstant => 1)` works from setup and PGML
- [ ] Fraction options affect results and messaging
- [ ] Intervals/inequalities parsed, not string-compared
- [ ] Context flags are honored where used
- [ ] No silent PGML feature loss; warnings or support added
- [ ] CI green on main

