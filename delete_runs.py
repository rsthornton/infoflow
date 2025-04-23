"""
Utility script to delete simulation runs from the InfoFlow database.

This script provides commands to list, delete individual, or purge all simulation runs 
from the InfoFlow SQLite database. It's useful for maintaining a clean database, 
especially when conducting numerous research experiments.

Usage:
    python delete_runs.py --list [--limit N]     List recent simulation runs
    python delete_runs.py --delete RUN_ID        Delete a specific run
    python delete_runs.py --delete-all [--force] Delete all simulation runs
    python delete_runs.py --clear-recent         Delete the 10 most recent runs

The --force flag can be used with --delete-all to bypass confirmation prompts.

See also:
    docs/guides/managing_simulations.md for comprehensive documentation on
    managing simulation data.
"""

import os
import sqlite3
from pathlib import Path
import argparse

def list_runs(limit=10):
    """List recent simulation runs."""
    db_path = Path(os.getcwd()) / "data" / "simulation_stats.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Get recent runs
    c.execute("""
        SELECT run_id, timestamp, name, steps 
        FROM simulation_runs 
        ORDER BY timestamp DESC
        LIMIT ?
    """, (limit,))
    
    runs = c.fetchall()
    conn.close()
    
    if not runs:
        print("No simulation runs found.")
        return
    
    print("\nRecent simulation runs:")
    print("-" * 80)
    print(f"{'Run ID':<20} {'Timestamp':<20} {'Steps':<8} {'Name':<30}")
    print("-" * 80)
    
    for run in runs:
        run_id, timestamp, name, steps = run
        name = name or "Unnamed simulation"
        print(f"{run_id:<20} {timestamp:<20} {steps:<8} {name:<30}")
    
    return runs

def delete_run(run_id):
    """Delete a specific run from the database."""
    db_path = Path(os.getcwd()) / "data" / "simulation_stats.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    try:
        # Check if run exists
        c.execute("SELECT COUNT(*) FROM simulation_runs WHERE run_id = ?", (run_id,))
        count = c.fetchone()[0]
        
        if count == 0:
            print(f"Run ID '{run_id}' not found.")
            conn.close()
            return False
        
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Delete from timestep_data
        c.execute("DELETE FROM timestep_data WHERE run_id = ?", (run_id,))
        steps_deleted = c.rowcount
        
        # Delete from simulation_runs
        c.execute("DELETE FROM simulation_runs WHERE run_id = ?", (run_id,))
        
        # Commit changes
        conn.commit()
        print(f"Deleted run '{run_id}' with {steps_deleted} timesteps.")
        conn.close()
        return True
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error deleting run: {e}")
        conn.close()
        return False

def delete_all_runs():
    """Delete all simulation runs from the database."""
    db_path = Path(os.getcwd()) / "data" / "simulation_stats.db"
    
    if not db_path.exists():
        print(f"Database not found at {db_path}")
        return False
    
    conn = sqlite3.connect(db_path)
    
    try:
        # Begin transaction
        conn.execute("BEGIN TRANSACTION")
        
        # Delete all data
        c = conn.cursor()
        c.execute("DELETE FROM timestep_data")
        c.execute("DELETE FROM simulation_runs")
        
        # Commit changes
        conn.commit()
        print("Deleted all simulation runs from the database.")
        conn.close()
        return True
        
    except sqlite3.Error as e:
        conn.rollback()
        print(f"Error deleting runs: {e}")
        conn.close()
        return False

def main():
    parser = argparse.ArgumentParser(description="Delete simulation runs from the InfoFlow database.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("-l", "--list", action="store_true", help="List recent simulation runs")
    group.add_argument("-d", "--delete", type=str, help="Delete a specific run by ID")
    group.add_argument("--delete-all", action="store_true", help="Delete all simulation runs (USE WITH CAUTION)")
    parser.add_argument("-f", "--force", action="store_true", help="Force delete without confirmation")
    group.add_argument("--clear-recent", action="store_true", help="Clear the 10 most recent runs")
    
    parser.add_argument("--limit", type=int, default=20, help="Number of runs to list (default: 20)")
    
    args = parser.parse_args()
    
    if args.list:
        list_runs(args.limit)
    elif args.delete:
        delete_run(args.delete)
    elif args.delete_all:
        # Add -f/--force argument to bypass confirmation
        force = getattr(args, 'force', False)
        if force:
            delete_all_runs()
        else:
            try:
                confirm = input("Are you sure you want to delete ALL simulation runs? This cannot be undone. (y/N): ")
                if confirm.lower() == 'y':
                    delete_all_runs()
                else:
                    print("Operation cancelled.")
            except (EOFError, KeyboardInterrupt):
                print("\nConfirmation required. Use --force to bypass confirmation.")
                print("Example: python delete_runs.py --delete-all --force")
    elif args.clear_recent:
        runs = list_runs(10)
        if runs:
            confirm = input(f"Are you sure you want to delete these {len(runs)} recent runs? (y/N): ")
            if confirm.lower() == 'y':
                for run in runs:
                    delete_run(run[0])
            else:
                print("Operation cancelled.")

if __name__ == "__main__":
    main()