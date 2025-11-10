import subprocess
import re

failures = [
    "AnswerOrderedList", "BarGraph", "CalculatingWithPoints", "ChemicalReaction",
    "CustomAnswerCheckers", "DraggableSubsets", "DynamicGraphPolygon",
    "ExtractingCoordinatesFromPoint", "GraphsInTables", "Images", "LinearRegression",
    "ManyMultipleChoice", "Matching", "MatchingAlt", "MatchingGraphs", "MatrixAnswer1",
    "MultipleChoiceCheckbox", "MultipleChoiceRadio", "ParametricPlotAlt",
    "PeriodicAnswers", "ProvingTrigIdentities", "RiemannSums", "Scaffolding",
    "ScatterPlot", "SeriesTest", "SimplePopUp", "SpecialTrigValues",
    "VectorOperations", "Vectors"
]

error_types = {}

for test_name in failures:
    result = subprocess.run(
        [
            "C:/Users/mdahl/.conda/envs/pytorch-5090/python.exe", "-m", "pytest",
            f"d:\pg\packages\pg_translator\tests\test_tutorial_sample_problems.py::test_tutorial_problem_renders[{test_name}]",
            "-v", "--tb=line"
        ],
        capture_output=True,
        text=True,
        timeout=10
    )
    
    output = result.stdout + result.stderr
    
    # Extract error type
    if "SyntaxError" in output:
        if "qq" in output or "qw" in output:
            error_type = "SyntaxError: Perl string operators (qq/qw)"
        elif "with" in output:
            error_type = "SyntaxError: reserved keyword (with)"
        elif "x" in output and "cross" in output.lower():
            error_type = "SyntaxError: vector cross product (x)"
        else:
            match = re.search(r"SyntaxError: ([^\n]+)", output)
            error_type = f"SyntaxError: {match.group(1)[:50]}" if match else "SyntaxError: unknown"
    elif "NameError" in output:
        match = re.search(r"NameError: ([^\n]+)", output)
        error_type = f"NameError: {match.group(1)[:50]}" if match else "NameError: unknown"
    elif "AttributeError" in output:
        match = re.search(r"AttributeError: ([^\n]+)", output)
        error_type = f"AttributeError: {match.group(1)[:50]}" if match else "AttributeError: unknown"
    elif "TypeError" in output:
        match = re.search(r"TypeError: ([^\n]+)", output)
        error_type = f"TypeError: {match.group(1)[:50]}" if match else "TypeError: unknown"
    else:
        error_type = "Other error"
    
    if error_type not in error_types:
        error_types[error_type] = []
    error_types[error_type].append(test_name)

# Print categorized results
for error_type in sorted(error_types.keys()):
    print(f"\n{error_type} ({len(error_types[error_type])} tests)")
    for test in error_types[error_type]:
        print(f"  - {test}")
