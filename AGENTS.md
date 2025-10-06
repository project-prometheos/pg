# Repository Guidelines

## Project Structure & Module Organization
- Monorepo managed by pnpm + Nx. Application code lives in `apps/`.
- `apps/backend` hosts the FastAPI service with SQLite/Alembic; API tests in `apps/backend/tests`.
- `apps/web` contains the React + Vite + TypeScript app; sources in `apps/web/src` with component tests beside `.test.ts(x)` files.
- `packages/*` provides shared Python libraries (e.g., `problemkit`) and Postgres tooling consumed by services.
- `assets/` and `tutorial/` store TeX/PG references; coordinate before editing to avoid breaking published materials.
- Tooling and CI scripts live under `bin/`, `.github/`, and `docker/`.

## Build, Test, and Development Commands
- Install JavaScript dependencies with `pnpm install`; provision Python tooling via `python -m pip install -e apps/backend[dev] -e packages/problemkit`.
- Launch both apps locally using `pnpm dev`, which runs backend and web targets through Nx.
- Start only the API with `cd apps/backend && uvicorn app.main:app --reload`; launch the web UI via `pnpm --dir apps/web dev`.
- Run the Nx test matrix with `pnpm test`; targeted suites: `cd apps/backend && pytest -q` and `pnpm --dir apps/web test`.
- Enforce formatting and linting using `pnpm lint`, `python -m ruff check apps/backend/app`, and `python -m black apps/backend/app`.

## Coding Style & Naming Conventions
- Follow `.editorconfig`: LF line endings, tab width 4 (YAML uses 2 spaces).
- Python adheres to Black (88 columns) and Ruff; prefer `snake_case` for functions or variables and `PascalCase` for classes.
- Web code relies on Prettier (single quotes, trailing commas) and ESLint/Nx; keep component names in `PascalCase` and file names in `kebab-case.tsx` when appropriate.
- Format Perl or PG assets with `perl bin/run-perltidy.pl`; respect existing `.pg` directives.

## Testing Guidelines
- Backend tests use pytest and FastAPI `TestClient`; place them in `apps/backend/tests` as `test_*.py`.
- Frontend tests run on Vitest with Testing Library, named `*.test.ts(x)` alongside the component under test.
- Add or extend tests with each feature or bug fix and aim to maintain coverage; favor fast Nx targets before running the full suite.

## Commit & Pull Request Guidelines
- Commit messages follow Conventional Commits (`feat(scope): summary`, `fix(scope): ...`, `chore: ...`).
- Pull requests should provide a concise summary, link relevant issues, list validation steps (`pnpm lint`, `pnpm test`), and attach UI screenshots when applicable.
- Include schema, migration, or configuration updates alongside code changes that depend on them.

## Agent-Specific Tips
- Keep diffs minimal and avoid touching `tutorial/` unless requested.
- Prefer `rg` for search and Nx targets for builds or tests; verify changes with the smallest meaningful command set before requesting review.
