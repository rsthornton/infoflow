# InfoFlow Experiment Guide

This guide outlines how to use the new CSV-based experiment framework to answer our research questions.

## Research Questions

1. **What is the relationship between institutional trust and a healthy social media information ecosystem?**
2. **How does the amount, and the types of connectivity in social media networks influence how information spreads?**
3. **How does resistance to update one's beliefs affect information trust evaluation?**

## Simplified Workflow

### 1. Run Simulations and Export CSV

Use the InfoFlow web interface to run simulations:

1. Start the server: `python run_server.py`
2. Configure and run your experiment using the web interface
3. Export your results as a CSV file

### 2. Organize Your Data

Place your CSV files into the appropriate directory:

```
experiments/data/trust-experiments/      # For trust-related experiments
experiments/data/network-experiments/    # For network structure experiments
experiments/data/cognitive-experiments/  # For cognitive parameter experiments
```

You can use the automated organizer to help:

```bash
# Organize a specific CSV file
python experiments/analysis/organize_csv.py path/to/your/file.csv

# Organize all CSVs in the export directories
python experiments/analysis/organize_csv.py --all
```

### 3. Analyze Your Data

#### Basic Analysis

```bash
# Plot a specific metric
python experiments/analysis/csv_analyzer.py plot experiments/data/trust-experiments/your-file.csv --metric avg_trust_government --show

# Compare metrics across experiments
python experiments/analysis/csv_analyzer.py compare experiments/data/trust-experiments/*.csv --metric avg_truth_assessment --show

# Generate a summary report
python experiments/analysis/csv_analyzer.py summary experiments/data/trust-experiments/*.csv --output summary.csv
```

#### Information Spread Analysis

```bash
# Analyze all information spread metrics
python experiments/analysis/csv_analyzer.py spread experiments/data/trust-experiments/your-file.csv --show

# Compare spread by content accuracy (true/false/fuzzy)
python experiments/analysis/csv_analyzer.py accuracy-spread experiments/data/trust-experiments/your-file.csv --show

# Compare spread by source type
python experiments/analysis/csv_analyzer.py source-spread experiments/data/trust-experiments/your-file.csv --show

# Compare truth vs. falsehood spread across experiments
python experiments/analysis/csv_analyzer.py truth-vs-falsehood experiments/data/trust-experiments/*.csv --show
```

#### Research Question Analysis

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

### 4. Interpret Results

When analyzing your results, focus on:

- **Trust experiments**: Look for relationships between trust levels and truth assessment metrics
- **Network experiments**: Look for patterns in how information spreads through different network structures
- **Cognitive experiments**: Look for how different cognitive parameters affect belief accuracy

## CSV Metrics to Focus On

### Trust Research

- `avg_trust_government`, `avg_trust_corporate`, `avg_trust_influencer`
- `avg_truth_assessment`
- `avg_spread_true_content`, `avg_spread_false_content`

### Network Research

- `avg_content_spread`, `max_content_spread`
- `viral_content_count`
- `avg_spread_CorporateMediaAgent`, `avg_spread_InfluencerAgent`, `avg_spread_GovernmentMediaAgent`

### Belief Research

- `avg_spread_true_content` vs. `avg_spread_false_content`
- `accuracy_spread_correlation`
- Metrics related to cognitive parameters

## Generating Research Reports

The framework includes tools to generate comprehensive reports that directly address our research questions:

```bash
python experiments/analysis/research_analysis.py generate-report
```

This will create visualizations and summary CSV files in the `experiments/visualizations/` directory, organized by research area.