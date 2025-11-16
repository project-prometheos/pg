## DESCRIPTION
## Fraction answer
## ENDDESCRIPTION
## DBsubject(WeBWorK)
## DBchapter(WeBWorK tutorial)
## DBsection(PGML tutorial 2015)
## Date(06/01/2015)
## Institution(Hope College)
## Author(Paul Pearson)
## MO(1)
## KEYWORDS('algebra', 'fraction answer')
#:% name = Fraction Answer
#:% type = Sample
#:% subject = PerlList([algebra, precalculus])
#:% categories = PerlList([fraction])
#:% section = preamble
#: The macro `contextFraction.pl` must be loaded.
from pg.mathobjects import *
from pg.course import *
from pg.pgml import *
from pg.standard import *
from pg.math.fraction import Fraction
# Loaded: PGstandard.pl, PGML.pl, contextFraction.pl, PGcourse.pl

DOCUMENT()
#:% section = setup
#: The PODLINK('contextFraction.pl') macro provides four contexts:
#:
#: ```{#contexts .perl}
#: Context('Fraction');
#: Context('Fraction-NoDecimals');
#: Context('LimitedFraction');
#: Context('LimitedProperFraction');
#: ```
#:
#: See PODLINK('contextFraction.pl') for the differences between these contexts.
Context('Fraction-NoDecimals')
answer = Compute('3/2')
#:% section = statement
#: There are many context flags that control how fraction answers are checked.
#: See the documentation for the PODLINK('contextFraction.pl') macro for more
#: details.
PGML_BLOCK_0 = '''
Simplify = {}
Simplify [``\\frac{6}{4}``].

Answer = [_]{answer.cmp(
    studentsMustReduceFractions = 1,
    reduceFractions = 1,
    allowMixedNumbers = 0
)}{15}
'''
TEXT(PGML(PGML_BLOCK_0))
#:% section = solution
PGML_BLOCK_1 = '''
Factor and cancel to obtain [`\\displaystyle [$answer]`].
'''
SOLUTION(PGML(PGML_BLOCK_1))
ENDDOCUMENT()

if __name__ == "__main__":
    """Execute problem and display results."""
    from pg.macros.core.pg_core import get_environment
    
    env = get_environment()
    if env:
        print("=" * 80)
        print("PROBLEM STATEMENT")
        print("=" * 80)
        print(''.join(env.output_array))
        
        if env.solution_array:
            print("\n" + "=" * 80)
            print("SOLUTION")
            print("=" * 80)
            print(''.join(env.solution_array))
        
        if env.hint_array:
            print("\n" + "=" * 80)
            print("HINT")
            print("=" * 80)
            print(''.join(env.hint_array))
        
        print("\n" + "=" * 80)
        print(f"ANSWERS: {len(env.answers_hash)} answer blank(s)")
        print("=" * 80)
        for name in sorted(env.answers_hash.keys()):
            print(f"  {name}")
