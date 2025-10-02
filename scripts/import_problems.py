#!/usr/bin/env python3
"""Import WeBWorK problems into SQLite database.

This script:
1. Parses PG files to extract metadata (pure Python)
2. Reads PG files
3. Imports everything into SQLite database
"""

import json
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Any, List

from pg_parser import PGParser


class ProblemImporter:
    """Import WeBWorK problems into SQLite database."""
    
    def __init__(self, db_path: str = "problems.db"):
        self.db_path = Path(db_path)
        self.conn: sqlite3.Connection = None
        self.problems_dir = Path("tutorial/sample-problems")
        
    def parse_problems(self, problems_dir: Path = None) -> Dict[str, Any]:
        """Parse PG files to extract metadata."""
        if problems_dir is None:
            problems_dir = self.problems_dir
            
        print("Parsing PG files to extract metadata...")
        
        metadata = PGParser.generate_metadata(problems_dir)
        
        print(f"Found {len(metadata)} problems")
        
        return metadata
    
    def init_database(self):
        """Initialize SQLite database with schema."""
        print("Initializing database...")
        
        # Read schema
        schema_path = Path("scripts/schema.sql")
        if not schema_path.exists():
            print(f"[ERROR] Schema file not found: {schema_path}")
            sys.exit(1)
        
        with open(schema_path, "r") as f:
            schema = f.read()
        
        # Create database
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.executescript(schema)
        self.conn.commit()
        
        print(f"[OK] Database initialized: {self.db_path.absolute()}")
    
    def import_problems(self, metadata: Dict[str, Any], collection: str = "tutorial") -> int:
        """Import problems into database."""
        print(f"\nImporting problems from collection: {collection}")
        
        count = 0
        skipped = 0
        
        for filename, meta in metadata.items():
            # Construct file path
            problem_dir = self.problems_dir / meta.get('dir', '')
            pg_file = problem_dir / filename
            
            if not pg_file.exists():
                print(f"  [WARN] Skipping {filename} (file not found)")
                skipped += 1
                continue
            
            # Read PG source
            with open(pg_file, 'r', encoding='utf-8') as f:
                pg_source = f.read()
            
            # Generate problem ID
            problem_id = f"{meta.get('dir', '')}/{filename}".replace('.pg', '')
            
            # Prepare metadata JSON
            metadata_json = json.dumps({
                'types': meta.get('types', []),
                'subjects': meta.get('subjects', []),
                'categories': meta.get('categories', []),
                'keywords': [k.lower() for k in meta.get('keywords', [])],
                'macros': meta.get('macros', []),
                'related': meta.get('related', []),
                'db_subjects': meta.get('DBsubject', []),
                'db_chapter': meta.get('DBchapter', []),
                'db_section': meta.get('DBsection', [])
            })
            
            # Insert into database
            try:
                # Just use the file path as-is, not relative
                file_path_str = str(pg_file).replace('\\', '/')
                
                self.conn.execute("""
                    INSERT INTO problems (id, name, description, pg_source, file_path, 
                                         source_collection, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    problem_id,
                    meta.get('name', filename),
                    meta.get('description', ''),
                    pg_source,
                    file_path_str,
                    collection,
                    metadata_json
                ))
                
                count += 1
                print(f"  [OK] {meta.get('name', filename)}")
                
            except sqlite3.IntegrityError as e:
                print(f"  [WARN] Duplicate: {filename}")
                skipped += 1
            except Exception as e:
                print(f"  [ERROR] Error importing {filename}: {e}")
                skipped += 1
        
        self.conn.commit()
        
        # Update collection count
        self.conn.execute("""
            UPDATE collections 
            SET problem_count = (SELECT COUNT(*) FROM problems WHERE source_collection = ?)
            WHERE id = ?
        """, (collection, collection))
        self.conn.commit()
        
        print(f"\n[OK] Imported {count} problems")
        if skipped > 0:
            print(f"[WARN] Skipped {skipped} problems")
        
        return count
    
    def show_stats(self):
        """Show database statistics."""
        print("\nDatabase Statistics")
        print("=" * 50)
        
        cursor = self.conn.execute("""
            SELECT source_collection, COUNT(*) as count
            FROM problems
            GROUP BY source_collection
        """)
        
        for row in cursor:
            print(f"  {row[0]}: {row[1]} problems")
        
        cursor = self.conn.execute("SELECT COUNT(*) FROM problems")
        total = cursor.fetchone()[0]
        print(f"\n  Total: {total} problems")
        
        # Show subject distribution
        print("\nSubject Distribution (top 10)")
        cursor = self.conn.execute("""
            SELECT json_each.value as subject, COUNT(*) as count
            FROM problems, json_each(metadata, '$.subjects')
            GROUP BY subject
            ORDER BY count DESC
            LIMIT 10
        """)
        
        for row in cursor:
            print(f"  {row[0]}: {row[1]} problems")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    """Main import process."""
    print("WeBWorK Problem Database Import")
    print("=" * 50)
    print()
    
    # Parse arguments
    db_path = sys.argv[1] if len(sys.argv) > 1 else "problems.db"
    
    importer = ProblemImporter(db_path)
    
    try:
        # Step 1: Initialize database
        importer.init_database()
        
        # Step 2: Parse PG files
        metadata = importer.parse_problems()
        
        # Step 3: Import problems
        count = importer.import_problems(metadata, collection="tutorial")
        
        # Step 4: Show statistics
        importer.show_stats()
        
        print("\n[SUCCESS] Import completed successfully!")
        print(f"Database: {importer.db_path.absolute()}")
        print("\nNext steps:")
        print("  1. Start backend: cd apps/backend && uvicorn app.main:app --reload")
        print("  2. Search API: http://localhost:8000/api/problems/search?q=calculus")
        
    except KeyboardInterrupt:
        print("\n\n[WARN] Import cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        importer.close()


if __name__ == "__main__":
    main()
