# InfoFlow Experiment Guide

This guide provides instructions for conducting systematic experiments using the InfoFlow social media simulation. It works in conjunction with the detailed parameters in the `research-parameter-guide.md` document in the project root.

## Getting Started with Experiments

1. **Launch the InfoFlow web interface**:
   ```bash
   python run_server.py
   ```

2. **Navigate to the "Run Simulation" tab** in your browser at http://127.0.0.1:5001

3. **Load a baseline scenario** from the dropdown menu or configure parameters manually

## Using the Content Flow Visualization

One of the most powerful features of the InfoFlow simulation is the content flow visualization, which makes information spread visible and analyzable.

### Understanding the Visualization Legend

The content flow visualization uses a dual encoding system:

1. **Line Colors** indicate content accuracy:
   - **Green** lines = True content (accuracy ≥ 70%)
   - **Yellow** lines = Fuzzy content (accuracy between 30-70%)
   - **Red** lines = False content (accuracy ≤ 30%)

2. **Line Styles** indicate content source:
   - **Solid** lines = Corporate Media sources
   - **Dashed** lines = Influencer sources
   - **Dotted** lines = Government sources

This dual encoding allows you to simultaneously track both the accuracy of information and its source as it spreads through the network.

### Visualization Modes

The simulation offers three different perspectives on content flow:

1. **Overview Mode**: Shows all content paths simultaneously
   - Best for comparing different content items
   - Useful for identifying which content spread furthest

2. **Time-Step Mode**: Shows network state at each simulation step
   - Best for seeing how the network evolves over time
   - Shows which content appears at which simulation step

3. **Hop-by-Hop Mode**: Shows content spreading node by node
   - Best for detailed analysis of a single content's spread
   - Allows step-by-step tracking of how information propagates

Switch between these modes using the buttons in the visualization interface.

## Experimental Approaches

### 1. Content Source Comparison

To compare how content from different sources spreads:

1. Load the `trust_study.json` scenario
2. Select the "Overview" mode in the visualization
3. Use the content type selector to choose "All Content Types"
4. Observe the different line styles (solid/dashed/dotted) representing different sources
5. Note which sources' content spreads furthest and fastest

### 2. Network Structure Impact

To examine how network topology affects content spread:

1. Run simulations with different network types (small world, scale free, random)
2. For each network type, run the simulation with all other parameters identical
3. Switch to "Time-Step" mode and use the timeline slider
4. Compare how quickly content reaches various parts of the network
5. Note whether certain content types (based on color) spread differently in different networks

### 3. Belief Resistance Analysis

To study how cognitive factors affect belief updates:

1. Run simulations with different cognitive profiles (from research-parameter-guide.md)
2. For each profile, analyze how content of different accuracies propagates
3. Compare time steps required for content to reach similar penetration
4. Note whether high confirmation bias populations are more resistant to accurate information

## Data Collection and Export

After running experiments, capture your findings:

1. **Export Visualization**: Use the "Export SVG" button to save the network visualization
2. **Export Charts**: Each chart has an export button for saving as PNG
3. **Export CSV Data**: Use the "Export CSV" button to save simulation data for structured analysis (recommended)
4. **Export JSON Data**: Use the "Export JSON" button to save complete simulation data if needed
5. **Export HTML**: For shareable results, use the "Export HTML" button to create a self-contained HTML file

### CSV Analysis Workflow

The new CSV-based analysis framework simplifies the research workflow:

1. **Export CSV files** to the `experiments/exports` directory using the "Export CSV" button
2. **Organize files** using the CSV organizer:
   ```bash
   python experiments/analysis/organize_csv.py --all
   ```
3. **List available data** to see what you have to work with:
   ```bash
   python experiments/analysis/list_data.py
   ```
4. **Analyze specific metrics** for individual experiments:
   ```bash
   python experiments/analysis/csv_analyzer.py plot experiments/data/trust-experiments/high-trust-1.csv --metric avg_trust_government --show
   ```
5. **Compare metrics** across multiple experiments:
   ```bash
   python experiments/analysis/csv_analyzer.py compare experiments/data/trust-experiments/*.csv --metric avg_truth_assessment --show
   ```
6. **Analyze information spread** patterns:
   ```bash
   python experiments/analysis/csv_analyzer.py source-spread experiments/data/trust-experiments/high-trust-1.csv --show
   ```
7. **Compare truth vs. falsehood spread**:
   ```bash
   python experiments/analysis/csv_analyzer.py truth-vs-falsehood experiments/data/trust-experiments/*.csv --show
   ```
8. **Run research-focused analysis**:
   ```bash
   python experiments/analysis/research_analysis.py trust-analysis
   ```

## Advanced Analysis Tips

1. **Individual Agent Tracking**: Select specific agents in the network to see their metrics evolution
2. **Comparison Across Runs**: Use the timestamps and exported data to compare different experiment configurations
3. **Pattern Identification**: Look for recurring patterns in how information spreads in different conditions
4. **Parameter Sensitivity**: Systematically vary one parameter at a time to understand its impact

## Example Experiment Workflow

Here's a complete workflow for investigating institutional trust impact:

1. Load the `trust_study.json` scenario
2. Run the simulation
3. Switch to "Overview" mode and select "All Content Types"
4. Export a screenshot of the network visualization
5. Switch to the Charts tab and export trust evolution charts
6. Modify the trust parameters according to the "Low Trust Environment" settings in the research-parameter-guide.md
7. Run again with the new parameters
8. Compare the visualizations and charts from both runs
9. Document your observations about how different trust levels affected content spread

By following systematic experimental approaches and leveraging the visualization capabilities, you can gain valuable insights into social media information dynamics.