"""Setup script for the portable SQLite problem database."""
#!/usr/bin/env python3
"""Setup script to initialize the problem database and run migrations."""

import os
import sys
import subprocess
from pathlib import Path

def run_command(cmd: list[str], cwd: str = None) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
        print(f"✓ {' '.join(cmd)}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {' '.join(cmd)}")
        print(f"  Error: {e.stderr}")
        return False

def setup_database():
    """Set up the SQLite database with migrations."""
    print("Setting up SQLite problem database...")
    
    # Change to backend directory
    backend_dir = Path(__file__).parent / "apps" / "backend"
    os.chdir(backend_dir)
    
    # Install dependencies
    print("\n1. Installing Python dependencies...")
    if not run_command([sys.executable, "-m", "pip", "install", "-e", "."]):
        return False
    
    # Install sqlite-vec (if available)
    print("\n2. Installing sqlite-vec...")
    try:
        run_command([sys.executable, "-m", "pip", "install", "sqlite-vec"])
    except:
        print("  Warning: sqlite-vec not available, using fallback embedding method")
    
    # Initialize Alembic
    print("\n3. Initializing Alembic...")
    if not run_command(["alembic", "init", "alembic"]):
        return False
    
    # Create initial migration
    print("\n4. Creating initial migration...")
    if not run_command(["alembic", "revision", "--autogenerate", "-m", "Initial migration"]):
        return False
    
    # Run migrations
    print("\n5. Running database migrations...")
    if not run_command(["alembic", "upgrade", "head"]):
        return False
    
    # Run sample problem migration
    print("\n6. Migrating sample problems...")
    if not run_command([sys.executable, "scripts/migrate_sample_problems.py"]):
        return False
    
    print("\n✓ Database setup completed successfully!")
    print("\nNext steps:")
    print("1. Start the backend server: cd apps/backend && python -m uvicorn app.main:app --reload")
    print("2. Start the frontend: cd apps/web && npm run dev")
    print("3. Visit http://localhost:3000/search to explore problems")
    
    return True

def main():
    """Main setup function."""
    print("WeBWorK PG Problem Database Setup")
    print("=" * 40)
    
    if setup_database():
        sys.exit(0)
    else:
        print("\n✗ Setup failed!")
        sys.exit(1)

if __name__ == "__main__":
    main()
