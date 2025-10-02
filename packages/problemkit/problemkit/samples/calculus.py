"""Sample calculus problem demonstrating the authoring API."""
from __future__ import annotations

from sympy import Symbol, diff, latex, simplify

from ..decorators import problem
from ..models import InputSpec, ProblemInstance
from ..rng import RNG


@problem(id="calc.product_rule.v1", vars=["x"], tags=["calculus", "derivative"])
def product_rule(*, seed: int, rng: RNG) -> ProblemInstance:
    x = Symbol("x")
    coefficient = rng.randint(1, 5)
    exponent = rng.randint(2, 6)
    expression = (coefficient * x + 1) * x**exponent
    derivative = simplify(diff(expression, x))

    return ProblemInstance(
        statement_tex=(
            "Compute $\\frac{d}{dx}\\left((%s x + 1) x^{%s}\\right)$." % (coefficient, exponent)
        ),
        inputs=[InputSpec(name="ans", type="math", label="Answer")],
        answers={"ans": str(derivative)},
        solution_tex=f"The derivative is ${latex(derivative)}$.",
        meta={"source": "sample"},
    )
