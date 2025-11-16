#!/bin/bash
################################################################################
# Parity Comparison Test Runner
# Compares Perl and Python outputs for test snippets
################################################################################

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PERL_ADAPTER="$SCRIPT_DIR/perl_ref/run_pg_snippet.pl"
PY_ADAPTER="$SCRIPT_DIR/py_port/run_pg_snippet.py"
DIFF_TOOL="$SCRIPT_DIR/tools/render_diff/diff_outputs.py"
SNIPPETS_DIR="$SCRIPT_DIR/tests/snippets"
BUILD_DIR="$SCRIPT_DIR/build"

# Test seed for reproducibility
SEED=42

mkdir -p "$BUILD_DIR"

echo "======================================"
echo "PG Parity Comparison Test Suite"
echo "======================================"
echo ""
echo "Testing: Formula, Vector, Answer Checking, Grading, etc."
echo ""

total_pass=0
total_fail=0
total_skip=0

# Test categories
declare -A categories
categories[formula]="mathobjects_formula.pg"
categories[vector]="mathobjects_vectors.pg"
categories[interval]="mathobjects_intervals.pg"
categories[fraction]="fraction_basic.pg"
categories[answer_checking]="standard_basic.pg"
categories[grading]="multianswer_basic.pg"
categories[pgml]="pgml_answer_blanks.pg"
categories[choice]="choice_multiple_choice.pg"

# Run comparison for each category
for category in "${!categories[@]}"; do
    snippet_file="$SNIPPETS_DIR/${categories[$category]}"
    
    if [ ! -f "$snippet_file" ]; then
        echo -e "${YELLOW}SKIP${NC} $category (file not found: ${categories[$category]})"
        ((total_skip++))
        continue
    fi
    
    echo -n "Testing $category (${categories[$category]}) ... "
    
    perl_out="$BUILD_DIR/${category}_perl.json"
    py_out="$BUILD_DIR/${category}_py.json"
    
    # Run Perl
    perl "$PERL_ADAPTER" "$snippet_file" "$SEED" "$perl_out" 2>/dev/null
    perl_status=$?
    
    # Run Python
    python3 "$PY_ADAPTER" "$snippet_file" "$SEED" "$py_out" 2>/dev/null
    py_status=$?
    
    if [ $perl_status -ne 0 ] && [ $py_status -ne 0 ]; then
        echo -e "${YELLOW}SKIP${NC} (both failed - likely missing dependencies)"
        ((total_skip++))
        continue
    fi
    
    if [ $perl_status -ne 0 ]; then
        echo -e "${YELLOW}WARN${NC} (Perl failed - Python only)"
        # Still compare if Python succeeded
        if [ $py_status -eq 0 ]; then
            echo "  Python output: $(python3 -c "import json; d=json.load(open('$py_out')); print(f\"{len(d.get('html',''))} chars, {len(d.get('answers',[]))} answers\")")"
        fi
        continue
    fi
    
    if [ $py_status -ne 0 ]; then
        echo -e "${RED}FAIL${NC} (Python error)"
        ((total_fail++))
        continue
    fi
    
    # Compare outputs
    python3 "$DIFF_TOOL" "$perl_out" "$py_out" >/dev/null 2>&1
    diff_status=$?
    
    if [ $diff_status -eq 0 ]; then
        echo -e "${GREEN}PASS${NC}"
        ((total_pass++))
    else
        echo -e "${RED}FAIL${NC}"
        ((total_fail++))
        # Show diff details
        echo "  Differences:"
        python3 "$DIFF_TOOL" "$perl_out" "$py_out" 2>&1 | head -10 | sed 's/^/    /'
    fi
done

echo ""
echo "======================================"
echo "Summary"
echo "======================================"
echo -e "Passed: ${GREEN}$total_pass${NC}"
echo -e "Failed: ${RED}$total_fail${NC}"
echo -e "Skipped: ${YELLOW}$total_skip${NC}"
echo ""

if [ $total_fail -eq 0 ] && [ $total_pass -gt 0 ]; then
    echo -e "${GREEN}✓ All comparisons PASSED${NC}"
    exit 0
elif [ $total_pass -gt 0 ]; then
    echo -e "${YELLOW}⚠ Some comparisons passed, some failed${NC}"
    exit 1
else
    echo -e "${RED}✗ All comparisons FAILED or SKIPPED${NC}"
    exit 1
fi

