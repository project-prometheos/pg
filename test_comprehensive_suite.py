import sys
from pathlib import Path

for pkg in ['pg_translator', 'pg_macros', 'pg_math', 'pg_mathobjects',
            'pg_parser', 'pg_answer', 'pg_pgml', 'pg_renderer']:
    sys.path.insert(0, str(Path(__file__).parent / "packages" / pkg))

from pg_translator.in_process_sandbox import InProcessSandbox
from pg_translator.macro_loader import MacroLoader
from pg_translator.preprocessor import PGPreprocessor
from pg_parser import Context

# Comprehensive test suite - various problem types
test_problems = [
    # Working problems from Phase 1 (8)
    "test_problems/simple_01.pg",
    "tutorial/sample-problems/Misc/FormulaAnswer.pg",
    "tutorial/sample-problems/ProblemTechniques/SimplePopUp.pg",
    "tutorial/sample-problems/Algebra/FractionAnswer.pg",
    "tutorial/sample-problems/DiffCalc/DifferentiateFunction.pg",
    "tutorial/sample-problems/Statistics/MeanStdDev.pg",
    "tutorial/sample-problems/Algebra/AlgebraicFractionAnswer.pg",
    "tutorial/sample-problems/Complex/ComplexOperations.pg",

    # Working from Phase 2 (2)
    "tutorial/sample-problems/ProblemTechniques/StringsInContext.pg",
    "tutorial/sample-problems/Trig/TrigIdentities.pg",

    # Algebra problems
    "tutorial/sample-problems/Algebra/InequalityAnswer.pg",
    "tutorial/sample-problems/Algebra/PointAnswers.pg",
    "tutorial/sample-problems/Algebra/DomainRange.pg",
    "tutorial/sample-problems/Algebra/Logarithms.pg",
    "tutorial/sample-problems/Algebra/LinearInequality.pg",
    "tutorial/sample-problems/Algebra/SimpleFactoring.pg",
    "tutorial/sample-problems/Algebra/NoSolution.pg",
    "tutorial/sample-problems/Algebra/FactoredPolynomial.pg",
    "tutorial/sample-problems/Algebra/ExpandedPolynomial.pg",

    # Fraction problems
    "tutorial/sample-problems/ProblemTechniques/RestrictAnswerToFraction.pg",

    # More Trig
    "tutorial/sample-problems/Trig/PeriodicAnswers.pg",
    "tutorial/sample-problems/Trig/SpecialTrigValues.pg",
    "tutorial/sample-problems/Trig/TrigDegrees.pg",

    # More DiffCalc problems
    "tutorial/sample-problems/DiffCalc/DifferenceQuotient.pg",
    "tutorial/sample-problems/DiffCalc/LinearApprox.pg",
    "tutorial/sample-problems/DiffCalc/AnswerWithUnits.pg",

    # IntegralCalc problems
    "tutorial/sample-problems/IntegralCalc/IndefiniteIntegrals.pg",
    "tutorial/sample-problems/IntegralCalc/LimitsOfIntegration.pg",
    "tutorial/sample-problems/IntegralCalc/DoubleIntegral.pg",

    # More Misc
    "tutorial/sample-problems/Misc/EssayAnswer.pg",
    "tutorial/sample-problems/Misc/MultipleChoicePopup.pg",
    "tutorial/sample-problems/Misc/MultipleChoiceRadio.pg",
]

results = []
success_count = 0

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
            success_count += 1
        else:
            error = result.errors.split('\n')[0][:70]
            results.append((problem_path, "RUNTIME_ERROR", len(result.answers), error))
    except Exception as e:
        error = str(e).split('\n')[0][:70]
        results.append((problem_path, "COMPILE_ERROR", 0, error))

print("\n" + "=" * 95)
print(f"{'COMPREHENSIVE TEST SUITE':^95}")
print("=" * 95)

for path, status, num_answers, error in results:
    problem_name = Path(path).stem
    status_symbol = "✅" if status == "SUCCESS" else "❌"

    if status == "SUCCESS":
        print(f"{status_symbol} {problem_name:45s} SUCCESS")
    elif status == "NOT_FOUND":
        print(f"{status_symbol} {problem_name:45s} NOT_FOUND")
    else:
        error_msg = f"({error})" if error else ""
        print(f"{status_symbol} {problem_name:45s} ERROR {error_msg}")

print("=" * 95)
print(f"Success rate: {success_count}/{len(results)} ({100*success_count//len(results)}%)")
print("=" * 95)
