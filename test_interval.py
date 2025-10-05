#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test interval notation conversion."""

import re

def clean_latex_interval(latex_str):
    """Test the interval conversion."""
    # First convert \pi to π
    latex_str = latex_str.replace(r'\pi', 'π')
    print(f"After \\pi conversion: {repr(latex_str)}")
    
    # Try to convert interval notation
    pattern = r'([0-9π]),\s*([0-9π]+)\['
    matches = re.findall(pattern, latex_str)
    print(f"Pattern matches: {matches}")
    
    result = re.sub(pattern, r'\1, \2)', latex_str)
    print(f"After interval conversion: {repr(result)}")
    
    return result

# Test cases
test_cases = [
    r'\([0,2\pi[\)',
    r'[0,2\pi[',
    r'i \([0,2\pi[\).',
]

print("Testing interval notation conversion:\n")
for test in test_cases:
    print(f"Input: {repr(test)}")
    result = clean_latex_interval(test)
    print(f"Final: {repr(result)}")
    print()
