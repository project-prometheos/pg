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

- [x] Build a checklist of all transforms currently handled by `_rewrite_statement`/`_rewrite_with_pygments`.
- [x] Mark each as “grammar‑friendly” vs “token‑fallback”.

Initial inventory (with current status):

- [x] Control flow: `if`/`elsif`/`else`, `unless`, `while` (in grammar)
- [x] Loop forms: `for my $i (...)`, `foreach my $i (...)` (in grammar)
- [x] Statement modifiers: `stmt if/unless cond` (in grammar)
- [x] `do { ... } until (cond)` loops (in grammar + collector)
- [x] Ranges: `START .. END` (in grammar)
- [x] Ternary `cond ? a : b` (in grammar)
- [x] Method chaining: `$obj->method(args)` (+ basic auto‑parens rules) (grammar + token post‑proc)
- [x] Hash/array subscripting: `$h{key}`, `$a[idx]` (in grammar)
- [x] Hash/array literals: `{ key => value }`, `[ a, b ]` (in grammar)
- [x] Map/grep blocks: `map { expr } list`, `grep { expr } list` (in grammar)
- [x] Regex literals: `qr/pattern/flags` (grammar + fixed flags token)
- [x] String ops: concatenation `.`, repetition `x` (in grammar)
- [x] String comparisons: `eq`, `ne`, `lt`, `gt`, `le`, `ge` (in grammar)
- [~] Sigils: `$`, `@`, `%` (removed via token layer; acceptable fallback)
- [~] Special shims: AnswerHints tuple wrapping, `Context().functions.add(name => {…})`, quoted‑string `= value` pairs (kept in token layer by design)
- [~] Perl specials: `$#array` → `len(array)-1`, `~~&func` → `func` (token layer)

### 2) Grammar Roadmap

- [x] Extend `_grammar` to cover grammar‑friendly items listed above.
- [x] Define/extend transformer rules to lower into IR (`("if", ...)`, `("for", ...)`, `("map", ...)`, etc.).
- [x] Note parser strategy (Earley) and avoid zero‑width tokens (fixed regex flags with `REGEX_FLAGS?`).

### 3) Incremental Ports (repeat per feature)

For each chosen slice:

- [ ] Add/extend grammar productions.
- [ ] Implement transformer lowering to IR.
- [ ] Update `_emit_ir` / `_expr_to_py` to support the IR.
- [ ] Add targeted tests (unit + golden snippets) for pygments preprocessor.
- [ ] Remove matching case from `_rewrite_statement` / `_rewrite_with_pygments`.
- [ ] Run full preprocessor + translator suites; fix regressions.

Suggested order of migration (current status):

1. [x] Control flow headers (`if`/`elsif`/`else`/`unless`/`while`)
2. [x] Loops (`for`/`foreach`, ranges)
3. [x] Statement modifiers (`stmt if/unless cond`)
4. [x] Ternary operator
5. [x] Map/grep blocks
6. [x] Method chaining + auto‑parens (partial: auto‑parens post‑proc retained)
7. [x] Regex literals w/ flags
8. [~] AnswerHints/Context `.add` shims (intentionally kept in token layer)

### 4) Fallback Cleanup

- [x] After each feature ports to grammar, prune redundant logic from `_rewrite_statement` and keep Pygments layer focused on:
  - Sigil removal in residual contexts
  - Simple token joins (`->`, `::`, `=>`)
  - String interpolation/conversion
  - Niche shims that don’t fit grammar cleanly

### 5) Validation & Rollout

- [x] Ensure `packages/pg_translator/tests/test_preprocessor_pygments.py` (structured) remains green.
- [ ] Ensure `packages/pg_translator/tests/test_preprocessor.py` (legacy) remains green under new defaults (translator now imports structured preprocessor).
- [ ] Run broader translator/integration suites (OPL/realworld if available).
- [x] Document default switch; keep `LegacyPGPreprocessor` available via package exports.

## Testing Strategy

- Unit: Author minimal PG snippets per feature; assert emitted Python matches expectations.
- Golden: Keep a small corpus of representative PG files to catch regressions.
- Performance: Measure preprocessing latency after major grammar expansions.

## Risks & Mitigations

- Grammar ambiguity/complexity → Start small, prefer explicit productions, keep fallback.
- Hidden PG idioms → Expand test corpus iteratively; lean on real PG files.
- Output drift → Compare against legacy output for known snippets until parity proven.

## Status Tracking

- [x] Inventory complete
- [x] Roadmap approved
- [x] First migrations (control flow, loops, modifiers, ternary, map/grep) merged
- [x] Fallback cleanup phase started
- [x] Pygments preprocessor suite green
- [ ] Full translator/OPL suite green
- [x] Default import switches completed (convert, solve)
