#!/usr/bin/env python
"""
Experiment File Organizer for InfoFlow

This script helps organize experiment files by moving exported JSON files from
experiments/exported-json to the appropriate experiment directory based on 
their content and user selections.
"""

import os
import sys
import json
import shutil
from pathlib import Path
import argparse
import re
from datetime import datetime

# Define experiment types and their directories
EXPERIMENT_DIRS = {
    "trust": "trust-experiment",
    "network": "network-experiment",
    "cognitive": "cognitive-experiment",
    "custom": "custom-experiments"
}

def list_json_files(src_dir):
    """List all JSON files in the source directory."""
    json_files = []
    for f in os.listdir(src_dir):
        if f.endswith('.json') and os.path.isfile(os.path.join(src_dir, f)):
            json_files.append(f)
    return json_files

def read_json_data(file_path):
    """Read and return JSON data from a file."""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {file_path} is not a valid JSON file.")
        return None
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return None

def detect_experiment_type(data):
    """
    Attempt to automatically detect experiment type based on parameters
    Returns a tuple of (detected_type, confidence, reason)
    """
    if not data or "parameters" not in data:
        return ("unknown", 0, "No parameters found")
    
    params = data.get("parameters", {})
    
    # Check for trust experiment
    trust_patterns = {
        "high initial trust": params.get("initial_trust_in_government", 5.0) > 7.0 or 
                             params.get("initial_trust_in_corporate", 5.0) > 7.0 or
                             params.get("initial_trust_in_influencers", 5.0) > 7.0,
        "low initial trust": params.get("initial_trust_in_government", 5.0) < 3.0 or
                             params.get("initial_trust_in_corporate", 5.0) < 3.0 or
                             params.get("initial_trust_in_influencers", 5.0) < 3.0,
        "trust scenario": "trust_study" in params.get("scenario_id", ""),
        "trust in name": "trust" in data.get("name", "").lower(),
    }
    trust_score = sum(1 for k, v in trust_patterns.items() if v)
    
    # Check for network experiment
    network_patterns = {
        "modified network params": params.get("small_world_k", 4) != 4 or
                                  params.get("small_world_p", 0.1) != 0.1 or
                                  params.get("scale_free_m", 3) != 3,
        "network scenario": "network_connectivity" in params.get("scenario_id", ""),
        "network in name": "network" in data.get("name", "").lower() or 
                          "connectivity" in data.get("name", "").lower(),
        "custom network type": params.get("network_type", "small_world") != "small_world",
    }
    network_score = sum(1 for k, v in network_patterns.items() if v)
    
    # Check for cognitive experiment
    cognitive_patterns = {
        "modified cognitive params": params.get("confirmation_bias_min", 4) != 4 or 
                                    params.get("critical_thinking_min", 4) != 4 or
                                    params.get("social_conformity_min", 4) != 4 or
                                    params.get("truth_seeking_mean", 1.0) != 1.0,
        "belief scenario": "belief_resistance" in params.get("scenario_id", ""),
        "cognitive in name": any(kw in data.get("name", "").lower() for kw in 
                               ["cognitive", "belief", "thinking", "bias", "conformity"])
    }
    cognitive_score = sum(1 for k, v in cognitive_patterns.items() if v)
    
    # Determine the most likely experiment type
    scores = {
        "trust": trust_score,
        "network": network_score,
        "cognitive": cognitive_score,
    }
    max_type = max(scores, key=scores.get)
    max_score = scores[max_type]
    
    # Calculate confidence (0-100%)
    total_checks = sum(len(patterns) for patterns in 
                     [trust_patterns, network_patterns, cognitive_patterns])
    confidence = int((max_score / total_checks) * 100) if total_checks > 0 else 0
    
    # Determine reason for classification
    if max_type == "trust" and trust_score > 0:
        reasons = [k for k, v in trust_patterns.items() if v]
        reason = f"Trust indicators: {', '.join(reasons)}"
    elif max_type == "network" and network_score > 0:
        reasons = [k for k, v in network_patterns.items() if v]
        reason = f"Network indicators: {', '.join(reasons)}"
    elif max_type == "cognitive" and cognitive_score > 0:
        reasons = [k for k, v in cognitive_patterns.items() if v]
        reason = f"Cognitive indicators: {', '.join(reasons)}"
    else:
        reason = "No clear indicators found"
    
    # If confidence is too low, return unknown
    if confidence < 10:
        return ("unknown", confidence, "Insufficient indicators")
        
    return (max_type, confidence, reason)

def suggest_filename(data, exp_type):
    """Suggest a standardized filename based on data content and experiment type."""
    name = data.get("name", "")
    run_id = data.get("id", "unknown")
    
    # Check if we should preserve the original filename
    # If the file already has a meaningful name, use it
    if name and len(name) > 5:
        # The file likely already has a meaningful name that was provided
        # by the user when exporting. Just clean it if needed.
        
        # Convert to lowercase and remove special characters if necessary
        clean_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name.lower())
        # Remove repeated underscores
        clean_name = re.sub(r'_+', '_', clean_name)
        # Trim underscores from beginning and end
        clean_name = clean_name.strip('_')
        
        # Return the name with .json extension if needed
        if not clean_name.endswith('.json'):
            return f"{clean_name}.json"
        return clean_name
    
    # Otherwise, generate a name based on experiment type and parameters
    params = data.get("parameters", {})
    if exp_type == "trust":
        t_gov = params.get("initial_trust_in_government", 5)
        t_corp = params.get("initial_trust_in_corporate", 5)
        t_inf = params.get("initial_trust_in_influencers", 5)
        t_avg = (t_gov + t_corp + t_inf) / 3
        
        if t_avg >= 7:
            level = "high"
        elif t_avg <= 3:
            level = "low"
        else:
            level = "moderate"
            
        clean_name = f"{level}-trust"
    elif exp_type == "network":
        net_type = params.get("network_type", "small_world")
        clean_name = f"{net_type.replace('_', '-')}-network"
    elif exp_type == "cognitive":
        # Detect if it's about confirmation bias, critical thinking, etc.
        if params.get("confirmation_bias_min", 4) != 4:
            clean_name = "confirmation-bias"
        elif params.get("critical_thinking_min", 4) != 4:
            clean_name = "critical-thinking"
        elif params.get("social_conformity_min", 4) != 4:
            clean_name = "social-conformity"
        else:
            clean_name = "cognitive-factors"
    else:
        timestamp = datetime.now().strftime("%Y%m%d")
        clean_name = f"simulation_{timestamp}"
    
    # Add a timestamp to ensure uniqueness
    timestamp = re.search(r'_run_(\d+)', run_id)
    if timestamp:
        ts = timestamp.group(1)
    else:
        ts = int(datetime.now().timestamp())
    
    return f"{clean_name}_{ts}.json"

def move_file(src_path, dest_dir, new_filename=None):
    """Move a file to the destination directory with optional renaming."""
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir, exist_ok=True)
    
    filename = os.path.basename(src_path) if new_filename is None else new_filename
    dest_path = os.path.join(dest_dir, filename)
    
    # Check if destination file already exists
    if os.path.exists(dest_path):
        base, ext = os.path.splitext(filename)
        timestamp = datetime.now().strftime("%H%M%S")
        dest_path = os.path.join(dest_dir, f"{base}_{timestamp}{ext}")
    
    try:
        shutil.copy2(src_path, dest_path)
        # Check if file was copied successfully before removing the original
        if os.path.exists(dest_path):
            # Ask for confirmation before removing the original
            return dest_path
        else:
            print(f"Error: Failed to copy {src_path} to {dest_path}")
            return None
    except Exception as e:
        print(f"Error moving file: {e}")
        return None

def main():
    parser = argparse.ArgumentParser(description="Organize InfoFlow experiment files")
    parser.add_argument("--all", action="store_true", help="Process all files in the export directory")
    parser.add_argument("--file", type=str, help="Process a specific file")
    parser.add_argument("--auto", action="store_true", help="Automatically detect experiment type without prompting")
    parser.add_argument("--keep-original", action="store_true", help="Keep original files in export directory")
    
    args = parser.parse_args()
    
    # Determine project root based on script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.abspath(os.path.join(script_dir, ".."))
    
    # Define directory paths
    export_dir = os.path.join(project_root, "experiments", "exported-json")
    experiment_base_dir = os.path.join(project_root, "experiments")
    
    # Ensure export directory exists
    if not os.path.exists(export_dir):
        print(f"Creating export directory: {export_dir}")
        os.makedirs(export_dir, exist_ok=True)
    
    # Get list of JSON files to process
    if args.file:
        file_path = args.file
        if not os.path.exists(file_path):
            file_path = os.path.join(export_dir, args.file)
            
        if not os.path.exists(file_path):
            print(f"Error: File '{args.file}' not found.")
            return 1
            
        files_to_process = [os.path.basename(file_path)]
        export_dir = os.path.dirname(file_path)
    else:
        if not os.path.exists(export_dir):
            print(f"Error: Export directory '{export_dir}' not found.")
            return 1
            
        files_to_process = list_json_files(export_dir)
    
    if not files_to_process:
        print(f"No JSON files found in {export_dir}")
        return 0
    
    # Process each file
    print(f"Found {len(files_to_process)} JSON files to process")
    
    for i, filename in enumerate(files_to_process):
        file_path = os.path.join(export_dir, filename)
        
        print(f"\nProcessing {i+1}/{len(files_to_process)}: {filename}")
        
        # Read file data
        data = read_json_data(file_path)
        if not data:
            continue
        
        # Detect experiment type
        exp_type, confidence, reason = detect_experiment_type(data)
        
        # Get experiment metadata for display
        name = data.get("name", "Unnamed simulation")
        run_id = data.get("id", "Unknown ID")
        steps = data.get("steps", 0)
        timestamp = data.get("timestamp", "Unknown date")
        
        print(f"  Title: {name}")
        print(f"  ID: {run_id}")
        print(f"  Date: {timestamp}")
        print(f"  Steps: {steps}")
        print(f"  Detected type: {exp_type.upper()} (confidence: {confidence}%)")
        print(f"  Reason: {reason}")
        
        # Suggest a new filename
        suggested_filename = suggest_filename(data, exp_type)
        print(f"  Suggested filename: {suggested_filename}")
        
        # Determine target directory
        if exp_type != "unknown":
            target_dir = os.path.join(experiment_base_dir, EXPERIMENT_DIRS[exp_type])
        else:
            # Default to custom experiments for unknown types
            target_dir = os.path.join(experiment_base_dir, EXPERIMENT_DIRS["custom"])
        
        # Automatic mode: use detected type and suggested filename
        if args.auto:
            dest_path = move_file(file_path, target_dir, suggested_filename)
            if dest_path:
                print(f"  Moved to: {dest_path}")
                if not args.keep_original:
                    os.remove(file_path)
                    print(f"  Removed original file: {file_path}")
            continue
        
        # Interactive mode: ask user for confirmation
        print("\nActions:")
        print("  [t] Move to trust-experiment/")
        print("  [n] Move to network-experiment/")
        print("  [c] Move to cognitive-experiment/")
        print("  [x] Move to custom-experiments/")
        print("  [r] Rename file")
        print("  [s] Skip this file")
        print("  [q] Quit")
        
        while True:
            choice = input("\nEnter choice: ").lower()
            
            if choice == 'q':
                return 0
            elif choice == 's':
                print("  Skipping file")
                break
            elif choice == 'r':
                new_name = input(f"  Enter new filename [{suggested_filename}]: ")
                if not new_name:
                    new_name = suggested_filename
                if not new_name.endswith('.json'):
                    new_name += '.json'
                    
                # Just rename the file in place
                new_path = os.path.join(export_dir, new_name)
                try:
                    os.rename(file_path, new_path)
                    print(f"  Renamed to: {new_name}")
                    file_path = new_path  # Update file_path for potential move
                except Exception as e:
                    print(f"  Error renaming file: {e}")
                continue  # Continue asking for action
            elif choice in ['t', 'n', 'c', 'x']:
                # Determine target directory
                if choice == 't':
                    target_dir = os.path.join(experiment_base_dir, EXPERIMENT_DIRS["trust"])
                elif choice == 'n':
                    target_dir = os.path.join(experiment_base_dir, EXPERIMENT_DIRS["network"])
                elif choice == 'c':
                    target_dir = os.path.join(experiment_base_dir, EXPERIMENT_DIRS["cognitive"])
                elif choice == 'x':
                    target_dir = os.path.join(experiment_base_dir, EXPERIMENT_DIRS["custom"])
                
                # Ask for filename
                rename_prompt = input(f"  Use suggested filename '{suggested_filename}'? [Y/n]: ")
                if rename_prompt.lower() in ['n', 'no']:
                    new_name = input("  Enter new filename: ")
                    if not new_name.endswith('.json'):
                        new_name += '.json'
                else:
                    new_name = suggested_filename
                
                # Move the file
                dest_path = move_file(file_path, target_dir, new_name)
                if dest_path:
                    print(f"  Moved to: {dest_path}")
                    
                    # Ask about removing original
                    if not args.keep_original:
                        remove_prompt = input("  Remove original file? [Y/n]: ")
                        if remove_prompt.lower() not in ['n', 'no']:
                            os.remove(file_path)
                            print(f"  Removed original file: {file_path}")
                break
            else:
                print("  Invalid choice, please try again")
    
    print("\nDone processing files.")
    return 0

if __name__ == "__main__":
    sys.exit(main())