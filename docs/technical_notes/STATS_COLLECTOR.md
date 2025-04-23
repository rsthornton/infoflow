# InfoFlow Stats Collector Implementation

## Overview

The InfoFlow Stats Collector is a lightweight, efficient system for tracking simulation results and enabling comparisons between runs. This component has been crucial to our debugging and refinement of the trust dynamics system.

## Current Status

The Stats Collector is now fully implemented and integrated with the InfoFlow model. It has been instrumental in:

1. **Identifying the Trust Dynamics Issue**: The collection of trust metrics over time allowed us to identify that trust values were remaining static throughout simulations.

2. **Verifying Fix Implementation**: After implementing fixes to the media agent tracking, the Stats Collector confirmed that trust values now change appropriately based on content received.

3. **Parameter Impact Analysis**: The system allows us to compare how different parameters affect trust evolution, validating that our model responds as expected to parameter changes.

## Key Components

### 1. Stats Tracking & Storage

- Simple SQLite database with two tables:
  - `simulation_runs`: Metadata about each run
  - `timestep_data`: Time series metrics for each step
- JSON export/import capability for sharing results

### 2. Core Implementation

```python
# simple_stats.py

import sqlite3
import json
import time
import uuid
import os

class StatsCollector:
    def __init__(self, db_path="simulation_stats.db"):
        # Create database if it doesn't exist
        self.db_path = db_path
        self.run_id = str(uuid.uuid4())[:8]
        self.init_db()
        
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create tables if they don't exist
        c.execute('''
        CREATE TABLE IF NOT EXISTS simulation_runs (
            run_id TEXT PRIMARY KEY,
            timestamp TEXT,
            name TEXT,
            parameters TEXT,
            steps INTEGER
        )
        ''')
        
        c.execute('''
        CREATE TABLE IF NOT EXISTS timestep_data (
            run_id TEXT,
            step INTEGER,
            metric_name TEXT,
            value REAL,
            PRIMARY KEY (run_id, step, metric_name)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def start_run(self, parameters):
        """Record the start of a new simulation run"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Store run metadata
        c.execute(
            "INSERT INTO simulation_runs VALUES (?, ?, ?, ?, ?)",
            (self.run_id, time.strftime("%Y-%m-%d %H:%M:%S"), "", json.dumps(parameters), 0)
        )
        
        conn.commit()
        conn.close()
        
        return self.run_id
    
    def record_step(self, step, metrics):
        """Record metrics for a simulation step"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Update step count
        c.execute(
            "UPDATE simulation_runs SET steps = MAX(steps, ?) WHERE run_id = ?",
            (step, self.run_id)
        )
        
        # Store each metric
        for name, value in metrics.items():
            c.execute(
                "INSERT OR REPLACE INTO timestep_data VALUES (?, ?, ?, ?)",
                (self.run_id, step, name, value)
            )
        
        conn.commit()
        conn.close()
    
    def name_run(self, name):
        """Add a name to the current run"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(
            "UPDATE simulation_runs SET name = ? WHERE run_id = ?",
            (name, self.run_id)
        )
        
        conn.commit()
        conn.close()
    
    @staticmethod
    def get_recent_runs(limit=10):
        """Get metadata for recent simulation runs"""
        conn = sqlite3.connect("simulation_stats.db")
        c = conn.cursor()
        
        c.execute(
            "SELECT run_id, timestamp, name, steps FROM simulation_runs ORDER BY timestamp DESC LIMIT ?",
            (limit,)
        )
        
        runs = [{"id": r[0], "timestamp": r[1], "name": r[2], "steps": r[3]} for r in c.fetchall()]
        
        conn.close()
        return runs
    
    @staticmethod
    def get_run_data(run_id):
        """Get complete data for a specific run"""
        conn = sqlite3.connect("simulation_stats.db")
        c = conn.cursor()
        
        # Get run metadata
        c.execute("SELECT * FROM simulation_runs WHERE run_id = ?", (run_id,))
        meta = c.fetchone()
        
        if not meta:
            conn.close()
            return None
        
        # Get metrics
        c.execute(
            "SELECT step, metric_name, value FROM timestep_data WHERE run_id = ? ORDER BY step",
            (run_id,)
        )
        
        # Organize by step
        metrics = {}
        for step, name, value in c.fetchall():
            if step not in metrics:
                metrics[step] = {}
            metrics[step][name] = value
        
        conn.close()
        
        return {
            "id": meta[0],
            "timestamp": meta[1],
            "name": meta[2],
            "parameters": json.loads(meta[3]),
            "steps": meta[4],
            "metrics": metrics
        }
    
    @staticmethod
    def export_run(run_id, filepath=None):
        """Export run data to JSON file"""
        data = StatsCollector.get_run_data(run_id)
        
        if not data:
            return False
        
        if not filepath:
            filepath = f"simulation_{run_id}.json"
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        return filepath
```

### 3. Model Integration

The StatsCollector is now fully integrated with the InformationFlowModel:

```python
def __init__(self, ...):
    # Existing code...
    self.stats = StatsCollector()
    self.stats.start_run(self._get_parameters_dict())
    
def _get_parameters_dict(self):
    return {
        "num_citizens": self.num_citizens,
        "network_type": self.network_type,
        "corporate_publication_rate": self.media_params.get("corporate_publication_rate", 0.9),
        "influencer_publication_rate": self.media_params.get("influencer_publication_rate", 1.0),
        "government_publication_rate": self.media_params.get("government_publication_rate", 0.9),
        "corporate_influence_reach": self.media_params.get("corporate_influence_reach", 0.9),
        "influencer_influence_reach": self.media_params.get("influencer_influence_reach", 0.7),
        "government_influence_reach": self.media_params.get("government_influence_reach", 0.8),
        # Other parameters...
    }

def step(self):
    # Existing step logic...
    
    # Record metrics
    metrics = {
        "avg_trust_corporate": np.mean([a.trust_levels.get("CorporateMediaAgent", 5.0) for a in self.citizens]),
        "avg_trust_influencer": np.mean([a.trust_levels.get("InfluencerAgent", 5.0) for a in self.citizens]),
        "avg_trust_government": np.mean([a.trust_levels.get("GovernmentMediaAgent", 5.0) for a in self.citizens]),
        "avg_truth_assessment": np.mean([a.truth_assessment for a in self.citizens]),
        "truth_assessment_var": np.var([a.truth_assessment for a in self.citizens]),
        "trust_corporate_var": np.var([a.trust_levels.get("CorporateMediaAgent", 5.0) for a in self.citizens]),
        "trust_influencer_var": np.var([a.trust_levels.get("InfluencerAgent", 5.0) for a in self.citizens]),
        "trust_government_var": np.var([a.trust_levels.get("GovernmentMediaAgent", 5.0) for a in self.citizens])
    }
    self.stats.record_step(self.steps, metrics)
```

### 4. Analysis Tools

We've implemented several tools for analyzing simulation results:

1. **Comparison Script**:
```python
# compare_runs.py
from infoflow.utils.simple_stats import StatsCollector
import matplotlib.pyplot as plt
import sys

def plot_comparison(run_ids, metric=None):
    metrics = metric or "avg_trust_government"
    runs = []
    
    for run_id in run_ids:
        data = StatsCollector.get_run_data(run_id)
        if data:
            runs.append(data)
            
    if not runs:
        print("No valid run data found")
        return
        
    plt.figure(figsize=(10, 6))
    
    for run in runs:
        steps = []
        values = []
        
        for step, step_metrics in run['metrics'].items():
            if metrics in step_metrics:
                steps.append(int(step))
                values.append(step_metrics[metrics])
                
        label = f"{run['name'] or run['id']} ({len(steps)} steps)"
        plt.plot(steps, values, label=label)
        
    plt.title(f"Comparison of {metrics}")
    plt.xlabel("Step")
    plt.ylabel("Value")
    plt.legend()
    plt.grid(True)
    plt.tight_layout()
    plt.savefig(f"comparison_{metrics}.png")
    plt.show()
```

2. **API Endpoints**:
```python
@bp.route('/api/simulation-runs', methods=['GET'])
def get_simulation_runs():
    """Get list of recent simulation runs"""
    runs = StatsCollector.get_recent_runs(limit=20)
    return jsonify({"status": "success", "data": runs})

@bp.route('/api/simulation-data/<run_id>', methods=['GET'])
def get_simulation_data(run_id):
    """Get full data for a simulation run"""
    data = StatsCollector.get_run_data(run_id)
    if not data:
        return jsonify({"status": "error", "message": "Run not found"}), 404
    return jsonify({"status": "success", "data": data})
```

3. **Export Functionality**:
```python
# Export the latest run to a JSON file
StatsCollector.export_run(latest_run_id, "data/exports/latest_run.json")
```

## Key Insights from Stats Collection

The Stats Collector has provided several key insights:

1. **Trust Dynamics Patterns**:
   - Trust values show clear responses to media content accuracy
   - Government trust increases on average due to higher truth commitment
   - Corporate trust decreases on average with low truth commitment

2. **Parameter Sensitivity**:
   - Publication rates significantly impact trust evolution speed
   - Influence reach affects how many agents receive content
   - Truth commitment is the primary driver of trust direction

3. **Population Variance**:
   - Trust levels have measurable variance across the population
   - Variances increase over time as agents have different experiences
   - Individual differences in critical thinking create different trust trajectories

## Future Enhancements

Based on our experience using the Stats Collector for debugging, we plan to implement the following enhancements:

1. **Advanced Visualization**:
   - Add histograms showing distribution of trust values
   - Create heatmaps of parameter sensitivity
   - Implement time-series animations for trust evolution

2. **Parameter Exploration**:
   - Add automated parameter sweeps
   - Implement sensitivity analysis tools
   - Create optimization algorithms for finding parameter combinations

3. **Statistical Analysis**:
   - Add correlation analysis between parameters and outcomes
   - Implement significance testing for parameter effects
   - Create predictive models for trust evolution

## Conclusion

The Stats Collector has proven to be an invaluable tool for debugging and refining the InfoFlow model. It provided the data needed to identify and fix the trust dynamics issue, and continues to offer insights into how different parameters affect simulation outcomes.

With the trust dynamics now functioning correctly, we can use the Stats Collector to explore more complex questions about information flow and trust evolution in social networks.