"""
Simple statistics collection system for InfoFlow.

This module provides a lightweight system for tracking and comparing simulation results.
"""

import json
import os
import sqlite3
import time
import uuid
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np


class StatsCollector:
    """
    Simple statistics collector for tracking simulation results.

    This class collects metrics at each simulation step and stores them in a SQLite database,
    allowing for easy retrieval and comparison of simulation runs.
    """

    def __init__(self, db_path=None, run_id=None):
        """
        Initialize the stats collector.

        Args:
            db_path: Path to the SQLite database. Defaults to 'data/simulation_stats.db'
                    relative to the current working directory.
            run_id: Optional specific run ID to use. If None, generates a random UUID.
        """
        if db_path is None:
            # Create data directory if it doesn't exist
            data_dir = Path(os.getcwd()) / "data"
            os.makedirs(data_dir, exist_ok=True)
            db_path = data_dir / "simulation_stats.db"

        self.db_path = str(db_path)
        
        # Allow passing in a specific run_id or generate a new one
        self.run_id = run_id if run_id else str(uuid.uuid4())[:8]
        self.init_db()

    def init_db(self):
        """Initialize the database schema if it doesn't exist."""
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            c = conn.cursor()

            # Create tables if they don't exist
            c.execute(
                """
            CREATE TABLE IF NOT EXISTS simulation_runs (
                run_id TEXT PRIMARY KEY,
                timestamp TEXT,
                name TEXT,
                parameters TEXT,
                steps INTEGER
            )
            """
            )

            c.execute(
                """
            CREATE TABLE IF NOT EXISTS timestep_data (
                run_id TEXT,
                step INTEGER,
                metric_name TEXT,
                value REAL,
                PRIMARY KEY (run_id, step, metric_name)
            )
            """
            )

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error in init_db: {e}")
            # Non-critical - we'll try creating tables again in future calls

    def start_run(self, parameters, force_id=False):
        """
        Record the start of a new simulation run.

        Args:
            parameters: Dictionary of simulation parameters
            force_id: If True, use the current run_id even if it exists in the database

        Returns:
            The run ID for this simulation
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            c = conn.cursor()

            # Check if run_id already exists, and handle accordingly
            c.execute("SELECT 1 FROM simulation_runs WHERE run_id = ?", (self.run_id,))
            exists = c.fetchone() is not None
            
            if exists and not force_id:
                # If the ID exists and we're not forcing it, log this fact for debugging
                print(f"WARNING: run_id {self.run_id} already exists in database. Generating a new one.")
                
                # Generate a new unique ID since this one already exists
                old_id = self.run_id
                self.run_id = f"run_{int(time.time())}_{str(uuid.uuid4())[:6]}"
                print(f"Changed run_id from {old_id} to {self.run_id}")
            elif exists and force_id:
                # If we're forcing the ID and it exists, delete the old entry
                print(f"Force ID enabled. Replacing existing run_id {self.run_id}")
                c.execute("DELETE FROM simulation_runs WHERE run_id = ?", (self.run_id,))
                c.execute("DELETE FROM timestep_data WHERE run_id = ?", (self.run_id,))
            
            # Store run metadata
            c.execute(
                "INSERT INTO simulation_runs VALUES (?, ?, ?, ?, ?)",
                (
                    self.run_id,
                    time.strftime("%Y-%m-%d %H:%M:%S"),
                    "",
                    json.dumps(parameters),
                    0,
                ),
            )

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error in start_run: {e}")
            # Ensure we have a valid run_id even if db operation fails
            self.run_id = f"sim_{int(time.time())}"
            
        return self.run_id

    def record_step(self, step, metrics):
        """
        Record metrics for a simulation step.

        Args:
            step: Current simulation step (0-indexed)
            metrics: Dictionary of metric names and values
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            c = conn.cursor()

            # Update step count (add 1 to convert from 0-indexed to 1-indexed for display)
            # This ensures "75 steps" shows as 75 steps in the UI
            display_step = step + 1
            c.execute(
                "UPDATE simulation_runs SET steps = MAX(steps, ?) WHERE run_id = ?",
                (display_step, self.run_id),
            )

            # Store each metric
            for name, value in metrics.items():
                # Convert numpy types to Python native types
                if isinstance(value, (np.integer, np.floating)):
                    value = value.item()

                c.execute(
                    "INSERT OR REPLACE INTO timestep_data VALUES (?, ?, ?, ?)",
                    (self.run_id, step, name, value),
                )

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error in record_step: {e}")
            # Just log the error but continue - we don't want to crash the simulation

    def name_run(self, name):
        """
        Add a name to the current run.

        Args:
            name: Name to assign to this simulation run
        """
        try:
            conn = sqlite3.connect(self.db_path, timeout=10)
            c = conn.cursor()

            c.execute(
                "UPDATE simulation_runs SET name = ? WHERE run_id = ?", (name, self.run_id)
            )

            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(f"Database error in name_run: {e}")
            # Non-critical operation, can continue without successful naming

    @staticmethod
    def get_recent_runs(limit=10):
        """
        Get metadata for recent simulation runs.

        Args:
            limit: Maximum number of runs to return

        Returns:
            List of dictionaries with run metadata
        """
        # Use default path if this is a static method call
        data_dir = Path(os.getcwd()) / "data"
        db_path = data_dir / "simulation_stats.db"

        if not os.path.exists(db_path):
            return []

        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            c = conn.cursor()

            c.execute(
                "SELECT run_id, timestamp, name, steps FROM simulation_runs ORDER BY timestamp DESC LIMIT ?",
                (limit,),
            )

            runs = [
                {"id": r[0], "timestamp": r[1], "name": r[2], "steps": r[3]}
                for r in c.fetchall()
            ]

            conn.close()
            return runs
        except sqlite3.Error as e:
            print(f"Database error in get_recent_runs: {e}")
            return []
            
    @staticmethod
    def get_run_metadata(run_id):
        """
        Get metadata for a specific simulation run without retrieving all metrics data.
        
        Args:
            run_id: The ID of the simulation run
            
        Returns:
            Dictionary with run metadata, or None if not found
        """
        # Use default path if this is a static method call
        data_dir = Path(os.getcwd()) / "data"
        db_path = data_dir / "simulation_stats.db"
        
        if not os.path.exists(db_path):
            return None
            
        try:
            conn = sqlite3.connect(str(db_path), timeout=10)
            c = conn.cursor()
            
            c.execute(
                "SELECT run_id, timestamp, name, steps FROM simulation_runs WHERE run_id = ?",
                (run_id,),
            )
            
            result = c.fetchone()
            conn.close()
            
            if result:
                return {
                    "id": result[0],
                    "timestamp": result[1],
                    "name": result[2],
                    "steps": result[3]
                }
            return None
        except sqlite3.Error as e:
            print(f"Database error in get_run_metadata: {e}")
            return None

    @staticmethod
    def get_run_data(run_id):
        """
        Get complete data for a specific run.

        Args:
            run_id: The ID of the simulation run

        Returns:
            Dictionary with run metadata and metrics
        """
        # Use default path if this is a static method call
        data_dir = Path(os.getcwd()) / "data"
        db_path = data_dir / "simulation_stats.db"

        if not os.path.exists(db_path):
            print(f"Database file does not exist: {db_path}")
            return None

        try:
            # Increased timeout to 30 seconds to handle potentially slow operations or locks
            conn = sqlite3.connect(str(db_path), timeout=30)
            
            # Enable foreign keys and set pragmas for better performance
            conn.execute("PRAGMA foreign_keys = ON")
            conn.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging for better concurrency
            
            c = conn.cursor()

            # Get run metadata
            c.execute("SELECT * FROM simulation_runs WHERE run_id = ?", (run_id,))
            meta = c.fetchone()

            if not meta:
                print(f"No run found with ID: {run_id}")
                conn.close()
                return None

            # Get metrics with a separate try block to ensure we close the connection
            try:
                c.execute(
                    "SELECT step, metric_name, value FROM timestep_data WHERE run_id = ? ORDER BY step",
                    (run_id,),
                )

                # Organize by step
                metrics = {}
                for step, name, value in c.fetchall():
                    step_str = str(step)
                    if step_str not in metrics:
                        metrics[step_str] = {}
                    metrics[step_str][name] = value
                
                # Safely decode JSON parameters
                try:
                    parameters = json.loads(meta[3]) if meta[3] else {}
                except json.JSONDecodeError:
                    print(f"Error decoding parameters JSON for run {run_id}")
                    parameters = {}
                
                result = {
                    "id": meta[0],
                    "timestamp": meta[1],
                    "name": meta[2],
                    "parameters": parameters,
                    "steps": meta[4],
                    "metrics": metrics,
                }
                
                conn.close()
                return result
                
            except sqlite3.Error as e:
                print(f"Error fetching metrics for run {run_id}: {e}")
                conn.close()
                
                # Return partial data without metrics
                return {
                    "id": meta[0],
                    "timestamp": meta[1],
                    "name": meta[2],
                    "parameters": json.loads(meta[3]) if meta[3] else {},
                    "steps": meta[4],
                    "metrics": {},
                }
                
        except sqlite3.Error as e:
            print(f"Database error in get_run_data: {e}")
            return None
        except Exception as e:
            print(f"Unexpected error in get_run_data: {e}")
            return None

    @staticmethod
    def export_run(run_id, filepath=None, filename=None, format="json"):
        """
        Export run data to a JSON or CSV file.

        Args:
            run_id: The ID of the simulation run
            filepath: Path to save the file. If None, uses a default name.
            filename: Specific filename to use (without path). If None, generates a default.
            format: Export format, either "json" or "csv"

        Returns:
            Path to the saved file, or False if the run was not found
        """
        data = StatsCollector.get_run_data(run_id)

        if not data:
            return False

        if not filepath:
            # Use the appropriate export directory based on format
            project_root = Path(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
            
            if format.lower() == "json":
                export_dir = project_root / "experiments" / "exported-json"
            else:
                export_dir = project_root / "experiments" / "exports"
                
            os.makedirs(export_dir, exist_ok=True)
            
            # Use provided filename or generate a default one
            if filename:
                base_filename = filename
                if "." in base_filename:  # Remove extension if provided
                    base_filename = base_filename.rsplit(".", 1)[0]
            else:
                # Generate a name based on simulation name if available
                if data.get("name"):
                    # Clean up the name for safe filename use
                    safe_name = data["name"].replace(" ", "_").replace("/", "-").replace("\\", "-")
                    base_filename = f"{safe_name}_{run_id}"
                else:
                    base_filename = f"simulation_{run_id}"
            
            # Add extension based on format
            ext = ".json" if format.lower() == "json" else ".csv"
            filepath = export_dir / f"{base_filename}{ext}"

        if format.lower() == "json":
            # Export as JSON
            with open(filepath, "w") as f:
                json.dump(data, f, indent=2)
        else:
            # Export as CSV
            try:
                # Extract parameters for CSV header
                params = data.get("parameters", {})
                param_str = ""
                for key, value in params.items():
                    # Convert parameter value to string and escape commas
                    param_str += f",{key}=\"{str(value).replace(',', ';')}\""
                
                # Open CSV file for writing
                with open(filepath, "w") as f:
                    # Write header
                    f.write(f"step,run_id,timestamp,name{param_str}")
                    
                    # Add metric columns dynamically based on first step metrics
                    if "metrics" in data and data["metrics"]:
                        first_step = min(data["metrics"].keys(), key=lambda x: int(x))
                        for metric_name in data["metrics"][first_step].keys():
                            f.write(f",{metric_name}")
                    f.write("\n")
                    
                    # Write data rows
                    if "metrics" in data and data["metrics"]:
                        for step, metrics in sorted(data["metrics"].items(), key=lambda x: int(x[0])):
                            # Basic fields
                            f.write(f"{step},{data.get('id', '')},{data.get('timestamp', '')},{data.get('name', '')}")
                            
                            # Parameters (same for all steps)
                            for val in params.values():
                                f.write(f",\"{str(val).replace(',', ';')}\"")
                            
                            # Metrics for this step
                            for metric_name in data["metrics"][first_step].keys():
                                value = metrics.get(metric_name, "")
                                f.write(f",{value}")
                            f.write("\n")
            except Exception as e:
                print(f"Error exporting to CSV: {e}")
                # Fallback to JSON if CSV export fails
                with open(filepath.with_suffix(".json"), "w") as f:
                    json.dump(data, f, indent=2)
                return filepath.with_suffix(".json")

        return filepath

    @staticmethod
    def plot_comparison(run_ids, metric=None, save_path=None, show=True):
        """
        Plot a comparison of metrics from multiple simulation runs.

        Args:
            run_ids: List of run IDs to compare
            metric: Name of the metric to plot. If None, uses 'avg_trust_government'
            save_path: Path to save the plot. If None, uses a default location.
            show: Whether to display the plot interactively

        Returns:
            Path to the saved plot, or None if no data was found
        """
        metrics = metric or "avg_trust_government"
        runs = []

        for run_id in run_ids:
            data = StatsCollector.get_run_data(run_id)
            if data:
                runs.append(data)

        if not runs:
            print("No valid run data found")
            return None

        plt.figure(figsize=(10, 6))

        for run in runs:
            steps = []
            values = []

            for step, step_metrics in run["metrics"].items():
                if metrics in step_metrics:
                    steps.append(int(step))
                    values.append(step_metrics[metrics])

            steps, values = zip(*sorted(zip(steps, values)))
            label = f"{run['name'] or run['id']} ({len(steps)} steps)"
            plt.plot(steps, values, label=label)

        plt.title(f"Comparison of {metrics}")
        plt.xlabel("Step")
        plt.ylabel("Value")
        plt.legend()
        plt.grid(True)
        plt.tight_layout()

        if save_path is None:
            # Create plots directory if it doesn't exist
            plots_dir = Path(os.getcwd()) / "data" / "plots"
            os.makedirs(plots_dir, exist_ok=True)
            save_path = plots_dir / f"comparison_{metrics}.png"

        plt.savefig(save_path)

        if show:
            plt.show()

        return save_path
