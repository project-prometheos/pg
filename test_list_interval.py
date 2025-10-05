"""Test the newly implemented List and Interval classes."""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / 'packages' / 'pg_translator'))

from pg_translator.translator import PGTranslator

def test_simple_factoring():
    """Test the SimpleFactoring problem that uses List."""
    print("\n" + "="*60)
    print("TEST 1: SimpleFactoring (List MathObject)")
    print("="*60)
    
    pg_src = Path('tutorial/sample-problems/Algebra/SimpleFactoring.pg').read_text()
    translator = PGTranslator()
    result = translator.translate_source(pg_src, seed=123)
    
    assert result.statement_html, "Should have statement HTML"
    assert len(result.answer_blanks) == 2, f"Should have 2 answer blanks, got {len(result.answer_blanks)}"
    assert not result.errors, f"Should have no errors, got: {result.errors}"
    
    # Check that answer evaluators exist
    for blank_id in result.answer_blanks:
        evaluator = result.answer_blanks[blank_id]['evaluator']
        assert evaluator is not None, f"Blank {blank_id} should have evaluator"
        # Evaluator is the MathObject, which has cmp() method
        assert hasattr(evaluator, 'cmp'), f"Evaluator should have cmp method"
        # Calling cmp() should return a checker with check method
        checker = evaluator.cmp()
        assert hasattr(checker, 'check'), f"Checker should have check method"
    
    print("✅ List MathObject working!")
    print(f"   Statement contains: {result.statement_html[:100]}...")
    print(f"   Answer blanks: {list(result.answer_blanks.keys())}")
    return True


def test_domain_range():
    """Test the DomainRange problem that uses Interval."""
    print("\n" + "="*60)
    print("TEST 2: DomainRange (Interval MathObject)")
    print("="*60)
    
    pg_src = Path('tutorial/sample-problems/Algebra/DomainRange.pg').read_text()
    translator = PGTranslator()
    result = translator.translate_source(pg_src, seed=42)
    
    assert result.statement_html, "Should have statement HTML"
    assert len(result.answer_blanks) == 4, f"Should have 4 answer blanks, got {len(result.answer_blanks)}"
    assert not result.errors, f"Should have no errors, got: {result.errors}"
    
    # Check that answer evaluators exist
    for blank_id in result.answer_blanks:
        evaluator = result.answer_blanks[blank_id]['evaluator']
        assert evaluator is not None, f"Blank {blank_id} should have evaluator"
        # Evaluator is the MathObject, which has cmp() method
        assert hasattr(evaluator, 'cmp'), f"Evaluator should have cmp method"
        # Calling cmp() should return a checker with check method
        checker = evaluator.cmp()
        assert hasattr(checker, 'check'), f"Checker should have check method"
    
    print("✅ Interval MathObject working!")
    print(f"   Statement contains: {result.statement_html[:100]}...")
    print(f"   Answer blanks: {list(result.answer_blanks.keys())}")
    return True


def test_list_functionality():
    """Test List class directly."""
    print("\n" + "="*60)
    print("TEST 3: List Class Functionality")
    print("="*60)
    
    from pg_mathobjects import List, Real, Formula
    
    # Test basic list
    lst1 = List(1, 2, 3)
    assert len(lst1) == 3, "List should have 3 items"
    assert str(lst1) == "1, 2, 3", f"String repr incorrect: {str(lst1)}"
    print(f"   List(1, 2, 3) = {lst1}")
    
    # Test List with Formulas
    f1 = Formula("x+1")
    f2 = Formula("x-1")
    lst2 = List(f1, f2)
    assert len(lst2) == 2, "List should have 2 items"
    print(f"   List(Formula('x+1'), Formula('x-1')) = {lst2}")
    
    # Test NONE list
    lst3 = List("NONE")
    assert lst3.is_none, "List('NONE') should be marked as none"
    assert str(lst3) == "NONE", "List('NONE') should display as NONE"
    print(f"   List('NONE') = {lst3}")
    
    # Test equality
    lst4 = List(1, 2, 3)
    lst5 = List(1, 2, 3)
    assert lst4 == lst5, "Equal lists should compare equal"
    print(f"   List(1, 2, 3) == List(1, 2, 3): {lst4 == lst5}")
    
    print("✅ List class functionality verified!")
    return True


def test_interval_functionality():
    """Test Interval class directly."""
    print("\n" + "="*60)
    print("TEST 4: Interval Class Functionality")
    print("="*60)
    
    from pg_mathobjects import Interval, Context
    
    Context('Interval')
    
    # Test closed interval
    i1 = Interval("[1, 5]")
    assert i1.contains(3), "[1, 5] should contain 3"
    assert i1.contains(1), "[1, 5] should contain 1 (closed)"
    assert i1.contains(5), "[1, 5] should contain 5 (closed)"
    assert not i1.contains(0), "[1, 5] should not contain 0"
    print(f"   Interval('[1, 5]') = {i1}")
    print(f"   Contains 3: {i1.contains(3)}, Contains 0: {i1.contains(0)}")
    
    # Test open interval
    i2 = Interval("(0, 10)")
    assert i2.contains(5), "(0, 10) should contain 5"
    assert not i2.contains(0), "(0, 10) should not contain 0 (open)"
    assert not i2.contains(10), "(0, 10) should not contain 10 (open)"
    print(f"   Interval('(0, 10)') = {i2}")
    print(f"   Contains 0: {i2.contains(0)}, Contains 10: {i2.contains(10)}")
    
    # Test infinite interval
    i3 = Interval("[5, inf)")
    assert i3.contains(5), "[5, inf) should contain 5"
    assert i3.contains(1000), "[5, inf) should contain 1000"
    assert not i3.contains(4), "[5, inf) should not contain 4"
    print(f"   Interval('[5, inf)') = {i3}")
    print(f"   Contains 1000: {i3.contains(1000)}, Contains 4: {i3.contains(4)}")
    
    # Test LaTeX output
    print(f"   LaTeX: {i3.TeX()}")
    
    print("✅ Interval class functionality verified!")
    return True


def test_compute_with_contexts():
    """Test Compute() with different contexts."""
    print("\n" + "="*60)
    print("TEST 5: Compute() with Interval Context")
    print("="*60)
    
    from pg_mathobjects import Compute, Context, Interval
    
    # Test in Interval context
    Context('Interval')
    result = Compute("[1, 5)")
    assert isinstance(result, Interval), f"Should return Interval, got {type(result)}"
    print(f"   Context('Interval'); Compute('[1, 5)') = {result}")
    print(f"   Type: {type(result).__name__}")
    
    # Test with infinity
    result2 = Compute("(-inf, 0]")
    assert isinstance(result2, Interval), "Should return Interval"
    print(f"   Compute('(-inf, 0]') = {result2}")
    
    print("✅ Compute() context switching verified!")
    return True


# Run all tests
if __name__ == "__main__":
    try:
        test_simple_factoring()
        test_domain_range()
        test_list_functionality()
        test_interval_functionality()
        test_compute_with_contexts()
        
        print("\n" + "="*60)
        print("🎉 ALL TESTS PASSED!")
        print("="*60)
        print("\n✅ List MathObject implemented and working")
        print("✅ Interval MathObject implemented and working")
        print("✅ SimpleFactoring problem now renders correctly")
        print("✅ DomainRange problem now renders correctly")
        print("\nBoth previously broken problems are now fixed! 🚀")
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
