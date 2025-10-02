# Problem Generator Monorepo Scaffold

This repository contains an Nx + pnpm monorepo that mirrors the strategy
outlined in the migration plan. It provides:

- `apps/backend`: FastAPI service exposing `/api` endpoints.
- `apps/web`: React + Vite frontend consuming generated problems.
- `packages/problemkit`: framework-agnostic authoring core.
- `packages/schemas` and `packages/ui`: TypeScript packages shared across apps.

## Getting started

```bash
pnpm install
pnpm dev
```

The `dev` script launches both the FastAPI server (via `uvicorn`) and the Vite
frontend with hot reloading. You can visit `http://localhost:5173` to try the
sample calculus problem end-to-end.

### Python dependencies

The backend relies on Python 3.12. Install editable dependencies for local
iteration:

```bash
python -m pip install -e packages/problemkit -e apps/backend[dev]
```

Run the FastAPI test-suite:

```bash
pnpm exec nx run backend:test
```

### Frontend tooling

```bash
pnpm exec nx run web:lint
pnpm exec nx run web:test
```

### Dev container

Open the repository in VS Code and use the included `.devcontainer` definition
for a reproducible environment with Python, Node, and pnpm pre-installed.
