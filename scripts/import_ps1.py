#!/usr/bin/env python3
"""Import webwork_ps1_pg problems into SQLite database."""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Any, List

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from pg_parser import PGParser


class PS1Importer:
    """Import WeBWorK PS1 problems into SQLite database."""

    def __init__(self, db_path: str = "problems.db"):
        self.db_path = Path(db_path)
        self.conn: sqlite3.Connection = None
        self.problems_dir = Path("webwork_ps1_pg")

    def connect_db(self):
        """Connect to existing database."""
        if not self.db_path.exists():
            print(f"[ERROR] Database not found: {self.db_path}")
            print("Run: python scripts/import_problems.py first")
            sys.exit(1)

        self.conn = sqlite3.connect(str(self.db_path))
        print(f"[OK] Connected to database: {self.db_path.absolute()}")

    def add_collection(self):
        """Add PS1 collection if it doesn't exist."""
        self.conn.execute("""
            INSERT OR IGNORE INTO collections (id, name, description, problem_count)
            VALUES (?, ?, ?, ?)
        """, (
            "ps1",
            "Problem Set 1",
            "Swedish mathematics problem set covering trigonometry and calculus",
            0
        ))
        self.conn.commit()
        print("[OK] PS1 collection added/verified")

    def import_problems(self) -> int:
        """Import PS1 problems into database."""
        print(f"\nImporting problems from: {self.problems_dir}")

        # Find all .pg files
        pg_files = sorted(self.problems_dir.glob("*.pg"))

        if not pg_files:
            print(f"[ERROR] No .pg files found in {self.problems_dir}")
            return 0

        print(f"Found {len(pg_files)} .pg files")

        count = 0
        skipped = 0

        for pg_file in pg_files:
            # Read PG source
            with open(pg_file, 'r', encoding='utf-8') as f:
                pg_source = f.read()

            # Generate problem ID and name
            problem_num = pg_file.stem.replace('ps1-prob', '')
            problem_id = f"PS1/Problem-{problem_num}"
            problem_name = f"PS1 Problem {problem_num}"

            # Extract description from PGML if possible
            description = self._extract_description(pg_source)

            # Prepare metadata JSON
            metadata_json = json.dumps({
                'types': ['problem set', 'exercise'],
                'subjects': ['mathematics', 'calculus', 'trigonometry'],
                'categories': ['problem set 1'],
                'keywords': ['ps1', 'swedish', 'mathematics'],
                'macros': self._extract_macros(pg_source),
                'related': [],
                'db_subjects': ['Mathematics'],
                'db_chapter': ['Problem Set 1'],
                'db_section': []
            })

            # Insert into database
            try:
                file_path_str = str(pg_file).replace('\\', '/')

                self.conn.execute("""
                    INSERT OR REPLACE INTO problems (id, name, description, pg_source, file_path,
                                         source_collection, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    problem_id,
                    problem_name,
                    description,
                    pg_source,
                    file_path_str,
                    "ps1",
                    metadata_json
                ))

                count += 1
                print(f"  [OK] {problem_name}: {description[:60]}...")

            except Exception as e:
                print(f"  [ERROR] Error importing {pg_file.name}: {e}")
                skipped += 1

        self.conn.commit()

        # Update collection count
        self.conn.execute("""
            UPDATE collections
            SET problem_count = (SELECT COUNT(*) FROM problems WHERE source_collection = ?)
            WHERE id = ?
        """, ("ps1", "ps1"))
        self.conn.commit()

        print(f"\n[OK] Imported {count} problems")
        if skipped > 0:
            print(f"[WARN] Skipped {skipped} problems")

        return count

    def _extract_description(self, pg_source: str) -> str:
        """Extract problem description from PGML."""
        import re

        # Look for BEGIN_PGML...END_PGML block
        match = re.search(r'BEGIN_PGML\s+(.*?)\s+END_PGML', pg_source, re.DOTALL)
        if not match:
            return "Swedish mathematics problem"

        pgml = match.group(1).strip()

        # Extract first line or paragraph
        lines = pgml.split('\n')
        for line in lines:
            line = line.strip()
            if line and not line.startswith('[') and not line.startswith('#'):
                # Remove LaTeX and formatting
                line = re.sub(r'\\\(.*?\\\)', '', line)
                line = re.sub(r'\$.*?\$', '', line)
                line = re.sub(r'\*\*Problem \d+\.\*\*', '', line)
                line = line.strip()
                if line:
                    return line[:200]  # Truncate to 200 chars

        return "Swedish mathematics problem"

    def _extract_macros(self, pg_source: str) -> List[str]:
        """Extract macros from loadMacros call."""
        import re

        match = re.search(r'loadMacros\((.*?)\)', pg_source)
        if not match:
            return []

        macros_str = match.group(1)
        # Extract quoted strings
        macros = re.findall(r'["\']([^"\']+)["\']', macros_str)
        return macros

    def show_stats(self):
        """Show database statistics."""
        print("\nDatabase Statistics")
        print("=" * 50)

        cursor = self.conn.execute("""
            SELECT source_collection, COUNT(*) as count
            FROM problems
            GROUP BY source_collection
            ORDER BY count DESC
        """)

        for row in cursor:
            print(f"  {row[0]}: {row[1]} problems")

        cursor = self.conn.execute("SELECT COUNT(*) FROM problems")
        total = cursor.fetchone()[0]
        print(f"\nTotal: {total} problems")


def main():
    """Main entry point."""
    print("WeBWorK PS1 Problem Importer")
    print("=" * 50)

    importer = PS1Importer()
    importer.connect_db()
    importer.add_collection()
    importer.import_problems()
    importer.show_stats()

    print("\n[DONE] Import complete!")
    print("Run: pnpm dev (to start the web server)")


if __name__ == "__main__":
    main()
