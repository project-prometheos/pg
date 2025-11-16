#!/bin/bash
################################################################################
# Install Perl WeBWorK Libraries for Parity Testing
################################################################################

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "======================================"
echo "Installing Perl WeBWorK Libraries"
echo "======================================"
echo ""

# Check Perl version
echo "Checking Perl version..."
perl --version | head -2
PERL_VERSION=$(perl -e 'print $^V' | sed 's/v//')
echo "Perl version: $PERL_VERSION"
echo ""

# Check if cpanm is installed
if ! command -v cpanm &> /dev/null; then
    echo "cpanminus (cpanm) not found. Installing..."
    
    if command -v apt-get &> /dev/null; then
        echo "Installing via apt-get..."
        sudo apt-get update
        sudo apt-get install -y cpanminus
    elif command -v brew &> /dev/null; then
        echo "Installing via Homebrew..."
        brew install cpanminus
    else
        echo "Installing via curl..."
        curl -L https://cpanmin.us | perl - --sudo App::cpanminus
    fi
    
    if ! command -v cpanm &> /dev/null; then
        echo "ERROR: Failed to install cpanm"
        exit 1
    fi
    echo "✓ cpanm installed"
else
    echo "✓ cpanm already installed"
fi
echo ""

# Install Perl dependencies from cpanfile
echo "Installing Perl dependencies from cpanfile..."
cd "$REPO_ROOT"

if [ -f "cpanfile" ]; then
    echo "Found cpanfile, installing dependencies..."
    cpanm --installdeps . --notest
    echo "✓ Dependencies installed"
else
    echo "WARNING: cpanfile not found"
fi
echo ""

# Check for macros directory
echo "Checking for macros directory..."
if [ -d "$REPO_ROOT/macros" ]; then
    echo "✓ macros/ directory found"
    MACRO_COUNT=$(find "$REPO_ROOT/macros" -name "*.pl" | wc -l)
    echo "  Found $MACRO_COUNT macro files"
else
    echo "WARNING: macros/ directory not found"
fi
echo ""

# Test Perl adapter
echo "Testing Perl adapter..."
cd "$SCRIPT_DIR"
TEST_SNIPPET="tests/snippets/standard_basic.pg"
if [ -f "$TEST_SNIPPET" ]; then
    perl perl_ref/run_pg_snippet.pl "$TEST_SNIPPET" 42 /tmp/test_perl_install.json 2>&1 | tail -5
    if [ $? -eq 0 ]; then
        echo "✓ Perl adapter working"
    else
        echo "⚠ Perl adapter has issues (may still work with minimal environment)"
    fi
else
    echo "⚠ Test snippet not found, skipping adapter test"
fi
echo ""

# Summary
echo "======================================"
echo "Installation Summary"
echo "======================================"
echo ""
echo "Next steps:"
echo "1. Run parity tests: pytest parity_lab/tests/contract/test_parity_comparison.py -v"
echo "2. Check if Perl comparisons are working"
echo "3. Review INSTALL_PERL_LIBS.md for troubleshooting"
echo ""

