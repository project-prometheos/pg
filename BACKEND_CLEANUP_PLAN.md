# Backend Cleanup Plan

## Goal
Remove the old service wrapper (`pg_renderer_python.py`) and use the packages directly in the routers.

## Changes Needed

### 1. Update `apps/backend/app/routers/problems_search.py`
- **Line 8**: Replace `from ..services.pg_renderer_python import get_pg_render_service` with:
  ```python
  from pg_renderer import PGRenderer
  from pg_renderer.answer_checker import AnswerChecker
  ```

- **Lines 252-253**: Replace:
  ```python
  renderer = get_pg_render_service()
  rendered = renderer.render_problem(problem['pg_source'], seed=seed)
  ```
  with:
  ```python
  renderer = PGRenderer()
  rendered = renderer.render(problem['pg_source'], seed=seed)
  ```

- **Lines 294-295**: Replace:
  ```python
  renderer = get_pg_render_service()
  results = renderer.check_answers(problem['pg_source'], seed=seed, student_inputs=inputs)
  ```
  with inline checking logic using `PGRenderer` and `AnswerChecker`

### 2. Update `apps/backend/app/routers/database_problems.py`
- **Line 7**: Replace `from ..services.pg_renderer_python import get_pg_render_service` with:
  ```python
  from pg_renderer import PGRenderer
  from pg_renderer.answer_checker import AnswerChecker
  ```

- **Lines 38-39**: Replace:
  ```python
  renderer = get_pg_render_service()
  rendered = renderer.render_problem(problem['pg_source'], seed=seed)
  ```
  with:
  ```python
  renderer = PGRenderer()
  rendered = renderer.render(problem['pg_source'], seed=seed)
  ```

- **Lines 80-81**: Replace:
  ```python
  renderer = get_pg_render_service()
  results = renderer.check_answers(problem['pg_source'], seed=seed, student_inputs=inputs)
  ```
  with inline checking logic

### 3. Delete old service file
- Delete `apps/backend/app/services/pg_renderer_python.py`

## Implementation Order
1. Update routers first
2. Test that backend still works
3. Delete old service file

