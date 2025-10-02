"""Deterministic random number generator for PG problems."""

import random
from typing import List, Any


class PGRandom:
    """
    Deterministic random number generator for PG problems.
    Mimics Perl's PG_random_generator behavior.
    """
    
    def __init__(self, seed: int = 0):
        self.rng = random.Random(seed)
    
    def random(self, min_val: float, max_val: float, step: float = 1) -> float:
        """
        Return random value in [min, max] with given step.
        
        Mimics: random(1, 5, 1) → one of [1, 2, 3, 4, 5]
        """
        if step == 0:
            return self.rng.uniform(min_val, max_val)
        
        num_steps = int((max_val - min_val) / step) + 1
        return min_val + self.rng.randrange(num_steps) * step
    
    def non_zero_random(self, min_val: float, max_val: float, step: float = 1) -> float:
        """Random value excluding zero."""
        val = self.random(min_val, max_val, step)
        while val == 0:
            val = self.random(min_val, max_val, step)
        return val
    
    def list_random(self, items: List[Any]) -> Any:
        """Pick random element from list."""
        return self.rng.choice(items)

