#!/usr/bin/env python3
"""
Command-line tool for comparing InfoFlow simulation runs.

This script provides a simple way to compare metrics from different simulation runs.
"""

import sys
import os
import argparse
import json
from pathlib import Path

# Add the project root to the Python path so we can import infoflow modules
project_root = Path(__file__).resolve().parent.parent
if project_root not in sys.path:
    sys.path.insert(0, str(project_root))

from infoflow.utils.simple_stats import StatsCollector

def parse_args():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Compare InfoFlow simulation runs')
    
    # Make run_ids optional
    parser.add_argument('run_ids', nargs='*', help='IDs of the simulation runs to compare')
    parser.add_argument('--metric', '-m', help='Metric to compare (default: avg_trust_government)')
    parser.add_argument('--output', '-o', help='Path to save the plot')
    parser.add_argument('--no-display', action='store_true', help='Do not display the plot')
    parser.add_argument('--list', '-l', action='store_true', help='List recent simulation runs')
    parser.add_argument('--export', '-e', help='Export a simulation run to JSON')
    
    return parser.parse_args()

def list_recent_runs():
    """Display a list of recent simulation runs."""
    runs = StatsCollector.get_recent_runs(limit=20)
    
    if not runs:
        print("No simulation runs found.")
        return
    
    print(f"{'ID':<10} {'Date':<20} {'Steps':<6} {'Name'}")
    print("-" * 50)
    
    for run in runs:
        print(f"{run['id']:<10} {run['timestamp']:<20} {run['steps']:<6} {run['name']}")

def export_run(run_id, output_path=None):
    """Export a simulation run to JSON."""
    if output_path:
        filepath = Path(output_path)
    else:
        filepath = None
    
    result = StatsCollector.export_run(run_id, filepath)
    
    if result:
        print(f"Exported run {run_id} to {result}")
    else:
        print(f"Run {run_id} not found")

def main():
    """Main entry point."""
    args = parse_args()
    
    if args.list:
        list_recent_runs()
        return
    
    if args.export:
        export_run(args.export, args.output)
        return
    
    # Only try to compare runs if run_ids were provided
    if args.run_ids:
        StatsCollector.plot_comparison(
            args.run_ids,
            metric=args.metric,
            save_path=args.output,
            show=not args.no_display
        )
    else:
        # If no specific command was given, show help
        if not (args.list or args.export):
            print("Please specify a command or run IDs to compare.")
            print("Use --list to see available simulation runs.")
            print("Use --export RUN_ID to export a simulation.")
            print("Or provide run IDs to compare them.")
            sys.exit(1)

if __name__ == "__main__":
    main()