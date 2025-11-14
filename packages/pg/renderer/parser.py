"""Parse PG files into structured format."""

import re
from typing import List
from dataclasses import dataclass


@dataclass
class PGProblem:
    """Parsed PG problem structure."""
    setup: str          # Code before BEGIN_PGML
    pgml: str           # Content between BEGIN_PGML...END_PGML
    solution: str       # Content in solution section (if any)
    macros: List[str]   # Loaded macro files


class PGParser:
    """Parse PG files into structured format."""
    
    def parse(self, pg_source: str) -> PGProblem:
        """Parse PG file into sections."""
        
        # Extract loadMacros
        macros = self._extract_macros(pg_source)
        
        # Extract PGML section
        pgml_match = re.search(
            r'BEGIN_PGML\s*\n(.*?)\nEND_PGML',
            pg_source,
            re.DOTALL
        )
        pgml = pgml_match.group(1) if pgml_match else ""
        
        # Extract setup (everything before BEGIN_PGML)
        if pgml_match:
            setup = pg_source[:pgml_match.start()]
        else:
            setup = pg_source
        
        # Extract solution (optional)
        solution_match = re.search(
            r'BEGIN_PGML_SOLUTION\s*\n(.*?)\nEND_PGML_SOLUTION',
            pg_source,
            re.DOTALL
        )
        solution = solution_match.group(1) if solution_match else ""
        
        return PGProblem(
            setup=setup,
            pgml=pgml,
            solution=solution,
            macros=macros
        )
    
    def _extract_macros(self, pg_source: str) -> List[str]:
        """Extract macro files from loadMacros()."""
        match = re.search(r'loadMacros\((.*?)\);', pg_source, re.DOTALL)
        if not match:
            return []
        
        macro_list = match.group(1)
        # Extract quoted strings
        return re.findall(r'["\']([^"\']+)["\']', macro_list)

