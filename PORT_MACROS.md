# PG Macro Port Plan

Scaffolding commands:

    mkdir -p packages/pg_macros/pg_macros/runtime packages/pg_macros/tests/golden
    cat <<"EOF" > packages/pg_macros/pyproject.toml
    [build-system]
    requires = ["setuptools>=61.0", "wheel"]
    build-backend = "setuptools.build_meta"
    EOF

## 1) Executive Summary
- Deliver Python parity for top 10 PG macros without regressing PG problem behavior.
- Align runtime abstractions (context, MathObjects, answers, rendering, RNG, graphing) with Perl semantics.
- Success metrics: 100 percent parity matrix completion, contract suite green on >=100 OPL samples, mutation score >=80 percent.

## 2) Inventory & Parity Matrix
### PGstandard.pl
| Symbol/Function | Arity | Options | Deps | Status | Notes keyword |
|---|---|---|---|---|---|
| TEXT | variadic | none | PGcore | partial | concat |
| ANS | variadic | evaluators | pg_answer | partial | queue |
| NAMED_ANS | 2 | label,evaluator | pg_answer | missing | binding |
| ans_rule | 0-1 | width | HTML | partial | input |
| random | 2-3 | step | rng | partial | seed |

### PGcourse.pl
| Symbol/Function | Arity | Options | Deps | Status | Notes keyword |
|---|---|---|---|---|---|
| _PGcourse_init | 0 | none | PGcore | missing | hook |
| loadMacros | variadic | course list | PGstandard | missing | bootstrap |

### MathObjects.pl
| Symbol/Function | Arity | Options | Deps | Status | Notes keyword |
|---|---|---|---|---|---|
| Compute | 1 | context | pg_math | stub | parser |
| Real | 1 | context | pg_mathobjects | stub | scalar |
| Formula | 1 | vars | pg_mathobjects | stub | expression |
| Context | 1 | name | pg_math | stub | switch |

### PGchoicemacros.pl
| Symbol/Function | Arity | Options | Deps | Status | Notes keyword |
|---|---|---|---|---|---|
| new_multiple_choice | 0 | seed | pg_answer | partial | radio |
| new_true_false | 0 | seed | pg_answer | partial | boolean |
| new_match_list | 0 | seed | random | missing | match |
| new_select_list | 0 | seed | random | missing | subset |
| new_pop_up_select_list | 0 | seed | parserPopUp | missing | popup |

### PGML.pl
| Symbol/Function | Arity | Options | Deps | Status | Notes keyword |
|---|---|---|---|---|---|
| PGML | 1 | context | pg_pgml | partial | render |
| BEGIN_PGML | 0 | none | preprocessor | stub | directive |
| END_PGML | 0 | none | preprocessor | stub | directive |

### PGgraphmacros.pl
| Symbol/Function | Arity | Options | Deps | Status | Notes keyword |
|---|---|---|---|---|---|
| init_graph | 4 | size,ticks,grid | WWPlot | missing | canvas |
| add_functions | variadic | color,style | Fun | missing | plot |
| add_label | 3 | align | Label | missing | annotate |

### AnswerFormatHelp.pl
| Symbol/Function | Arity | Options | Deps | Status | Notes keyword |
|---|---|---|---|---|---|
| AnswerFormatHelp | 2 | format | templates | missing | tooltip |
| helpLink | 1 | format | HTML | missing | link |
| addAnswerFormat | 2 | alias | registry | missing | catalog |

### parserPopUp.pl
| Symbol/Function | Arity | Options | Deps | Status | Notes keyword |
|---|---|---|---|---|---|
| PopUp::__init__ | 1-2 | correct | pg_answer | stub | ctor |
| PopUp::menu | 0 | none | HTML | stub | select |
| PopUp::cmp | 0 | none | StringEvaluator | stub | checker |

### parserMultiAnswer.pl
| Symbol/Function | Arity | Options | Deps | Status | Notes keyword |
|---|---|---|---|---|---|
| MultiAnswer | variadic | grader | pg_answer | missing | group |
| NAMED_MULTI_ANS | 2 | weights | PGstandard | missing | binding |
| multi_answer_cmp | variadic | partial | AnswerEvaluator | missing | scoring |

### contextFraction.pl
| Symbol/Function | Arity | Options | Deps | Status | Notes keyword |
|---|---|---|---|---|---|
| contextFraction | 0 | limits | Context | stub | fraction |
| contextLimitedFraction | 0 | proper flag | Context | missing | strict |
| DisableDecimals | 0 | none | Context flags | missing | clamp |

## Cross-Macro Shared Dependencies
| Component | Used By | Notes |
|---|---|---|
| Context system | MathObjects, contextFraction, parserMultiAnswer | PG flags |
| MathObjects runtime | PGstandard, MathObjects, contextFraction | Value classes |
| Answer evaluators | PGstandard, PGchoicemacros, parser* | grading |
| PG environment | PGstandard, PGcourse, PGML | lifecycle |
| PGML renderer | PGML, AnswerFormatHelp | markup |
| Graph APIs | PGgraphmacros | plotting |
| RNG | PGstandard, PGchoicemacros | seeding |

## 3) Environment & Shims
- Context: reuse pg_math.context.Context; add shim pg_macros.runtime.context exposing Perl names, fraction flags, Context(), setContext().
- MathObjects/Value: reuse pg_mathobjects; implement adapters in pg_macros.runtime.value for constructors, coercion, stringification.
- Answer evaluators: reuse pg_answer; provide pg_macros.runtime.answers for answer queue management, partial credit hooks, hints, error text parity.
- Rendering: reuse pg_pgml and pg_renderer; add pg_macros.runtime.render enforcing safe markup, tex normalization, BEGIN_PGML bridging.
- RNG: use random.Random seeded via PGEnvironment.problem_seed; expose helper pg_macros.runtime.rng.get_rng() for deterministic draws and srand alias.
- Graph layer: build pg_macros.runtime.graph wrapping WWPlot-compatible API (function sampling, grid, labels, image cache) and bridging to pg_renderer.graphs.

## 4) Architecture & File/Module Layout
- Core layout under packages/pg_macros/pg_macros:
  - Public API: __init__.py, registry.py.
  - Macros: pg_standard.py, pg_course.py, math_objects.py, pg_choice.py, pgml.py, pg_graph.py, answer_format_help.py, parser_popup.py, parser_multi_answer.py, context_fraction.py.
  - Runtime: runtime/__init__.py, context.py, value.py, answers.py, render.py, rng.py, graph.py.
- Mapping table:
| Perl file | Python module |
|---|---|
| PGstandard.pl | pg_macros.pg_standard |
| PGcourse.pl | pg_macros.pg_course |
| MathObjects.pl | pg_macros.math_objects |
| PGchoicemacros.pl | pg_macros.pg_choice |
| PGML.pl | pg_macros.pgml |
| PGgraphmacros.pl | pg_macros.pg_graph |
| AnswerFormatHelp.pl | pg_macros.answer_format_help |
| parserPopUp.pl | pg_macros.parser_popup |
| parserMultiAnswer.pl | pg_macros.parser_multi_answer |
| contextFraction.pl | pg_macros.context_fraction |

## 5) API Design Rules & Compatibility
- Expose Perl names through registry; provide snake_case aliases internally but avoid breaking loadMacros() contracts.
- Use mutable classes mirroring Perl object state; leverage dataclass only for passive records (PopUp).
- Raise PGMacroError with message templates copied from Perl; map Perl warnings to Python logging where needed.
- Simulate Perl references by returning callable wrappers or context-bound objects; emulate blessed hashes with dict-backed classes exposing attribute access and to_hash() helpers.

## 6) Test Strategy (Contract & Coverage)
- Contract corpus: select >=100 problems across algebra, calculus, trig, stats, graphing from webwork_ps1_pg; run Perl and Python macro stacks, store fixtures under packages/pg_macros/tests/golden.
- Unit tests per macro covering nominal behavior, edge flags, error text, alias exports; focus on seeded randomness, context toggles, HTML output.
- Integration tests using PG translator to render PGML, multi-answer flows, pop-up state, fraction contexts, and graph snapshots hashed for parity.
- Execute pytest packages/pg_macros/tests -q --cov --cov-branch; mark contract suite with @pytest.mark.contract for nightly runs.

## 7) Golden Outputs & Verification
- Run Perl macros via perl -MWeBWorK::PG -e harness, capture outputs as JSON with normalized HTML/TeX, numeric outputs rounded to 1e-8, and deterministic RNG seeds.
- Use HTML sanitizer to canonicalize tags/attributes, TeX normalizer for whitespace, compare strings; allow float tolerance +/-1e-10.
- Graph parity via deterministic sampling, hash PNG/SVG bytes, allow perceptual hash diff <=5.
- Mutation testing with mutmut on macro modules, baseline mutation score >=80 percent, survivors documented.

## 8) Migration Phases & Milestones
| Phase | Outputs | Entry Criteria | Exit Criteria |
|---|---|---|---|
| 0 | Spec sheets, symbol CSV, option docs | Repo audit ready | API inventory approved |
| 1 | Runtime shims, PGEnvironment parity tests | Phase 0 exit | Runtime pytest green |
| 2 | Macro ports PGstandard->contextFraction | Phase 1 exit | Macro unit tests green |
| 3 | PGML/graph parity, renderer hooks | Phase 2 exit | PGML+graph contract pass |
| 4 | Contract tests, perf report, mutation run | Phase 3 exit | Coverage >=95 percent, perf ok |
| 5 | Docs, examples, CHANGELOG, version tag | Phase 4 exit | API freeze vote complete |

## 9) Tooling & CI
- pyproject updates: add mypy strict config, coverage settings, optional deps for tests.
- Lint/format: ruff check packages/pg_macros (rules E,F,I,PG), black packages/pg_macros (line length 88), mypy packages/pg_macros --strict.
- Tests: pytest -q --cov --cov-branch, pytest -m contract nightly, mutmut run --paths packages/pg_macros/pg_macros weekly.
- CI matrix:
| Dimension | Values |
|---|---|
| Python | 3.11, 3.12 |
| OS | ubuntu-latest, windows-latest |
| Caching | pip cache keyed by pyproject.toml hash; pytest cache |
| Artifacts | coverage XML, HTML report, built wheel, golden diff logs |
- Deterministic seeds: set PG_SEED=12345 in CI env; ensure graph renderer uses seed plus graph signature to name files; snapshot graphs into artifacts.

## 10) Risks & Mitigations
| Risk | Impact | Detection | Mitigation |
|---|---|---|---|
| Hidden Perl globals | State divergence | Contract tests | Shim exposes globals map |
| Context flag variance | Wrong grading | Context unit tests | Centralize flag defaults |
| MathObjects semantics | Incorrect answers | Golden outputs | Pair with pg_mathobjects maintainer |
| PGML edge cases | Rendering diff | PGML diff tests | Extend parser fixtures |
| Graph rendering diffs | Student confusion | Snapshot hash | Implement deterministic sampler |

## 11) Acceptance Criteria & Demo Plan
- Parity matrix marks complete for all in-scope symbols.
- Contract corpus renders and grades identically (HTML, TeX, answers, hints).
- Demo: run 3 canonical problems per macro (30 total) via CLI; show identical outputs, PGML previews, graph assets with matching hashes.

## 12) Work Items (Issue Backlog)
| Epic | Story | Task | Estimate | Depends |
|---|---|---|---|---|
| Runtime parity | Spec extraction | Auto-symbol scraper | 3d | none |
| Runtime parity | Context bridge | Implement context shim | 5d | Auto-symbol scraper |
| Runtime parity | Answer infra | Queue + NAMED_ANS parity | 5d | Context shim |
| Macro ports | PGstandard | Port aggregator + tests | 6d | Answer infra |
| Macro ports | MathObjects | Adapter + tests | 5d | Context shim |
| Macro ports | Choice macros | Port Match/Select | 7d | PGstandard |
| Macro ports | Parser suite | Port parserMultiAnswer | 6d | Answer infra |
| Rendering | PGML | Renderer parity suite | 6d | PGstandard |
| Rendering | Graph | Implement graph shim | 7d | Runtime RNG |
| Contract tests | Golden harness | Perl capture tooling | 4d | Macro ports |
| QA | Mutation testing | Configure mutmut CI | 2d | Contract harness |
| Docs | GUIDE | Write PORTING.md updates | 2d | All ports |

## 13) Appendices
- Glossary:
  - PG: Problem Generation language used by WeBWorK.
  - Macro: Reusable Perl/Python routine loaded via loadMacros().
  - MathObjects: Typed numeric system providing structured values.
  - Context: Configuration bundle controlling parsing/formatting rules.
- Test fixtures: packages/pg_macros/tests/golden/*.json, packages/pg_macros/tests/data/graphs/*.png.
- Licensing: Confirm original Perl macros under Open Problem Library license; document in packages/pg_macros/NOTICE; ensure new Python code MIT per repo policy.
