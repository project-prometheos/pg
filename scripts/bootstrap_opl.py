#!/usr/bin/env python3
"""Bootstrap script to clone OPL and import Tier 1 collections.

This script automates the process of:
1. Cloning the Open Problem Library
2. Importing high-quality Tier 1 collections
3. Setting up the problem database
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list, description: str, check=True):
    """Run a command and show progress."""
    print(f"\n{'-' * 60}")
    print(f"> {description}")
    print(f"{'-' * 60}")
    
    result = subprocess.run(cmd, check=False)
    
    if result.returncode != 0 and check:
        print(f"\n[X] Failed: {description}")
        sys.exit(1)
    
    return result.returncode == 0


def main():
    """Main bootstrap process."""
    print("=" * 60)
    print("WeBWorK OPL Bootstrap")
    print("Cloning and importing Tier 1 problem collections")
    print("=" * 60)
    
    # Configuration
    opl_dir = Path("webwork-open-problem-library")
    tier1_collections = [
        ("FortLewis", "Modern PGML, well-documented"),
        ("Hope", "Excellent examples, documented"),
        ("TCNJ", "High quality, diverse subjects"),
        ("UBC", "Modern, well-tested"),
    ]
    
    # Step 1: Check if database exists
    if not Path("problems.db").exists():
        print("\n[!] Database not found. Creating initial database...")
        run_command(
            [sys.executable, "scripts/import_problems.py"],
            "Creating database with tutorial problems"
        )
    else:
        print("\n[OK] Database found")
    
    # Step 2: Clone OPL if needed
    if not opl_dir.exists():
        print(f"\n[>>] Cloning Open Problem Library...")
        print("     (This is a large repository ~2.5 GB, may take several minutes)")
        
        # Use shallow clone to save time and space
        success = run_command(
            [
                "git", "clone", 
                "--depth", "1",
                "--single-branch",
                "https://github.com/openwebwork/webwork-open-problem-library.git",
                str(opl_dir)
            ],
            "Cloning OPL repository",
            check=False
        )
        
        if not success:
            print("\n[X] Failed to clone OPL. Please check:")
            print("    1. You have git installed")
            print("    2. You have internet connectivity")
            print("    3. You have ~3 GB of free disk space")
            sys.exit(1)
        
        print("\n[OK] OPL cloned successfully")
    else:
        print(f"\n[OK] OPL directory already exists: {opl_dir}")
        
        # Offer to update
        print("\n[?] Update OPL repository? (y/N): ", end='')
        response = input().strip().lower()
        if response == 'y':
            run_command(
                ["git", "-C", str(opl_dir), "pull"],
                "Updating OPL repository"
            )
    
    # Step 3: Import Tier 1 collections
    print("\n" + "=" * 60)
    print("IMPORTING TIER 1 COLLECTIONS")
    print("=" * 60)
    
    total_imported = 0
    
    for collection, description in tier1_collections:
        collection_path = opl_dir / "OpenProblemLibrary" / collection
        
        if not collection_path.exists():
            print(f"\n[!] {collection} not found, skipping...")
            continue
        
        print(f"\n{'-' * 60}")
        print(f"[>>] {collection}: {description}")
        print(f"{'-' * 60}")
        
        # Count problems first
        pg_files = list(collection_path.rglob("*.pg"))
        print(f"     Found {len(pg_files)} problems")
        
        # Import
        success = run_command(
            [
                sys.executable, 
                "scripts/import_opl.py",
                str(collection_path),
                f"OPL-{collection}"
            ],
            f"Importing {collection} collection",
            check=False
        )
        
        if success:
            total_imported += len(pg_files)
    
    # Step 4: Show final statistics
    print("\n" + "=" * 60)
    print("[OK] BOOTSTRAP COMPLETE!")
    print("=" * 60)
    print(f"\n[>>] Approximately {total_imported} problems imported")
    
    print("\n[>>] Collections imported:")
    for collection, description in tier1_collections:
        print(f"     [OK] {collection:<15} - {description}")
    
    print("\n[>>] Next steps:")
    print("     1. Start the backend:")
    print("        cd apps/backend && python -m uvicorn app.main:app --reload")
    print()
    print("     2. View problems:")
    print("        http://localhost:8000/api/problems")
    print()
    print("     3. Search problems:")
    print("        http://localhost:8000/api/problems/search?q=calculus")
    print()
    print("     4. Import more collections:")
    print("        python scripts/import_opl.py webwork-open-problem-library/OpenProblemLibrary/Michigan")
    print()
    
    # Optional: Import more
    print("-" * 60)
    print("[?] Import additional Tier 2 collections? (Michigan, LoyolaChicago)")
    print("    This will add ~4,500 more problems. (y/N): ", end='')
    
    response = input().strip().lower()
    if response == 'y':
        tier2_collections = [
            ("Michigan", "~3,000 problems"),
            ("LoyolaChicago", "~1,500 problems"),
        ]
        
        for collection, count in tier2_collections:
            collection_path = opl_dir / "OpenProblemLibrary" / collection
            if collection_path.exists():
                print(f"\n[>>] Importing {collection} ({count})...")
                run_command(
                    [
                        sys.executable,
                        "scripts/import_opl.py",
                        str(collection_path),
                        f"OPL-{collection}"
                    ],
                    f"Importing {collection}",
                    check=False
                )


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[!] Bootstrap cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n[X] Bootstrap failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

