#!/bin/bash
# Setup Perl environment for parity testing
# Source this file before running tests: source parity_lab/setup_perl_env.sh

# Setup local::lib if modules are installed there
if [ -d "$HOME/perl5/lib/perl5" ]; then
    eval $(perl -I ~/perl5/lib/perl5/ -Mlocal::lib 2>/dev/null)
    export PERL5LIB="$HOME/perl5/lib/perl5:$PERL5LIB"
    echo "✓ Perl local::lib environment configured"
fi

