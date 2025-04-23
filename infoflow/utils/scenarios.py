"""
Utilities for managing guided simulation scenarios.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any


def get_scenario_path() -> Path:
    """
    Get the path to the scenarios directory.
    
    Returns:
        Path object pointing to the scenarios directory
    """
    # First try to find the scenarios directory relative to this file
    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    scenarios_dir = current_dir.parent / "data" / "scenarios"
    
    # Check if the directory exists
    if not scenarios_dir.exists():
        # Try to find it relative to the current working directory
        scenarios_dir = Path(os.getcwd()) / "infoflow" / "data" / "scenarios"
        
    # Create the directory if it doesn't exist
    if not scenarios_dir.exists():
        os.makedirs(scenarios_dir, exist_ok=True)
    
    return scenarios_dir


def list_scenarios() -> List[Dict[str, Any]]:
    """
    List all available guided scenarios.
    
    Returns:
        List of scenario metadata dictionaries
    """
    scenarios = []
    scenarios_dir = get_scenario_path()
    
    # Find all JSON files in the scenarios directory
    for file_path in scenarios_dir.glob("*.json"):
        try:
            with open(file_path, "r") as f:
                scenario = json.load(f)
                
            # Add at least minimal metadata if missing
            if "id" not in scenario:
                scenario["id"] = file_path.stem
            
            if "name" not in scenario:
                scenario["name"] = file_path.stem.replace("_", " ").title()
                
            scenarios.append({
                "id": scenario["id"],
                "name": scenario["name"],
                "description": scenario.get("description", ""),
                "file_path": str(file_path)
            })
        except Exception as e:
            print(f"Error loading scenario from {file_path}: {e}")
    
    return scenarios


def get_scenario(scenario_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a specific guided scenario by ID.
    
    Args:
        scenario_id: ID of the scenario to retrieve
        
    Returns:
        Scenario data dictionary or None if not found
    """
    scenarios_dir = get_scenario_path()
    
    # First try direct match with the file name
    scenario_path = scenarios_dir / f"{scenario_id}.json"
    
    if not scenario_path.exists():
        # Try finding a file with matching ID field
        for file_path in scenarios_dir.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    scenario = json.load(f)
                    
                if scenario.get("id") == scenario_id:
                    scenario_path = file_path
                    break
            except Exception:
                continue
    
    # If we found a matching scenario, load and return it
    if scenario_path.exists():
        try:
            with open(scenario_path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading scenario {scenario_id}: {e}")
    
    return None