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
    "test_problems/simple_01.pg",
    "tutorial/sample-problems/Misc/FormulaAnswer.pg",
    "tutorial/sample-problems/ProblemTechniques/SimplePopUp.pg",
    "tutorial/sample-problems/Algebra/FractionAnswer.pg",
    "tutorial/sample-problems/DiffCalc/DifferentiateFunction.pg",
    "tutorial/sample-problems/Statistics/MeanStdDev.pg",
    "tutorial/sample-problems/Algebra/AlgebraicFractionAnswer.pg",
    "tutorial/sample-problems/Complex/ComplexOperations.pg",
]

results = []

for problem_path in test_problems:
    problem_file = Path(problem_path)
    if not problem_file.exists():
        results.append((problem_path, "NOT_FOUND", 0, None))
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
            results.append((problem_path, "SUCCESS", len(result.answers), None))
        else:
            error = result.errors.split('\n')[0][:60]
            results.append((problem_path, "RUNTIME_ERROR", len(result.answers), error))
    except Exception as e:
        error = str(e).split('\n')[0][:60]
        results.append((problem_path, "COMPILE_ERROR", 0, error))

print("\n" + "=" * 90)
print(" " * 30 + "EXPANDED TEST SUITE RESULTS")
print("=" * 90)
for path, status, ans_count, error in results:
    name = Path(path).stem[:35]
    if status == "SUCCESS":
        print(f"✅ {name:35s} SUCCESS       {ans_count:2d} answers")
    elif status == "NOT_FOUND":
        print(f"⚠️  {name:35s} NOT FOUND")
    else:
        print(f"❌ {name:35s} {status:14s} ({error})")

success_count = sum(1 for _, s, _, _ in results if s == "SUCCESS")
print("=" * 90)
print(f"Success rate: {success_count}/{len(results)} ({success_count*100//len(results)}%)")
print("=" * 90)
