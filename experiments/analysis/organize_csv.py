#!/usr/bin/env python
"""
CSV File Organizer for InfoFlow Experiments

This script helps organize CSV files into the appropriate directories
based on their experiment type.

Usage:
  python organize_csv.py [--all] [file1.csv file2.csv ...]

Options:
  --all   Organize all CSV files in the exports directory
"""

import os
import sys
import shutil
import glob
import re
import pandas as pd

# Base directories
EXPERIMENTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
DATA_DIR = os.path.join(EXPERIMENTS_DIR, 'data')
TRUST_DIR = os.path.join(DATA_DIR, 'trust-experiments')
NETWORK_DIR = os.path.join(DATA_DIR, 'network-experiments')
COGNITIVE_DIR = os.path.join(DATA_DIR, 'cognitive-experiments')
EXPORTS_DIR = os.path.join(EXPERIMENTS_DIR, 'exports')

def determine_experiment_type(csv_path):
    """Determine the experiment type based on filename and content."""
    try:
        # First try to determine from filename
        filename = os.path.basename(csv_path).lower()
        
        # Trust experiment patterns
        if any(pattern in filename for pattern in ['trust', 'cred']):
            return 'trust'
            
        # Network experiment patterns
        if any(pattern in filename for pattern in ['network', 'connect', 'topolog', 'scale', 'random', 'small-world']):
            return 'network'
            
        # Cognitive experiment patterns
        if any(pattern in filename for pattern in ['cognit', 'belief', 'bias', 'think']):
            return 'cognitive'
            
        # If filename doesn't provide clear indication, check content
        try:
            df = pd.read_csv(csv_path)
            
            # Check columns for clues
            columns = df.columns.tolist()
            
            # Trust-related columns
            if any('trust' in col.lower() for col in columns):
                return 'trust'
                
            # Network-related columns
            if any(pattern in ' '.join(columns).lower() for pattern in ['network_type', 'connectivity', 'small_world', 'scale_free']):
                return 'network'
                
            # Cognitive-related columns
            if any(pattern in ' '.join(columns).lower() for pattern in ['confirmation_bias', 'critical_thinking', 'social_conformity']):
                return 'cognitive'
                
        except Exception as e:
            print(f"Warning: Could not analyze content of {csv_path}: {e}")
            
        # If we still don't know, return 'unknown'
        return 'unknown'
        
    except Exception as e:
        print(f"Error determining experiment type for {csv_path}: {e}")
        return 'unknown'

def organize_csv_file(csv_path):
    """Organize a single CSV file."""
    if not os.path.exists(csv_path) or not csv_path.endswith('.csv'):
        print(f"Error: {csv_path} is not a valid CSV file")
        return False
        
    # Determine experiment type
    exp_type = determine_experiment_type(csv_path)
    
    # Determine destination
    if exp_type == 'trust':
        dest_dir = TRUST_DIR
    elif exp_type == 'network':
        dest_dir = NETWORK_DIR
    elif exp_type == 'cognitive':
        dest_dir = COGNITIVE_DIR
    else:
        # For unknown types, store in the base data directory
        dest_dir = DATA_DIR
        
    # Create destination filename (preserve original name)
    dest_path = os.path.join(dest_dir, os.path.basename(csv_path))
    
    # If destination file already exists, add a suffix
    if os.path.exists(dest_path):
        base, ext = os.path.splitext(dest_path)
        counter = 1
        while os.path.exists(f"{base}_{counter}{ext}"):
            counter += 1
        dest_path = f"{base}_{counter}{ext}"
    
    # Copy the file
    try:
        shutil.copy2(csv_path, dest_path)
        print(f"✓ Organized {os.path.basename(csv_path)} -> {os.path.relpath(dest_path, EXPERIMENTS_DIR)}")
        return True
    except Exception as e:
        print(f"Error copying {csv_path}: {e}")
        return False

def organize_all_csv_files():
    """Organize all CSV files in the exports directory."""
    organized_count = 0
    
    # Find all CSV files in the exports directory
    exported_paths = []
    
    # Check exports directory
    if os.path.exists(EXPORTS_DIR):
        exported_paths.extend(glob.glob(os.path.join(EXPORTS_DIR, '*.csv')))
    
    # Organize each file
    for path in exported_paths:
        if organize_csv_file(path):
            organized_count += 1
    
    print(f"\nOrganized {organized_count} of {len(exported_paths)} CSV files")
    return organized_count

def main():
    """Main function."""
    # Parse arguments
    if len(sys.argv) < 2:
        print(__doc__)
        return
        
    # Check if '--all' flag is present
    if '--all' in sys.argv:
        organize_all_csv_files()
        return
        
    # Otherwise organize specified files
    for csv_path in sys.argv[1:]:
        organize_csv_file(csv_path)

if __name__ == "__main__":
    main()