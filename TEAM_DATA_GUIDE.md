# InfoFlow Team Data Guide

This guide explains how to effectively share and analyze InfoFlow simulation data with your team.

## Quick Start for Team Members

1. **Access the simulation**:
   - The web interface is running at [http://localhost:5001](http://localhost:5001)
   - You can run simulations or view existing ones

2. **Export data**:
   - After viewing a simulation, use the `Export CSV` button 
   - Files are saved in the `experiments/exports/` directory

3. **Analyze in your preferred tool**:
   - CSV files can be opened directly in Excel, Google Sheets, R, or Python
   - The data is in time-series format with one row per simulation step

## Understanding the CSV Format

Each CSV export contains:

- **step**: The simulation step number
- **run_id**: Unique identifier for the simulation run
- **timestamp**: When the simulation was run
- **name**: The name given to the simulation
- **parameters**: Various simulation parameters (network_type, num_citizens, etc.)
- **metrics**: Various metrics collected at each step:
  - `avg_trust_government`: Average trust in government sources (0-10)
  - `avg_trust_corporate`: Average trust in corporate media (0-10) 
  - `avg_trust_influencer`: Average trust in social media influencers (0-10)
  - `avg_truth_assessment`: Average accuracy of user beliefs (0-1)
  - `polarization_index`: Measure of belief polarization (0-1)

## Using the CSV Analysis Tools

The project includes CSV analysis tools for common tasks:

```bash
# Plot a single metric from a simulation
python experiments/analysis/csv_analyzer.py plot path/to/simulation.csv --metric avg_truth_assessment

# Compare the same metric across multiple simulations
python experiments/analysis/csv_analyzer.py compare \
  simulation1.csv simulation2.csv simulation3.csv \
  --metric avg_trust_government

# Generate a summary report of all simulations
python experiments/analysis/csv_analyzer.py summary \
  experiments/data/trust-experiments/*.csv \
  --output summary_report.csv

# Analyze information spread metrics
python experiments/analysis/csv_analyzer.py source-spread experiments/data/trust-experiments/high-trust-1.csv --show

# Compare truth vs. falsehood spread
python experiments/analysis/csv_analyzer.py truth-vs-falsehood experiments/data/trust-experiments/*.csv --show

# Organize exported CSV files
python experiments/analysis/organize_csv.py --all

# List available experiment data 
python experiments/analysis/list_data.py
```

## Analysis in Excel

1. **Open the CSV file** directly in Excel
2. **Create charts** by selecting columns and using the Insert > Chart menu
3. **Pivot tables** can be used to aggregate data across steps

## Analysis in Python

```python
import pandas as pd
import matplotlib.pyplot as plt

# Load the data
df = pd.read_csv('path/to/simulation.csv')

# Plot trust evolution
plt.figure(figsize=(10, 6))
plt.plot(df['step'], df['avg_trust_government'], label='Government')
plt.plot(df['step'], df['avg_trust_corporate'], label='Corporate')
plt.plot(df['step'], df['avg_trust_influencer'], label='Influencer')
plt.title('Trust Evolution')
plt.xlabel('Simulation Step')
plt.ylabel('Average Trust (0-10)')
plt.legend()
plt.grid(True)
plt.show()

# Calculate final metrics
final_step = df['step'].max()
final_metrics = df[df['step'] == final_step].iloc[0]
print(f"Final Truth Assessment: {final_metrics['avg_truth_assessment']:.3f}")
print(f"Final Polarization: {final_metrics['polarization_index']:.3f}")
```

## Analysis in R

```r
# Load libraries
library(tidyverse)
library(ggplot2)

# Read the data
data <- read_csv('path/to/simulation.csv')

# Plot trust evolution
ggplot(data, aes(x = step)) +
  geom_line(aes(y = avg_trust_government, color = "Government")) +
  geom_line(aes(y = avg_trust_corporate, color = "Corporate")) +
  geom_line(aes(y = avg_trust_influencer, color = "Influencer")) +
  labs(title = "Trust Evolution", x = "Simulation Step", y = "Average Trust (0-10)") +
  theme_minimal() +
  scale_color_manual(values = c("Government" = "#8B0000", "Corporate" = "#00008B", "Influencer" = "#006400"))
```

## Comparing Multiple Simulations

To compare multiple simulations, you can either:

1. **Use the CSV analyzer tool**:
   ```bash
   python experiments/analysis-tools/csv_analyzer.py compare sim1.csv sim2.csv sim3.csv --metric avg_truth_assessment
   ```

2. **Load multiple files in your analysis tool**:
   ```python
   # Python example
   import pandas as pd
   import matplotlib.pyplot as plt
   
   # Load multiple files
   sim1 = pd.read_csv('sim1.csv')
   sim2 = pd.read_csv('sim2.csv')
   sim3 = pd.read_csv('sim3.csv')
   
   # Add identifying column
   sim1['simulation'] = 'High Trust'
   sim2['simulation'] = 'Moderate Trust'
   sim3['simulation'] = 'Low Trust'
   
   # Combine data
   combined = pd.concat([sim1, sim2, sim3])
   
   # Create comparison plot
   plt.figure(figsize=(12, 6))
   for name, group in combined.groupby('simulation'):
       plt.plot(group['step'], group['avg_truth_assessment'], label=name)
   
   plt.title('Truth Assessment Comparison')
   plt.xlabel('Simulation Step')
   plt.ylabel('Average Truth Assessment (0-1)')
   plt.legend()
   plt.grid(True)
   plt.show()
   ```

## Need Help?

If you have questions about analyzing the data or need help with specific analyses, please contact:

Shingai Thornton  
Email: rthornton@binghamton.edu