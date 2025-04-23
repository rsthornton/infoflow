#\!/usr/bin/env python
"""
Data Inventory Tool for InfoFlow

This script lists all available CSV files for analysis,
organized by research area.
"""

import os
import glob
import pandas as pd
from pathlib import Path

# Base directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
DATA_DIR = os.path.join(EXPERIMENTS_DIR, 'data')

def print_section(title):
    """Print a section header."""
    print("\n" + "=" * 60)
    print(f" {title}")
    print("=" * 60)

def analyze_csv(file_path):
    """Get basic info about a CSV file."""
    info = {
        'path': file_path,
        'name': os.path.basename(file_path),
        'size': os.path.getsize(file_path) / 1024,  # KB
        'metrics': [],
        'steps': 0
    }
    
    try:
        df = pd.read_csv(file_path)
        info['metrics'] = [col for col in df.columns if col.startswith('avg_') or 
                          col.startswith('count_') or col in ['polarization_index']]
        if 'step' in df.columns:
            info['steps'] = df['step'].max()
    except Exception as e:
        info['error'] = str(e)
        
    return info

def list_research_data():
    """List all available research data files."""
    print_section("InfoFlow Experiment Data Inventory")
    
    # Trust experiments
    trust_dir = os.path.join(DATA_DIR, 'trust-experiments')
    trust_files = glob.glob(os.path.join(trust_dir, '*.csv'))
    
    print_section("Trust Research Data")
    if trust_files:
        print(f"Found {len(trust_files)} trust experiment files:")
        for file_path in trust_files:
            info = analyze_csv(file_path)
            print(f"  - {info['name']} ({info['size']:.1f} KB, {info['steps']} steps)")
            if len(info['metrics']) > 0:
                print(f"    Metrics: {', '.join(info['metrics'][:5])}...")
            print()
    else:
        print("No trust experiment data found.")
    
    # Network experiments
    network_dir = os.path.join(DATA_DIR, 'network-experiments')
    network_files = glob.glob(os.path.join(network_dir, '*.csv'))
    
    print_section("Network Research Data")
    if network_files:
        print(f"Found {len(network_files)} network experiment files:")
        for file_path in network_files:
            info = analyze_csv(file_path)
            print(f"  - {info['name']} ({info['size']:.1f} KB, {info['steps']} steps)")
            if len(info['metrics']) > 0:
                print(f"    Metrics: {', '.join(info['metrics'][:5])}...")
            print()
    else:
        print("No network experiment data found.")
    
    # Cognitive experiments
    cognitive_dir = os.path.join(DATA_DIR, 'cognitive-experiments')
    cognitive_files = glob.glob(os.path.join(cognitive_dir, '*.csv'))
    
    print_section("Cognitive Research Data")
    if cognitive_files:
        print(f"Found {len(cognitive_files)} cognitive experiment files:")
        for file_path in cognitive_files:
            info = analyze_csv(file_path)
            print(f"  - {info['name']} ({info['size']:.1f} KB, {info['steps']} steps)")
            if len(info['metrics']) > 0:
                print(f"    Metrics: {', '.join(info['metrics'][:5])}...")
            print()
    else:
        print("No cognitive experiment data found.")
    
    # Other data
    other_files = glob.glob(os.path.join(DATA_DIR, '*.csv'))
    
    print_section("Other Experiment Data")
    if other_files:
        print(f"Found {len(other_files)} other data files:")
        for file_path in other_files:
            info = analyze_csv(file_path)
            print(f"  - {info['name']} ({info['size']:.1f} KB, {info['steps']} steps)")
            if len(info['metrics']) > 0:
                print(f"    Metrics: {', '.join(info['metrics'][:5])}...")
            print()
    else:
        print("No other data files found.")

if __name__ == "__main__":
    list_research_data()
