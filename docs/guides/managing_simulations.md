# Managing Simulation Data

This guide explains how to effectively manage simulation data in the InfoFlow system, including listing, exporting, comparing, and deleting simulation runs.

## Understanding Simulation Data Storage

InfoFlow stores simulation data in several locations:

1. **SQLite Database**: Primary storage in `data/simulation_stats.db`
   - Contains run metadata and time series metrics
   - Used by the web interface to display simulation history
   
2. **JSON Exports**: Optional exports in `data/exports/`
   - Contains complete simulation data including parameters and metrics
   - Created when explicitly exporting a simulation

3. **Generated Charts**: Visual outputs in `data/plots/` and web static directory
   - Contains visualizations of simulation metrics
   - Automatically generated during simulation and when viewing results

## Listing Simulation Runs

You can list recent simulation runs using the `delete_runs.py` utility:

```bash
# List 20 most recent simulation runs (default)
python delete_runs.py --list

# List a specific number of recent runs
python delete_runs.py --list --limit 50
```

This will display a table with the following information:
- Run ID (unique identifier for each simulation)
- Timestamp (when the simulation was run)
- Steps (number of simulation steps completed)
- Name (custom name if assigned, otherwise "Unnamed simulation")

## Exporting Simulation Data

You can export simulation data for analysis or backup:

### Through the Web Interface

1. Navigate to the Simulation History page
2. Find the simulation you want to export
3. Click "Export" and choose either JSON or HTML format

### Using Scripts

```bash
# Export a specific run to JSON
python scripts/compare_runs.py --export RUN_ID
```

## Comparing Simulation Runs

To compare the results of different simulation runs:

```bash
# Compare two runs on a specific metric
python scripts/compare_runs.py RUN_ID1 RUN_ID2 --metric avg_trust_government

# Compare multiple runs
python scripts/compare_runs.py RUN_ID1 RUN_ID2 RUN_ID3 --metric avg_truth_assessment
```

This will generate comparative charts showing how the selected metric evolved over time in each simulation.

## Deleting Simulation Runs

The `delete_runs.py` utility provides several options for cleaning up your simulation database:

```bash
# Delete a specific run by ID
python delete_runs.py --delete RUN_ID

# Delete the 10 most recent runs
python delete_runs.py --clear-recent

# Delete all simulation runs (with confirmation prompt)
python delete_runs.py --delete-all

# Delete all simulation runs without confirmation
python delete_runs.py --delete-all --force
```

### When to Delete Simulation Runs

Consider deleting simulation runs in these situations:

1. **Test or Debug Runs**: After verifying your simulation setup
2. **Parameter Exploration**: When you've completed parameter exploration and identified optimal settings
3. **Database Performance**: If you notice the web interface slowing down due to too many runs
4. **Disk Space Concerns**: If simulation data is consuming too much storage

### Best Practices

1. **Export Before Deleting**: Consider exporting important runs before deletion
2. **Document Run IDs**: Keep a record of important run IDs and their parameters
3. **Regular Maintenance**: Periodically clean up test and exploratory runs
4. **Use Clear Names**: Name your important simulations to easily identify them later

## Integration with Research Workflow

When conducting research with InfoFlow, consider this workflow:

1. **Setup Phase**: 
   - Run initial test simulations to validate your setup
   - Delete these runs when done

2. **Exploration Phase**:
   - Run parameter exploration simulations
   - Export important findings
   - Delete exploratory runs to keep the database clean

3. **Analysis Phase**:
   - Run final simulations with optimized parameters
   - Keep these runs in the database for detailed analysis
   - Export final runs as JSON for long-term storage

4. **Reporting Phase**:
   - Export final runs as HTML for sharing
   - Delete any unnecessary intermediate runs

This approach helps maintain a clean, performant simulation environment while preserving important research data.

## Technical Details

### Database Schema

The simulation database contains two main tables:

1. `simulation_runs`: Stores metadata for each run
   - `run_id`: Unique identifier
   - `timestamp`: When the run was created
   - `name`: Optional user-provided name
   - `parameters`: JSON-encoded simulation parameters
   - `steps`: Number of simulation steps performed

2. `timestep_data`: Stores metrics at each simulation step
   - `run_id`: Identifies which run the data belongs to
   - `step`: Simulation step number
   - `metrics`: JSON-encoded metrics for that step

### Data Deletion Process

When a run is deleted:

1. All entries for that run in the `timestep_data` table are removed
2. The corresponding metadata in the `simulation_runs` table is removed
3. No automatic deletion of exported files occurs (they must be manually deleted if needed)