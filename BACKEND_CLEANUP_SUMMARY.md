# Backend Cleanup Summary

## Problem
The backend has an old service wrapper (`apps/backend/app/services/pg_renderer_python.py`) that adds unnecessary complexity. The service is just a thin wrapper around the packages, which should be used directly.

## Solution
Remove the old service wrapper and use the packages directly in the routers.

## Files to Update

### 1. `apps/backend/app/routers/problems_search.py`

**Change import (line 8):**
```python
# OLD:
from ..services.pg_renderer_python import get_pg_render_service

# NEW:
from pg_renderer import PGRenderer
from pg_renderer.answer_checker import AnswerChecker
```

**Update render endpoint (lines 251-253):**
```python
# OLD:
renderer = get_pg_render_service()
rendered = renderer.render_problem(problem['pg_source'], seed=seed)

# NEW:
renderer = PGRenderer()
rendered = renderer.render(problem['pg_source'], seed=seed)
```

**Update check endpoint (lines 293-295):**
```python
# OLD:
renderer = get_pg_render_service()
results = renderer.check_answers(problem['pg_source'], seed=seed, student_inputs=inputs)

# NEW:
# Render to get correct answers
renderer = PGRenderer()
rendered = renderer.render(problem['pg_source'], seed=seed)

# Check each answer
checker = AnswerChecker(tolerance=0.01)
results = {}
for answer_id, student_answer in inputs.items():
    if answer_id in rendered['answers']:
        meta = rendered['answers'][answer_id]
        correct_answer = meta.get('correct_value')
        answer_type = meta.get('type')
        
        # Build context for answer checking
        context = {
            'variables': meta.get('variables', []),
            'checker': meta.get('checker', 'standard'),
            'options': meta.get('options', {}),
        }
        
        if answer_type == 'multi':
            is_correct, message = False, 'MultiAnswer groups are not supported yet.'
        else:
            is_correct, message = checker.check(
                student_answer,
                correct_answer,
                answer_type,
                context
            )
        
        results[answer_id] = {
            'correct': is_correct,
            'message': message,
            'student_answer': student_answer,
            'correct_answer': correct_answer,
            'answer_type': answer_type,
        }

all_correct = all(r['correct'] for r in results.values()) if results else False

return {
    'results': results,
    'all_correct': all_correct,
    'score': sum(1 for r in results.values() if r['correct']) / len(results) if results else 0
}
```

### 2. `apps/backend/app/routers/database_problems.py`

**Change import (line 7):**
```python
# OLD:
from ..services.pg_renderer_python import get_pg_render_service

# NEW:
from pg_renderer import PGRenderer
from pg_renderer.answer_checker import AnswerChecker
```

**Update render endpoint (lines 38-39):**
```python
# OLD:
renderer = get_pg_render_service()
rendered = renderer.render_problem(problem['pg_source'], seed=seed)

# NEW:
renderer = PGRenderer()
rendered = renderer.render(problem['pg_source'], seed=seed)
```

**Update check endpoint (lines 80-81):**
Same as the changes for `problems_search.py` above.

### 3. Delete old service file
After confirming the routers work with the direct package imports:
```
rm apps/backend/app/services/pg_renderer_python.py
```

## Benefits
1. **Simpler code**: No unnecessary service wrapper
2. **Less confusion**: Only one way to use the packages
3. **Easier maintenance**: Changes to packages don't require updating service wrappers
4. **Consistency**: Backend uses the same code as command-line tools

## Testing
After making the changes:
1. Start the backend: `cd apps/backend && uvicorn app.main:app --reload`
2. Test the render endpoint: `GET /api/db/{problem_id}/render?seed=42`
3. Test the check endpoint: `POST /api/db/{problem_id}/check` with test inputs
4. Verify both endpoints work correctly

## Next Steps
Once the changes are implemented and tested:
1. Delete the old service file
2. Update any documentation that references the old service
3. Commit the changes with a descriptive message like:
   ```
   refactor(backend): Remove service wrapper, use packages directly
   
   - Replace pg_renderer_python service with direct package imports
   - Simplify answer checking logic in routers
   - Delete obsolete service wrapper file
   ```

