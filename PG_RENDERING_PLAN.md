# Plan: Render Database Problems (PG Files)

## Current State

✅ **What's Working:**
- Database with 157 problems imported
- Search API returning problem metadata
- Browse UI showing all problems
- Full PG source stored in database

🚧 **What's Missing:**
- Rendering PG files from database
- Seed-based problem variation for database problems
- Integration with existing problem renderer

## The Challenge

We have two separate problem systems:
1. **Registry-based** (existing): Programmatic problems in Python (`problemkit`)
2. **Database-based** (new): PG files in SQLite

The existing frontend expects the registry format, but database problems are raw PG files that need to be parsed and rendered.

## Solution Architecture

### Option A: Perl Runtime Integration (Quick, Uses Existing Infrastructure)

**Idea**: Use the existing Perl PG rendering system via subprocess calls.

```
Database (PG file) → Python wrapper → Perl PG.pm → JSON response → Frontend
```

**Pros:**
- ✅ Reuses battle-tested PG.pm renderer
- ✅ Handles all PG features correctly
- ✅ Quick to implement (~200 LOC)
- ✅ No need to rewrite PG parser

**Cons:**
- ❌ Requires Perl runtime dependency
- ❌ Slower (subprocess overhead)
- ❌ More complex deployment

**Implementation:**
```python
# apps/backend/app/services/pg_renderer.py
import subprocess
import json
from pathlib import Path
from typing import Dict, Any

class PGRenderer:
    """Render PG problems using Perl PG.pm system."""
    
    def __init__(self):
        self.pg_root = Path(__file__).parent.parent.parent.parent
        self.perl_lib = self.pg_root / 'lib'
    
    def render_pg_file(self, pg_source: str, seed: int = 0) -> Dict[str, Any]:
        """
        Render a PG file to get problem HTML and answer evaluators.
        
        Args:
            pg_source: The PG file content as a string
            seed: Random seed for problem variation
            
        Returns:
            Dict with: statement_html, inputs, answers, solution_html
        """
        # Write PG source to temp file
        import tempfile
        with tempfile.NamedTemporaryFile(mode='w', suffix='.pg', delete=False) as f:
            f.write(pg_source)
            temp_path = f.name
        
        try:
            # Call Perl renderer
            result = subprocess.run([
                'perl',
                str(self.pg_root / 'scripts' / 'render_pg.pl'),
                temp_path,
                str(seed)
            ], capture_output=True, text=True, check=True)
            
            # Parse JSON response
            return json.loads(result.stdout)
        finally:
            Path(temp_path).unlink()
```

```perl
#!/usr/bin/env perl
# scripts/render_pg.pl - Minimal PG renderer for database problems

use strict;
use warnings;
use JSON::PP;
use lib 'lib';
use WeBWorK::PG;

my ($pg_file, $seed) = @ARGV;
die "Usage: render_pg.pl <pg_file> <seed>\n" unless $pg_file && defined $seed;

# Create PG translator
my $pg = WeBWorK::PG->new(
    sourceFilePath => $pg_file,
    problemSeed => $seed,
    displayMode => 'MathJax',
);

# Extract rendered content
my $result = {
    statement_html => $pg->{result}{text},
    inputs => $pg->{result}{flags}{ANSWER_ENTRY_ORDER} || [],
    answers => {},
    solution_html => $pg->{result}{solution} || '',
};

# Extract answer evaluators
foreach my $ans_name (keys %{$pg->{answers}}) {
    $result->{answers}{$ans_name} = {
        correct_value => $pg->{answers}{$ans_name}{correct_ans} || '',
        preview => $pg->{answers}{$ans_name}{preview_latex_string} || '',
    };
}

print encode_json($result);
```

**Estimated Time**: 4-6 hours
**Risk**: Medium (Perl dependency)

---

### Option B: Pure Python PG Renderer (Clean, Portable, More Work)

**Idea**: Build a minimal PG interpreter in Python that handles the most common PG constructs.

```
Database (PG file) → Python PG parser → AST → Renderer → JSON response → Frontend
```

**Pros:**
- ✅ No Perl dependency
- ✅ Fully portable
- ✅ Easier to extend
- ✅ Better performance

**Cons:**
- ❌ Need to implement PG language subset
- ❌ May not support all PG features initially
- ❌ More code to maintain (~1000 LOC)

**What PG Features to Support:**

1. **Core** (MVP):
   - Variable interpolation: `$a`, `$f`
   - Basic math: `+`, `-`, `*`, `/`, `^`
   - PGML markup: `[@ ... @]`, `[_ @]`, `[| ... |]`
   - Answer blanks: `[_____]{$answer}`
   - Context setup: `Context("Numeric")`

2. **Phase 2**:
   - Randomization: `random()`, `non_zero_random()`
   - Formulas: `Formula("x^2 + 1")`
   - Lists: `List(1, 2, 3)`
   - Intervals: `Interval("[0,1]")`

3. **Phase 3**:
   - Graphs: `init_graph()`, `add_functions()`
   - Tables: `DataTable()`
   - Custom checkers

**Implementation Sketch:**
```python
# packages/pg_renderer/pg_renderer/parser.py
import re
from typing import Dict, Any, List

class SimplePGParser:
    """Parse and execute a subset of PG language."""
    
    def __init__(self, pg_source: str, seed: int = 0):
        self.source = pg_source
        self.seed = seed
        self.context = {}
        self.answers = {}
        
    def parse(self) -> Dict[str, Any]:
        """Parse PG file and return rendered problem."""
        
        # 1. Extract setup section (before BEGIN_PGML)
        setup, pgml = self._split_sections()
        
        # 2. Execute setup to populate context
        self._execute_setup(setup)
        
        # 3. Render PGML with context
        statement_html = self._render_pgml(pgml)
        
        return {
            'statement_html': statement_html,
            'inputs': list(self.answers.keys()),
            'answers': self.answers,
            'solution_html': self._render_solution()
        }
    
    def _execute_setup(self, setup: str):
        """Execute Perl-like setup code in Python."""
        # Parse variable assignments
        for match in re.finditer(r'\$(\w+)\s*=\s*(.+?);', setup):
            var_name = match.group(1)
            var_value = match.group(2)
            self.context[var_name] = self._eval_expression(var_value)
    
    def _render_pgml(self, pgml: str) -> str:
        """Convert PGML to HTML."""
        html = pgml
        
        # Replace variable interpolations: [$var]
        html = re.sub(r'\[\$(\w+)\]', lambda m: str(self.context.get(m.group(1), '')), html)
        
        # Replace answer blanks: [_____]{$answer}
        html = re.sub(
            r'\[_+\]\{([^}]+)\}',
            lambda m: self._create_answer_blank(m.group(1)),
            html
        )
        
        # Basic PGML formatting
        html = html.replace('[*', '<strong>').replace('*]', '</strong>')
        html = html.replace('[|', '<em>').replace('|]', '</em>')
        
        return html
    
    def _create_answer_blank(self, answer_expr: str) -> str:
        """Create an answer blank and register the answer."""
        answer_id = f"AnSwEr{len(self.answers):04d}"
        
        # Evaluate answer expression
        correct_value = self._eval_expression(answer_expr.strip('$'))
        
        self.answers[answer_id] = {
            'correct_value': str(correct_value),
            'type': 'text'
        }
        
        return f'<input type="text" name="{answer_id}" />'
```

**Estimated Time**: 2-3 weeks
**Risk**: High (complex parsing)

---

### Option C: Hybrid Approach (RECOMMENDED)

**Idea**: Start with Perl (Option A) for correctness, gradually migrate to Python (Option B) for common patterns.

**Phase 1** (This Week): Perl Integration
- Create Perl wrapper script
- Add Python service to call Perl
- Add new API endpoint for database problems
- Test with 10-20 problems

**Phase 2** (Next Week): Python Renderer (Incremental)
- Implement Python renderer for simple problems
- Fall back to Perl for complex features
- Migrate problems one category at a time

**Phase 3** (Later): Full Python
- Deprecate Perl dependency
- Support all PG features in Python

---

## Implementation Plan: Option C (Recommended)

### Step 1: Create Perl Renderer Wrapper (Day 1)

```perl
#!/usr/bin/env perl
# scripts/render_pg.pl

use strict;
use warnings;
use JSON::PP;
use FindBin;
use lib "$FindBin::Bin/../lib";
use WeBWorK::PG;
use File::Temp qw(tempfile);

my $pg_source = do { local $/; <STDIN> }; # Read from stdin
my $seed = $ARGV[0] || 0;

# Write to temp file
my ($fh, $temp_file) = tempfile(SUFFIX => '.pg', UNLINK => 1);
print $fh $pg_source;
close $fh;

# Create PG environment
my $pg = WeBWorK::PG->new(
    sourceFilePath => $temp_file,
    problemSeed => $seed,
    displayMode => 'MathJax',
    outputMode => 'HTML',
);

# Build response
my $response = {
    statement_html => $pg->{result}{text} || '',
    inputs => $pg->{result}{flags}{ANSWER_ENTRY_ORDER} || [],
    answers => {},
    solution_html => $pg->{result}{solution} || '',
    warnings => $pg->{result}{warnings} || [],
    errors => $pg->{result}{errors} || [],
};

# Extract answer metadata
foreach my $ans_name (@{$response->{inputs}}) {
    if (my $ans = $pg->{answers}{$ans_name}) {
        $response->{answers}{$ans_name} = {
            correct_value => $ans->{correct_ans} || '',
            type => $ans->{type} || 'text',
            preview => $ans->{preview_latex_string} || '',
        };
    }
}

print encode_json($response);
```

### Step 2: Python Service Wrapper (Day 1)

```python
# apps/backend/app/services/pg_renderer.py

import subprocess
import json
from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class PGRenderError(Exception):
    """Error rendering PG problem."""
    pass

class PGRenderer:
    """Render PG problems using Perl backend."""
    
    def __init__(self):
        self.pg_root = Path(__file__).parent.parent.parent.parent.parent
        self.render_script = self.pg_root / 'scripts' / 'render_pg.pl'
        
        if not self.render_script.exists():
            raise FileNotFoundError(f"PG render script not found: {self.render_script}")
    
    def render(self, pg_source: str, seed: int = 0) -> Dict[str, Any]:
        """
        Render a PG problem to HTML with answer evaluators.
        
        Args:
            pg_source: Full PG file content
            seed: Random seed for problem variation
            
        Returns:
            {
                'statement_html': str,
                'inputs': List[str],
                'answers': Dict[str, Dict],
                'solution_html': str,
                'warnings': List[str],
                'errors': List[str]
            }
        """
        try:
            result = subprocess.run(
                ['perl', str(self.render_script), str(seed)],
                input=pg_source,
                capture_output=True,
                text=True,
                timeout=10,
                check=False
            )
            
            if result.returncode != 0:
                logger.error(f"PG render failed: {result.stderr}")
                raise PGRenderError(f"Perl renderer failed: {result.stderr}")
            
            return json.loads(result.stdout)
            
        except subprocess.TimeoutExpired:
            raise PGRenderError("PG rendering timed out")
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from renderer: {result.stdout}")
            raise PGRenderError(f"Invalid renderer output: {e}")
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            raise PGRenderError(f"Rendering failed: {e}")

# Singleton instance
_renderer: Optional[PGRenderer] = None

def get_renderer() -> PGRenderer:
    """Get singleton PG renderer instance."""
    global _renderer
    if _renderer is None:
        _renderer = PGRenderer()
    return _renderer
```

### Step 3: New API Endpoint (Day 1-2)

```python
# apps/backend/app/routers/problems_search.py (add to existing)

from ..services.pg_renderer import get_renderer, PGRenderError

@router.get("/db/{problem_id}/render", tags=["problems", "database"])
def render_database_problem(
    problem_id: str,
    seed: int = Query(0, ge=0, description="Random seed for problem variation"),
    db: ProblemDB = Depends(get_db)
) -> Dict[str, Any]:
    """
    Render a database problem with the given seed.
    
    This endpoint fetches a PG problem from the database,
    renders it using the PG system, and returns the HTML
    and answer evaluators.
    """
    # Get problem from database
    problem = db.get_by_id(problem_id)
    if not problem:
        raise HTTPException(404, f"Problem not found: {problem_id}")
    
    # Render PG source
    try:
        renderer = get_renderer()
        rendered = renderer.render(problem['pg_source'], seed=seed)
        
        return {
            'problem_id': problem_id,
            'name': problem['name'],
            'seed': seed,
            'statement_html': rendered['statement_html'],
            'inputs': rendered['inputs'],
            'answers': rendered['answers'],
            'solution_html': rendered['solution_html'],
            'warnings': rendered.get('warnings', []),
            'metadata': problem['metadata']
        }
    except PGRenderError as e:
        raise HTTPException(500, f"Failed to render problem: {str(e)}")
```

### Step 4: Update Frontend (Day 2)

```typescript
// apps/web/src/pages/BrowsePage.tsx - Update click handler

const handleProblemClick = (problemId: string) => {
  // Navigate to database problem renderer
  navigate(`/db/${problemId}?seed=0`);
};
```

```typescript
// apps/web/src/pages/DatabaseProblemPage.tsx - NEW FILE

import { useMemo } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { useNavigate, useParams, useSearchParams } from 'react-router-dom';

import { fetchDatabaseProblem, submitDatabaseAttempt } from '../services/api';
import Feedback from '../components/Feedback';
import ProblemRenderer from '../components/ProblemRenderer';
import SeedBox from '../components/SeedBox';

const DatabaseProblemPage = () => {
  const params = useParams();
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  const problemId = params.id!;
  const seed = Number(searchParams.get('seed') ?? '0');

  const { data, isPending } = useQuery({
    queryKey: ['db-problem', problemId, seed],
    queryFn: () => fetchDatabaseProblem(problemId, seed),
  });

  const mutation = useMutation({
    mutationFn: submitDatabaseAttempt,
  });

  const onSeedChange = (nextSeed: number) => {
    setSearchParams({ seed: String(nextSeed) });
  };

  const onSubmit = (values: Record<string, string>) => {
    if (!data) return;
    mutation.mutate({
      problemId,
      seed,
      inputs: values,
    });
  };

  return (
    <div className="mx-auto flex max-w-3xl flex-col gap-6 p-6">
      <header className="flex flex-col gap-2">
        <button
          onClick={() => navigate('/')}
          className="text-sm text-blue-600 hover:underline text-left"
        >
          ← Back to Browse
        </button>
        <h1 className="text-2xl font-semibold">{data?.name || problemId}</h1>
        <SeedBox seed={seed} onChange={onSeedChange} loading={isPending} />
      </header>
      <main>
        <ProblemRenderer problem={data} loading={isPending} onSubmit={onSubmit} />
      </main>
      {mutation.data && <Feedback feedback={mutation.data} />}
    </div>
  );
};

export default DatabaseProblemPage;
```

```typescript
// apps/web/src/services/api.ts - Add new functions

export async function fetchDatabaseProblem(problemId: string, seed: number) {
  const response = await fetch(`/api/problems/db/${problemId}/render?seed=${seed}`);
  if (!response.ok) throw new Error('Failed to fetch database problem');
  return response.json();
}

export async function submitDatabaseAttempt(data: {
  problemId: string;
  seed: number;
  inputs: Record<string, string>;
}) {
  const response = await fetch(`/api/problems/db/${data.problemId}/check`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ seed: data.seed, inputs: data.inputs }),
  });
  if (!response.ok) throw new Error('Failed to check answers');
  return response.json();
}
```

### Step 5: Answer Checking (Day 3)

```python
# apps/backend/app/routers/problems_search.py (add to existing)

@router.post("/db/{problem_id}/check", tags=["problems", "database"])
def check_database_problem_answers(
    problem_id: str,
    request_data: Dict[str, Any],
    db: ProblemDB = Depends(get_db)
) -> Dict[str, Any]:
    """Check student answers for a database problem."""
    seed = request_data.get('seed', 0)
    inputs = request_data.get('inputs', {})
    
    # Get problem
    problem = db.get_by_id(problem_id)
    if not problem:
        raise HTTPException(404, f"Problem not found: {problem_id}")
    
    # Render to get correct answers
    try:
        renderer = get_renderer()
        rendered = renderer.render(problem['pg_source'], seed=seed)
        
        # Check each answer
        results = {}
        for answer_id, student_answer in inputs.items():
            if answer_id in rendered['answers']:
                correct = rendered['answers'][answer_id]['correct_value']
                # Simple string comparison (TODO: improve with MathObject comparison)
                is_correct = student_answer.strip() == str(correct).strip()
                results[answer_id] = {
                    'correct': is_correct,
                    'student_answer': student_answer,
                    'correct_answer': correct,
                    'message': 'Correct!' if is_correct else 'Incorrect'
                }
        
        return {
            'results': results,
            'all_correct': all(r['correct'] for r in results.values())
        }
    except PGRenderError as e:
        raise HTTPException(500, f"Failed to check answers: {str(e)}")
```

---

## Timeline

### Week 1: MVP (Perl-based rendering)
- **Day 1**: Perl wrapper + Python service (4 hours)
- **Day 2**: API endpoint + Frontend integration (6 hours)
- **Day 3**: Answer checking + Testing (4 hours)
- **Day 4**: Bug fixes + Documentation (4 hours)
- **Day 5**: Polish + Deploy (2 hours)

**Deliverable**: Can view and solve database problems in browser

### Week 2-3: Improve & Scale (Optional)
- Add caching for rendered problems
- Implement Python renderer for simple problems
- Import more problem collections (OPL)
- Add problem stats and analytics

---

## Testing Strategy

1. **Unit Tests**: Test renderer with known PG files
2. **Integration Tests**: End-to-end problem rendering
3. **Manual Testing**: Verify 20 sample problems render correctly

```python
# tests/test_pg_renderer.py

def test_simple_numeric_problem():
    pg_source = """
DOCUMENT();
loadMacros("PGstandard.pl", "PGML.pl");
Context("Numeric");
$a = 2;
$b = 3;
$answer = $a + $b;
BEGIN_PGML
What is [$a] + [$b]?
Answer: [_____]{$answer}
END_PGML
ENDDOCUMENT();
"""
    renderer = PGRenderer()
    result = renderer.render(pg_source, seed=0)
    
    assert '2' in result['statement_html']
    assert '3' in result['statement_html']
    assert len(result['inputs']) == 1
    assert result['answers'][result['inputs'][0]]['correct_value'] == '5'
```

---

## Risk Mitigation

### Risk 1: Perl not available on deployment
**Mitigation**: 
- Provide Docker image with Perl pre-installed
- Document Perl installation clearly
- Consider Python fallback for simple problems

### Risk 2: PG rendering too slow
**Mitigation**:
- Add Redis caching for rendered problems
- Pre-render popular problems
- Implement async rendering queue

### Risk 3: Complex PG features break
**Mitigation**:
- Start with simple problems only
- Add feature detection to skip unsupported problems
- Provide clear error messages

---

## Success Criteria

✅ Can render at least 80% of database problems correctly
✅ Rendering completes in < 2 seconds per problem
✅ Students can submit answers and get feedback
✅ Seed variation works (different random values)
✅ Documentation exists for adding new problems

---

## Next Steps After This Plan

1. Import OPL collections (35,000+ problems)
2. Add problem search with filtering
3. Implement problem recommendations
4. Add instructor problem authoring UI
5. Deploy to production

---

**Estimated Total Time**: 20-30 hours (1 week with focus)
**Recommended Approach**: Option C (Hybrid Perl → Python)
**Priority**: High (needed to make database useful)

