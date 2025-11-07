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
    # Phase 1: Working problems (8/8)
    "test_problems/simple_01.pg",
    "tutorial/sample-problems/Misc/FormulaAnswer.pg",
    "tutorial/sample-problems/ProblemTechniques/SimplePopUp.pg",
    "tutorial/sample-problems/Algebra/FractionAnswer.pg",
    "tutorial/sample-problems/DiffCalc/DifferentiateFunction.pg",
    "tutorial/sample-problems/Statistics/MeanStdDev.pg",
    "tutorial/sample-problems/Algebra/AlgebraicFractionAnswer.pg",
    "tutorial/sample-problems/Complex/ComplexOperations.pg",

    # Phase 2: New problems to test
    "tutorial/sample-problems/Arithmetic/UnitConversion.pg",
    "tutorial/sample-problems/ProblemTechniques/Percent.pg",
    "tutorial/sample-problems/ProblemTechniques/StringsInContext.pg",
    "tutorial/sample-problems/Algebra/ImplicitDifferentiation.pg",
    "tutorial/sample-problems/IntCalc/AreasBetweenGraphs.pg",
    "tutorial/sample-problems/Trig/TrigIdentities.pg",
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
            error = result.errors.split('\n')[0][:80]
            results.append((problem_path, "RUNTIME_ERROR", len(result.answers), error))
    except Exception as e:
        error = str(e).split('\n')[0][:80]
        results.append((problem_path, "COMPILE_ERROR", 0, error))

print("\n" + "=" * 100)
print(f"{'EXPANDED TEST SUITE V2 RESULTS':^100}")
print("=" * 100)

success_count = 0
total_count = len(results)

for path, status, num_answers, error in results:
    problem_name = Path(path).stem
    status_symbol = "✅" if status == "SUCCESS" else "❌"
    error_msg = f"({error})" if error and status != "NOT_FOUND" else ""

    if status == "SUCCESS":
        success_count += 1
        print(f"{status_symbol} {problem_name:40s} {status:15s} {num_answers} answers")
    elif status == "NOT_FOUND":
        print(f"{status_symbol} {problem_name:40s} {status:15s}")
    else:
        print(f"{status_symbol} {problem_name:40s} {status:15s} {error_msg}")

print("=" * 100)
print(f"Success rate: {success_count}/{total_count} ({100*success_count//total_count}%)")
print("=" * 100)
