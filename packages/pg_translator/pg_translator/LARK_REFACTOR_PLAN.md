# Lark Grammar Refactor Plan

This plan tracks migrating PG preprocessing logic from ad‑hoc regex/token rewriting into a structured Lark grammar + IR emitter, with Pygments retained only for token‑level fixes.

## Goals

- Prefer grammar/AST over regex for all structural PG constructs.
- Preserve functional parity with the legacy preprocessor across the full test suite and real PG corpus.
- Keep diffs incremental and test‑driven; minimize risk by porting feature slices.

## Non‑Goals

- Changing user‑visible semantics beyond what tests/corpus require.
- Rewriting sandbox/execution or grading logic.

## Workstreams & TODOs

### 1) Feature Inventory (what to migrate)

- [ ] Build a checklist of all transforms currently handled by `_rewrite_statement`/`_rewrite_with_pygments`.
- [ ] Mark each as “grammar‑friendly” vs “token‑fallback”.

Initial inventory (to classify):

- [ ] Control flow: `if`/`elsif`/`else`, `unless`, `while`
- [ ] Loop forms: `for my $i (...)`, `foreach my $i (...)`
- [ ] Statement modifiers: `stmt if/unless cond`
- [ ] `do { ... } until (cond)` loops
- [ ] Ranges: `START .. END`
- [ ] Ternary `cond ? a : b`
- [ ] Method chaining: `$obj->method(args)` (+ auto‑parens rules)
- [ ] Hash/array subscripting: `$h{key}`, `$a[idx]`
- [ ] Hash/array literals: `{ key => value }`, `[ a, b ]`
- [ ] Map/grep blocks: `map { expr } list`, `grep { expr } list`
- [ ] Regex literals: `qr/pattern/flags`
- [ ] String ops: concatenation `.`, repetition `x`
- [ ] String comparisons: `eq`, `ne`, `lt`, `gt`, `le`, `ge`
- [ ] Sigils: `$`, `@`, `%` (context‑aware removal)
- [ ] Special shims: AnswerHints tuple wrapping, `Context().functions.add(name => {…})`, quoted‑string `= value` pairs
- [ ] Perl specials: `$#array` → `len(array)-1`, `~~&func` → `func`

### 2) Grammar Roadmap

- [ ] Extend `_grammar` to cover all grammar‑friendly items.
- [ ] Define/extend transformer rules to lower into IR (`("if", ...)`, `("for", ...)`, `("map", ...)`, etc.).
- [ ] Note parser strategy (Earley w/ dynamic) and avoid zero‑width tokens.

### 3) Incremental Ports (repeat per feature)

For each chosen slice:

- [ ] Add/extend grammar productions.
- [ ] Implement transformer lowering to IR.
- [ ] Update `_emit_ir` / `_expr_to_py` to support the IR.
- [ ] Add targeted tests (unit + golden snippets) for pygments preprocessor.
- [ ] Remove matching case from `_rewrite_statement` / `_rewrite_with_pygments`.
- [ ] Run full preprocessor + translator suites; fix regressions.

Suggested order of migration:

1. [ ] Control flow headers (`if`/`elsif`/`else`/`unless`/`while`)
2. [ ] Loops (`for`/`foreach`, ranges)
3. [ ] Statement modifiers (`stmt if/unless cond`)
4. [ ] Ternary operator
5. [ ] Map/grep blocks
6. [ ] Method chaining + auto‑parens
7. [ ] Regex literals w/ flags
8. [ ] AnswerHints/Context `.add` shims (keep in token layer if grammar gets messy)

### 4) Fallback Cleanup

- [ ] After each feature ports to grammar, prune redundant logic from `_rewrite_statement` and keep Pygments layer focused on:
  - Sigil removal in residual contexts
  - Simple token joins (`->`, `::`, `=>`)
  - String interpolation/conversion
  - Niche shims that don’t fit grammar cleanly

### 5) Validation & Rollout

- [ ] Ensure `packages/pg_translator/tests/test_preprocessor.py` (legacy) and `test_preprocessor_pygments.py` (structured) remain green.
- [ ] Run broader translator/integration suites (OPL/realworld if available).
- [ ] Document migration in `CHANGELOG`/README and keep `LegacyPGPreprocessor` available.

## Testing Strategy

- Unit: Author minimal PG snippets per feature; assert emitted Python matches expectations.
- Golden: Keep a small corpus of representative PG files to catch regressions.
- Performance: Measure preprocessing latency after major grammar expansions.

## Risks & Mitigations

- Grammar ambiguity/complexity → Start small, prefer explicit productions, keep fallback.
- Hidden PG idioms → Expand test corpus iteratively; lean on real PG files.
- Output drift → Compare against legacy output for known snippets until parity proven.

## Status Tracking

- [ ] Inventory complete
- [ ] Roadmap approved
- [ ] First migration (control flow) merged
- [ ] Fallback cleanup phase started
- [ ] Full suite green
- [ ] Rollout complete

