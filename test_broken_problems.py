"""Test the two broken problems to see what errors they produce."""
from pathlib import Path
import sys

# Add package to path
sys.path.insert(0, str(Path(__file__).parent / 'packages' / 'pg_translator'))

from pg_translator.translator import PGTranslator

def test_problem(problem_path: str):
    """Test a problem and report the error."""
    print(f"\n{'='*60}")
    print(f"Testing: {problem_path}")
    print('='*60)
    
    try:
        pg_src = Path(problem_path).read_text()
        translator = PGTranslator()
        result = translator.translate_source(pg_src, seed=0)
        
        print(f"✅ Translation successful")
        print(f"   Statement: {bool(result.statement_html)}")
        print(f"   Answer blanks: {len(result.answer_blanks)}")
        
        # Check for errors
        if result.errors:
            print(f"\n❌ Errors found:")
            for error in result.errors:
                print(f"   {error}")
        else:
            print(f"\n✅ No errors")
            
        return True
        
    except Exception as e:
        print(f"\n❌ Translation failed with exception:")
        print(f"   Type: {type(e).__name__}")
        print(f"   Message: {str(e)}")
        
        # Print traceback for more details
        import traceback
        print(f"\n   Traceback:")
        for line in traceback.format_exc().split('\n'):
            print(f"   {line}")
        
        return False

# Test both problems
test_problem('tutorial/sample-problems/Algebra/SimpleFactoring.pg')
test_problem('tutorial/sample-problems/Algebra/DomainRange.pg')
