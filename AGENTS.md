# Repository Guidelines

## Project Structure & Module Organization
- Monorepo managed by pnpm and Nx.
- `apps/backend` — FastAPI service (Python) with SQLite/Alembic; tests in `apps/backend/tests`.
- `apps/web` — React + Vite + TypeScript; app code in `apps/web/src`.
- `packages/*` — Python libraries (e.g., `problemkit`) and PG tooling.
- `assets/`, `tutorial/` — TeX/PG reference and samples; avoid edits without discussion.
- `bin/`, `.github/`, `docker/` — local tools, CI, and containerization.

## Build, Test, and Development Commands
- Install deps: `pnpm install` (root); Python: `python -m pip install -e apps/backend[dev] -e packages/problemkit`.
- Dev (both apps): `pnpm dev` (runs backend + web via Nx).
- Backend only: `cd apps/backend && uvicorn app.main:app --reload`.
- Web only: `pnpm --dir apps/web dev`.
- Tests: `pnpm test` (Nx), or `cd apps/backend && pytest -q`; `pnpm --dir apps/web test`.
- Lint/format: `pnpm lint`; Python: `python -m ruff check apps/backend/app` and `python -m black apps/backend/app`; Perl: `perl bin/run-perltidy.pl`.

## Coding Style & Naming Conventions
- EditorConfig: LF endings; default tabs width 4 (YAML uses 2 spaces).
- Python: Black (88 cols), Ruff, MyPy. Use `snake_case` for functions/vars, `PascalCase` for classes.
- Web (TS/React): Prettier (single quotes, trailing commas), ESLint/Nx. Components `PascalCase`, files `kebab-case.tsx` where appropriate.
- Perl/PG: perltidy per `.perltidyrc`; keep `.pg` formatting where indicated.

## Testing Guidelines
- Python: pytest + FastAPI `TestClient`. Name files `test_*.py`; functions `test_*`.
- Web: Vitest + Testing Library. Name `*.test.ts(x)` near sources.
- Add/extend tests for new features and bug fixes; keep coverage from regressing.

## Commit & Pull Request Guidelines
- Conventional Commits: `feat(scope): summary`, `fix(scope): …`, `refactor: …`, `chore: …`.
- PRs: concise description, linked issues, steps to validate; screenshots for UI changes.
- CI must pass (`pnpm lint`, `pnpm test`). Include schema/migration/config updates when relevant.

## Agent-Specific Tips
- Prefer minimal, focused diffs; avoid editing `tutorial/` content unless requested.
- Use Nx targets (`dev`, `build`, `lint`, `test`); update docs when APIs or routes change.
