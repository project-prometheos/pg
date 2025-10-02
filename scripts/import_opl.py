#!/usr/bin/env python3
"""Import problems from Open Problem Library (OPL).

This script imports WeBWorK problems from the OPL, which uses a different
metadata format than the tutorial problems.
"""

import json
import re
import sqlite3
import sys
from pathlib import Path
from typing import Dict, Any, Optional, List


class OPLImporter:
    """Import problems from Open Problem Library."""
    
    def __init__(self, db_path: str = "problems.db"):
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None
        
    def extract_metadata(self, content: str) -> Dict[str, Any]:
        """Extract OPL-style metadata from PG file content."""
        metadata = {
            'description': '',
            'db_subject': '',
            'db_chapter': '',
            'db_section': '',
            'date': '',
            'institution': '',
            'author': '',
            'mlt': '',
            'level': '',
            'keywords': [],
            'macros': []
        }
        
        # Extract DESCRIPTION block
        desc_match = re.search(
            r'##\s*DESCRIPTION\s*\n(.*?)\n##\s*ENDDESCRIPTION',
            content,
            re.DOTALL | re.IGNORECASE
        )
        if desc_match:
            desc = desc_match.group(1).strip()
            # Remove leading ## from description lines
            desc = '\n'.join(line.lstrip('#').strip() for line in desc.split('\n'))
            metadata['description'] = desc
        
        # Extract single-line metadata tags
        tags = {
            'DBsubject': 'db_subject',
            'DBchapter': 'db_chapter',
            'DBsection': 'db_section',
            'Date': 'date',
            'Institution': 'institution',
            'Author': 'author',
            'MLT': 'mlt',
            'Level': 'level'
        }
        
        for tag, key in tags.items():
            pattern = rf'##\s*{tag}\((.*?)\)'
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                metadata[key] = match.group(1).strip()
        
        # Extract KEYWORDS
        keywords_match = re.search(
            r"##\s*KEYWORDS\(['\"](.+?)['\"]\)",
            content,
            re.IGNORECASE
        )
        if keywords_match:
            keywords_str = keywords_match.group(1)
            # Split by comma and clean up
            metadata['keywords'] = [
                k.strip().strip("'\"").lower() 
                for k in re.split(r'[,\']', keywords_str)
                if k.strip() and k.strip() not in ["'", '"', ',']
            ]
        
        # Extract macros (loadMacros)
        macros_match = re.search(
            r'loadMacros\((.*?)\);',
            content,
            re.DOTALL
        )
        if macros_match:
            macros_str = macros_match.group(1)
            # Extract quoted strings
            macro_files = re.findall(r'["\']([^"\']+\.pl)["\']', macros_str)
            metadata['macros'] = macro_files
        
        return metadata
    
    def categorize_problem(self, metadata: Dict[str, Any]) -> Dict[str, List[str]]:
        """Categorize problem based on OPL metadata."""
        categories = {
            'subjects': [],
            'categories': [],
            'types': ['sample']
        }
        
        # Map DBsubject to our subject taxonomy
        subject_map = {
            'calculus': 'calculus',
            'algebra': 'algebra',
            'precalculus': 'algebra',
            'trigonometry': 'trigonometry',
            'statistics': 'statistics',
            'probability': 'statistics',
            'linear algebra': 'linear-algebra',
            'differential equations': 'differential-equations',
            'discrete mathematics': 'discrete-math',
            'geometry': 'geometry',
            'complex analysis': 'complex-analysis',
            'number theory': 'number-theory'
        }
        
        db_subject = metadata.get('db_subject', '').lower()
        for key, value in subject_map.items():
            if key in db_subject:
                categories['subjects'].append(value)
                break
        
        # Extract categories from chapter/section
        chapter = metadata.get('db_chapter', '').lower()
        section = metadata.get('db_section', '').lower()
        
        for text in [chapter, section]:
            if text:
                # Clean up and extract key terms
                terms = re.findall(r'\b[a-z]+\b', text)
                categories['categories'].extend([
                    t for t in terms 
                    if len(t) > 3 and t not in ['the', 'and', 'for', 'with']
                ])
        
        # Remove duplicates
        categories['categories'] = list(set(categories['categories']))
        
        return categories
    
    def init_database(self):
        """Initialize or connect to existing database."""
        if not self.db_path.exists():
            print(f"[X] Database not found: {self.db_path}")
            print("    Run 'python scripts/import_problems.py' first to create the database")
            sys.exit(1)
        
        self.conn = sqlite3.connect(str(self.db_path))
        print(f"[OK] Connected to database: {self.db_path.absolute()}")
    
    def import_directory(
        self, 
        opl_path: Path, 
        collection_name: str = "OPL",
        limit: Optional[int] = None
    ) -> int:
        """Import problems from OPL directory."""
        
        print(f"\n[>>] Scanning OPL directory: {opl_path}")
        
        if not opl_path.exists():
            print(f"[X] Directory not found: {opl_path}")
            return 0
        
        # Find all .pg files
        pg_files = list(opl_path.rglob("*.pg"))
        total_files = len(pg_files)
        
        if limit:
            pg_files = pg_files[:limit]
            print(f"[>>] Found {total_files} PG files (importing first {limit})")
        else:
            print(f"[>>] Found {total_files} PG files")
        
        if total_files == 0:
            print("[!] No .pg files found in directory")
            return 0
        
        # Determine collection name from path
        if collection_name == "OPL":
            # Try to extract institution name from path
            parts = opl_path.parts
            if 'OpenProblemLibrary' in parts:
                idx = parts.index('OpenProblemLibrary')
                if idx + 1 < len(parts):
                    collection_name = f"OPL-{parts[idx + 1]}"
        
        # Register collection
        try:
            self.conn.execute("""
                INSERT OR IGNORE INTO collections (id, name, description, problem_count)
                VALUES (?, ?, ?, 0)
            """, (
                collection_name,
                collection_name,
                f"Problems from {opl_path.name}"
            ))
            self.conn.commit()
        except Exception as e:
            print(f"[!] Warning: Could not register collection: {e}")
        
        # Import problems
        count = 0
        skipped = 0
        errors = 0
        
        print(f"\n[>>] Importing into collection: {collection_name}")
        print("-" * 60)
        
        for i, pg_file in enumerate(pg_files, 1):
            try:
                # Read file
                with open(pg_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                
                # Extract metadata
                metadata = self.extract_metadata(content)
                categories = self.categorize_problem(metadata)
                
                # Generate problem ID
                try:
                    relative_path = pg_file.relative_to(opl_path)
                except ValueError:
                    # If not relative to opl_path, use full stem
                    relative_path = pg_file
                
                problem_id = str(relative_path).replace('\\', '/').replace('.pg', '')
                
                # Create metadata JSON
                metadata_json = json.dumps({
                    'types': categories['types'],
                    'subjects': categories['subjects'],
                    'categories': categories['categories'],
                    'keywords': metadata['keywords'],
                    'macros': metadata['macros'],
                    'db_subject': metadata['db_subject'],
                    'db_chapter': metadata['db_chapter'],
                    'db_section': metadata['db_section'],
                    'institution': metadata['institution'],
                    'author': metadata['author'],
                    'level': metadata['level'],
                    'date': metadata['date']
                })
                
                # Generate display name
                name = metadata['db_section'] or metadata['db_chapter'] or pg_file.stem
                name = name.replace('_', ' ').replace('-', ' ').strip()
                
                # Insert into database
                self.conn.execute("""
                    INSERT OR REPLACE INTO problems 
                    (id, name, description, pg_source, file_path, source_collection, metadata)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    problem_id,
                    name,
                    metadata['description'][:500],  # Truncate long descriptions
                    content,
                    str(pg_file),
                    collection_name,
                    metadata_json
                ))
                
                count += 1
                
                # Progress indicator
                if count % 10 == 0:
                    print(f"  [{i}/{len(pg_files)}] Imported {count} problems...", end='\r')
                
            except sqlite3.IntegrityError:
                skipped += 1
            except Exception as e:
                errors += 1
                if errors <= 5:  # Show first 5 errors
                    print(f"\n  [X] Error with {pg_file.name}: {e}")
        
        # Commit all changes
        self.conn.commit()
        
        # Update collection count
        self.conn.execute("""
            UPDATE collections 
            SET problem_count = (SELECT COUNT(*) FROM problems WHERE source_collection = ?)
            WHERE id = ?
        """, (collection_name, collection_name))
        self.conn.commit()
        
        # Show summary
        print(f"\n{'-' * 60}")
        print(f"[OK] Imported {count} problems from {opl_path.name}")
        if skipped > 0:
            print(f"[!] Skipped {skipped} duplicate problems")
        if errors > 0:
            print(f"[!] {errors} errors encountered")
        
        return count
    
    def show_stats(self):
        """Show database statistics."""
        print("\n[>>] DATABASE STATISTICS")
        print("=" * 60)
        
        # Collection stats
        cursor = self.conn.execute("""
            SELECT source_collection, COUNT(*) as count
            FROM problems
            GROUP BY source_collection
            ORDER BY count DESC
        """)
        
        print("\n[>>] Collections:")
        for row in cursor:
            print(f"     {row[0]:<30} {row[1]:>6} problems")
        
        # Total
        cursor = self.conn.execute("SELECT COUNT(*) FROM problems")
        total = cursor.fetchone()[0]
        print(f"\n     {'Total':<30} {total:>6} problems")
        
        # Subject distribution
        print("\n[>>] Top Subjects:")
        cursor = self.conn.execute("""
            SELECT json_each.value as subject, COUNT(*) as count
            FROM problems, json_each(metadata, '$.subjects')
            WHERE json_each.value IS NOT NULL AND json_each.value != ''
            GROUP BY subject
            ORDER BY count DESC
            LIMIT 10
        """)
        
        for row in cursor:
            if row[0]:
                print(f"     {row[0]:<30} {row[1]:>6} problems")
    
    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    """Main import process."""
    if len(sys.argv) < 2:
        print("Usage: python scripts/import_opl.py <opl_directory> [collection_name] [--limit N]")
        print()
        print("Examples:")
        print("  python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/FortLewis")
        print("  python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope --limit 50")
        print("  python scripts/import_opl.py opl/OpenProblemLibrary/TCNJ OPL-TCNJ")
        sys.exit(1)
    
    opl_path = Path(sys.argv[1])
    collection_name = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith('--') else "OPL"
    
    # Check for limit flag
    limit = None
    if '--limit' in sys.argv:
        limit_idx = sys.argv.index('--limit')
        if limit_idx + 1 < len(sys.argv):
            try:
                limit = int(sys.argv[limit_idx + 1])
            except ValueError:
                print(f"⚠️  Invalid limit value: {sys.argv[limit_idx + 1]}")
    
    print("WeBWorK OPL Import")
    print("=" * 60)
    
    importer = OPLImporter()
    
    try:
        importer.init_database()
        count = importer.import_directory(opl_path, collection_name, limit)
        
        if count > 0:
            importer.show_stats()
            print("\n[OK] Import completed successfully!")
        else:
            print("\n[!] No problems imported")
        
    except KeyboardInterrupt:
        print("\n\n[!] Import cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[X] Import failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        importer.close()


if __name__ == "__main__":
    main()

