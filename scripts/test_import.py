#!/usr/bin/env python3
"""Test the OPL import system with tutorial problems."""

import sqlite3
import sys
from pathlib import Path


def test_import():
    """Test that import system is working."""
    print("=" * 60)
    print("Testing WeBWorK Import System")
    print("=" * 60)
    
    # Check database exists
    db_path = Path("problems.db")
    if not db_path.exists():
        print("\n[X] Database not found!")
        print("    Run: python scripts/import_problems.py")
        return False
    
    print(f"\n[OK] Database found: {db_path.absolute()}")
    
    # Connect and check schema
    conn = sqlite3.connect(str(db_path))
    
    # Check tables
    cursor = conn.execute("""
        SELECT name FROM sqlite_master 
        WHERE type='table' 
        ORDER BY name
    """)
    tables = [row[0] for row in cursor.fetchall()]
    
    expected_tables = ['collections', 'problems']
    missing_tables = [t for t in expected_tables if t not in tables]
    
    if missing_tables:
        print(f"\n[X] Missing tables: {missing_tables}")
        return False
    
    print(f"[OK] Database schema valid")
    print(f"     Tables: {', '.join(tables)}")
    
    # Check problems
    cursor = conn.execute("SELECT COUNT(*) FROM problems")
    problem_count = cursor.fetchone()[0]
    
    print(f"\n[>>] Current database status:")
    print(f"     Total problems: {problem_count}")
    
    if problem_count == 0:
        print("\n[!] No problems in database yet")
        print("    This is OK for a fresh install")
    else:
        # Show collections
        cursor = conn.execute("""
            SELECT source_collection, COUNT(*) as count
            FROM problems
            GROUP BY source_collection
            ORDER BY count DESC
        """)
        
        print(f"\n[>>] Collections:")
        for row in cursor:
            print(f"     - {row[0]}: {row[1]} problems")
        
        # Show subjects
        cursor = conn.execute("""
            SELECT json_each.value as subject, COUNT(*) as count
            FROM problems, json_each(metadata, '$.subjects')
            WHERE json_each.value IS NOT NULL AND json_each.value != ''
            GROUP BY subject
            ORDER BY count DESC
            LIMIT 5
        """)
        
        subjects = cursor.fetchall()
        if subjects:
            print(f"\n[>>] Top subjects:")
            for row in subjects:
                print(f"     - {row[0]}: {row[1]} problems")
    
    # Test search functionality
    print(f"\n[>>] Testing search...")
    cursor = conn.execute("""
        SELECT id, name 
        FROM problems 
        WHERE pg_source LIKE '%calculus%' 
           OR name LIKE '%calculus%'
           OR description LIKE '%calculus%'
        LIMIT 3
    """)
    
    results = cursor.fetchall()
    if results:
        print(f"     Found {len(results)} calculus problems:")
        for row in results:
            print(f"     - {row[0]}: {row[1]}")
    else:
        print(f"     No calculus problems found (this is OK)")
    
    conn.close()
    
    # Check import scripts
    print(f"\n[>>] Checking import scripts:")
    
    scripts = {
        'import_problems.py': 'Import tutorial problems',
        'import_opl.py': 'Import from OPL',
        'bootstrap_opl.py': 'Automated OPL import'
    }
    
    for script, desc in scripts.items():
        script_path = Path('scripts') / script
        if script_path.exists():
            print(f"     [OK] {script:<25} {desc}")
        else:
            print(f"     [X] {script:<25} MISSING!")
    
    # Summary
    print("\n" + "=" * 60)
    print("[OK] Import system is ready!")
    print("=" * 60)
    
    print("\n[>>] Next steps:")
    print()
    print("     1. Import tutorial problems (if not done):")
    print("        python scripts/import_problems.py")
    print()
    print("     2. Import OPL problems:")
    print("        python scripts/bootstrap_opl.py")
    print()
    print("     3. Or import specific collection:")
    print("        git clone --depth 1 https://github.com/openwebwork/webwork-open-problem-library.git")
    print("        python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Hope")
    print()
    print("     4. Start the backend:")
    print("        cd apps/backend")
    print("        python -m uvicorn app.main:app --reload")
    print()
    
    return True


if __name__ == "__main__":
    try:
        success = test_import()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n[X] Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

