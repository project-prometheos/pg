"""
Test script for simple problem rendering.

Tests that we can load macros and render a basic problem.
"""

import sys
from pathlib import Path

# Add packages to path
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_translator"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_macros"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_math"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_mathobjects"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_parser"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_answer"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_pgml"))
sys.path.insert(0, str(Path(__file__).parent / "packages" / "pg_renderer"))

from pg_translator import PGTranslator, PGExecutor
from pg_translator.preprocessor import PGPreprocessor
from pg_translator.macro_loader import MacroLoader
from pg_translator.in_process_sandbox import InProcessSandbox
from pg_parser import Context

# Read the test problem
problem_file = Path(__file__).parent / "test_problems" / "simple_01.pg"
problem_code = problem_file.read_text()

print("=" * 60)
print("Testing Simple Problem Rendering")
print("=" * 60)
print(f"\nProblem file: {problem_file}")
print("\nProblem code:")
print("-" * 60)
print(problem_code)
print("-" * 60)

# Create sandbox
print("\n1. Creating InProcessSandbox...")
sandbox = InProcessSandbox(timeout=30)

# Create macro loader
print("2. Creating MacroLoader...")
macro_loader = MacroLoader(sandbox)

# Wire up macro loader in sandbox namespace
print("3. Wiring up macro loader in sandbox namespace...")
sandbox.namespace['_macro_loader'] = macro_loader

# Preprocess the problem
print("\n4. Preprocessing problem...")
preprocessor = PGPreprocessor()
preprocess_result = preprocessor.preprocess(problem_code)
preprocessed_code = preprocess_result.code if hasattr(preprocess_result, 'code') else preprocess_result
print("\nPreprocessed code:")
print("-" * 60)
print(preprocessed_code)
print("-" * 60)

# Execute in sandbox
print("\n5. Executing problem...")
print(f"   Sandbox has pg_core: {hasattr(sandbox, '_pg_core')}")
if hasattr(sandbox, '_pg_core'):
    print(f"   pg_core module: {sandbox._pg_core}")
    print(f"   pg_core._pg_environment: {getattr(sandbox._pg_core, '_pg_environment', 'NOT FOUND')}")
print()
try:
    result = sandbox.execute(preprocessed_code, seed=123, context=Context("Numeric"))

    print(f"\nExecution result:")
    print(f"  Success: {result.success}")
    print(f"  Errors: {result.errors}")
    print(f"  Output text length: {len(result.output_text)}")
    print(f"  Answers: {list(result.answers.keys())}")

    if result.output_text:
        print(f"\nRendered output:")
        print("-" * 60)
        print(result.output_text)
        print("-" * 60)

    if result.errors:
        print(f"\nErrors:")
        print("-" * 60)
        print(result.errors)
        print("-" * 60)

except Exception as e:
    print(f"\n❌ Execution failed!")
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
print("Test complete")
print("=" * 60)
