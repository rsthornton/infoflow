# CSV Analyzer for InfoFlow

This tool provides comprehensive analysis capabilities for InfoFlow experiment data in CSV format.

## Features

- Plot metrics from CSV files
- Compare metrics across multiple experiments
- Analyze information spread by content accuracy (true/fuzzy/false)
- Compare information spread by source type
- Compare truth vs. falsehood spread across experiments
- Generate summary reports of experiment data

## Commands

- `plot`: Plot a metric from a CSV file
- `compare`: Compare a metric across multiple CSV files
- `spread`: Display information spread visualizations
- `source-spread`: Compare spread effectiveness across different source types
- `accuracy-spread`: Compare spread by content accuracy (true/false/fuzzy)
- `truth-vs-falsehood`: Analyze how truth spreads compared to falsehood
- `summary`: Generate a summary report of key metrics

## Usage Examples

```bash
# Plot a single metric
python csv_analyzer.py plot path/to/experiment.csv --metric avg_truth_assessment --show

# Compare a metric across experiments
python csv_analyzer.py compare path/to/experiment1.csv path/to/experiment2.csv --metric avg_trust_government

# Analyze information spread
python csv_analyzer.py spread path/to/experiment.csv --show

# Compare source spread effectiveness
python csv_analyzer.py source-spread path/to/experiment.csv --show

# Analyze content accuracy spread
python csv_analyzer.py accuracy-spread path/to/experiment.csv --show

# Compare truth vs. falsehood
python csv_analyzer.py truth-vs-falsehood path/to/experiment1.csv path/to/experiment2.csv --show

# Generate a summary report
python csv_analyzer.py summary path/to/experiment1.csv path/to/experiment2.csv --output summary.csv
```
