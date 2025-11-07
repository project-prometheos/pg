import sys
from pathlib import Path

for pkg in ['pg_translator', 'pg_macros', 'pg_math', 'pg_mathobjects', 
            'pg_parser', 'pg_answer', 'pg_pgml', 'pg_renderer']:
    sys.path.insert(0, str(Path(__file__).parent / "packages" / pkg))

from pg_translator.in_process_sandbox import InProcessSandbox
from pg_translator.macro_loader import MacroLoader
from pg_translator.preprocessor import PGPreprocessor
from pg_parser import Context

test_problems = [
    "tutorial/sample-problems/Misc/FormulaAnswer.pg",
    "tutorial/sample-problems/ProblemTechniques/SimplePopUp.pg",
    "tutorial/sample-problems/Algebra/FractionAnswer.pg",
    "tutorial/sample-problems/DiffCalc/DifferentiateFunction.pg",
    "tutorial/sample-problems/Statistics/MeanStdDev.pg",
]

results = []

for problem_path in test_problems:
    problem_file = Path(problem_path)
    if not problem_file.exists():
        results.append((problem_path, "NOT FOUND", None))
        continue
    
    try:
        problem_code = problem_file.read_text()
        sandbox = InProcessSandbox(timeout=30)
        macro_loader = MacroLoader(sandbox)
        sandbox.namespace['_macro_loader'] = macro_loader
        preprocessor = PGPreprocessor()
        preprocessed_code = preprocessor.preprocess(problem_code).code
        result = sandbox.execute(preprocessed_code, seed=123, context=Context("Numeric"))
        
        if result.success:
            results.append((problem_path, "SUCCESS", len(result.answers)))
        else:
            error = result.errors.split('\n')[0][:100]
            results.append((problem_path, f"FAIL: {error}", None))
    except Exception as e:
        error = str(e)[:100]
        results.append((problem_path, f"ERROR: {error}", None))

print("\n" + "=" * 80)
print("MULTIPLE PROBLEM TEST RESULTS")
print("=" * 80)
for path, status, ans_count in results:
    name = Path(path).stem
    if status == "SUCCESS":
        print(f"✅ {name:40s} {status:20s} ({ans_count} answers)")
    elif status == "NOT FOUND":
        print(f"⚠️  {name:40s} {status:20s}")
    else:
        print(f"❌ {name:40s} {status[:40]:40s}")

success_count = sum(1 for _, s, _ in results if s == "SUCCESS")
print("=" * 80)
print(f"Success rate: {success_count}/{len(results)}")
