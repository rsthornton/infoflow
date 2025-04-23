# InfoFlow CSV-Based Experiment Framework

This directory contains the streamlined CSV-based experiment framework for InfoFlow research.

## Directory Structure

```
experiments/
├── analysis/                  # Analysis tools
│   ├── csv_analyzer.py        # Enhanced CSV analyzer (central tool)
│   ├── list_data.py           # Data inventory tool
│   ├── organize_csv.py        # CSV file organizer
│   └── research_analysis.py   # Research question analysis tool
├── data/                      # All experiment data
│   ├── trust-experiments/     # Trust-related experiment data
│   ├── network-experiments/   # Network structure experiment data
│   └── cognitive-experiments/ # Cognitive factor experiment data
├── exports/                   # Temporary location for CSV exports from the web interface
├── visualizations/            # Generated visualizations
├── GUIDE.md                   # User guide for the new system
└── research-questions.md      # Core research questions
```

## Workflow

1. **Run experiments** in the web interface
2. **Export CSV files** to the `exports` directory
3. **Organize files** using `organize_csv.py`
4. **Analyze data** using the CSV analyzer

## CSV Analyzer Capabilities

The CSV analyzer (experiments/analysis/csv_analyzer.py) provides comprehensive analysis features:

- Plot metrics from CSV files
- Compare metrics across multiple experiments
- Analyze information spread by content accuracy (true/fuzzy/false)
- Compare information spread by source type
- Compare truth vs. falsehood spread across experiments
- Generate summary reports of experiment data

## Usage Examples

```bash
# Plot a metric from a CSV file
python experiments/analysis/csv_analyzer.py plot experiments/data/trust-experiments/high-trust-1.csv --metric avg_truth_assessment --show

# Compare a metric across multiple CSV files
python experiments/analysis/csv_analyzer.py compare experiments/data/trust-experiments/*.csv --metric avg_trust_government

# Analyze spread by content accuracy
python experiments/analysis/csv_analyzer.py accuracy-spread experiments/data/trust-experiments/high-trust-1.csv

# Compare information spread by source type
python experiments/analysis/csv_analyzer.py source-spread experiments/data/network-experiments/large-network-3.csv

# Compare truth vs. falsehood spread
python experiments/analysis/csv_analyzer.py truth-vs-falsehood experiments/data/trust-experiments/*.csv

# Generate a summary report
python experiments/analysis/csv_analyzer.py summary experiments/data/trust-experiments/*.csv --output experiments/visualizations/trust_summary.csv
```

## Research Questions

1. **What is the relationship between institutional trust and a healthy social media information ecosystem?**
   - Use trust-experiments data and compare trust levels with truth assessment metrics
   - Analyze how trust affects information spread and belief accuracy

2. **How does the amount, and the types of connectivity in social media networks influence how information spreads?**
   - Use network-experiments data to analyze spread patterns in different network structures
   - Compare information propagation speed and reach across network topologies

3. **How does resistance to update one's beliefs affect information trust evaluation?**
   - Use cognitive-experiments data to analyze belief resistance effects
   - Compare how different cognitive parameters influence truth assessment

## Data Management

After running experiments, use the organizer script to place your CSV files in the correct directories:

```bash
# Organize all CSV files in the exports directory
python experiments/analysis/organize_csv.py --all

# Check your available data
python experiments/analysis/list_data.py
```

## Research Analysis

For automated analysis aligned with research questions:

```bash
# Analyze the trust research question
python experiments/analysis/research_analysis.py trust-analysis

# Analyze the network research question
python experiments/analysis/research_analysis.py network-analysis

# Analyze the belief resistance research question
python experiments/analysis/research_analysis.py belief-analysis

# Generate comprehensive reports for all questions
python experiments/analysis/research_analysis.py generate-report
```