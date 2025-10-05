#!/usr/bin/env python3
"""
Test that verifies the improved context-aware fat comma conversion.
"""
from packages.pg_translator.pg_translator.preprocessor import PGPreprocessor

def test_dict_syntax():
    """Test various fat comma (=>) conversion scenarios."""
    processor = PGPreprocessor()
    
    test_cases = [
        {
            'name': 'Simple dict literal',
            'input': "hash = { key => 'value' }",
            'expected': "hash = { key : 'value' }",
        },
        {
            'name': 'Multiple keys in dict',
            'input': "opts = { a => 1, b => 2, c => 3 }",
            'expected': "opts = { a : 1, b : 2, c : 3 }",
        },
        {
            'name': 'Function parameters only',
            'input': "func(param1 => 1, param2 => 2)",
            'expected': "func(param1  = 1, param2  = 2)",
        },
        {
            'name': 'Mixed: function with dict parameter',
            'input': "func(opts => { key => 'val' })",
            'expected': "func(opts  = { key : 'val' })",
        },
        {
            'name': 'Method chaining with dict',
            'input': "BeginTable()->with(allcellcss => { padding => '3pt' })",
            'expected': "BeginTable().with_params(allcellcss  = { padding : '3pt' })",
        },
        {
            'name': 'Avoid array refs (skips entire line)',
            'input': "hints => [ $fx ] => [ 'message' ]",
            'expected': "hints => [ fx ] => [ 'message' ]",  # No conversion (protected by ] =>)
        },
    ]
    
    all_passed = True
    for test in test_cases:
        result = processor._transform_line(test['input'])
        passed = result == test['expected']
        status = '✓' if passed else '✗'
        
        print(f"{status} {test['name']}")
        if not passed:
            print(f"  Input:    {test['input']}")
            print(f"  Expected: {test['expected']}")
            print(f"  Got:      {result}")
            all_passed = False
    
    return all_passed

if __name__ == '__main__':
    import sys
    success = test_dict_syntax()
    print(f"\n{'All tests passed!' if success else 'Some tests failed.'}")
    sys.exit(0 if success else 1)
