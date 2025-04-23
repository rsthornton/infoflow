#!/usr/bin/env python
"""
CSV Experiment Analyzer for InfoFlow

This tool provides simple analysis capabilities for CSV experiment files, including:
- Loading simulation metrics from CSV exports
- Generating plots and visualizations
- Comparing multiple experiments
- Converting between JSON and CSV formats

Usage:
  python csv_analyzer.py [command] [options]
"""

import os
import sys
import json
import glob
import argparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import re
import csv

# Add project root to PATH for imports
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.abspath(os.path.join(script_dir, "../.."))
sys.path.append(project_root)

class CSVAnalyzer:
    """Analyzer for InfoFlow experiment CSV files."""
    
    def __init__(self):
        """Initialize the analyzer."""
        self.experiment_base_dir = os.path.join(project_root, "experiments")
        self.output_dir = os.path.join(self.experiment_base_dir, "analysis-tools", "outputs")
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Color schemes for consistent visualization
        self.colors = {
            'trust': {
                'government': '#8B0000',  # Dark red
                'corporate': '#00008B',   # Dark blue
                'influencer': '#006400'   # Dark green
            },
            'truth': '#FF8C00',  # Dark orange
            'polarization': '#800080',  # Purple
            
            # For comparing multiple runs
            'run_colors': [
                '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', 
                '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22', '#17becf'
            ]
        }
        
    def load_csv(self, file_path):
        """Load experiment data from a CSV file."""
        try:
            df = pd.read_csv(file_path)
            return df
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return None
    
    def csv_to_json(self, csv_path, json_path=None):
        """Convert a CSV export to JSON format."""
        df = self.load_csv(csv_path)
        if df is None:
            return False
            
        # If no output path specified, use the same name but with .json extension
        if json_path is None:
            json_path = os.path.splitext(csv_path)[0] + ".json"
            
        try:
            # Extract run metadata
            run_id = df['run_id'].iloc[0] if 'run_id' in df.columns else "unknown"
            timestamp = df['timestamp'].iloc[0] if 'timestamp' in df.columns else ""
            name = df['name'].iloc[0] if 'name' in df.columns else ""
            
            # Create the JSON structure
            data = {
                "id": run_id,
                "timestamp": timestamp,
                "name": name,
                "parameters": {},
                "steps": int(df['step'].max()),
                "metrics": {}
            }
            
            # Extract parameters (they're the same for all rows)
            param_columns = [col for col in df.columns if col not in ['step', 'run_id', 'timestamp', 'name']]
            for col in param_columns:
                # Try to identify parameters vs metrics
                if col.startswith('avg_') or col in ['polarization_index', 'trust_var_government', 
                                                     'trust_var_corporate', 'trust_var_influencer']:
                    # This is a metric, not a parameter
                    continue
                
                # Add to parameters if value exists
                if len(df) > 0:
                    val = df[col].iloc[0]
                    if not pd.isna(val):
                        # Try to convert to appropriate type
                        try:
                            if isinstance(val, str) and val.lower() in ['true', 'false']:
                                data["parameters"][col] = val.lower() == 'true'
                            elif isinstance(val, str) and val.isdigit():
                                data["parameters"][col] = int(val)
                            elif isinstance(val, str) and is_float(val):
                                data["parameters"][col] = float(val)
                            else:
                                data["parameters"][col] = val
                        except:
                            data["parameters"][col] = val
            
            # Extract metrics for each step
            metric_columns = [col for col in df.columns if col.startswith('avg_') or 
                              col in ['polarization_index', 'trust_var_government', 'trust_var_corporate', 'trust_var_influencer']]
            
            for _, row in df.iterrows():
                step = str(int(row['step']))
                data["metrics"][step] = {}
                
                for metric in metric_columns:
                    if metric in row and not pd.isna(row[metric]):
                        data["metrics"][step][metric] = row[metric]
            
            # Write JSON file with NumPy types handled
            with open(json_path, 'w') as f:
                # Define a custom serializer that handles NumPy types
                class NumpyEncoder(json.JSONEncoder):
                    def default(self, obj):
                        if isinstance(obj, (np.integer, np.int64)):
                            return int(obj)
                        elif isinstance(obj, (np.floating, np.float64)):
                            return float(obj)
                        elif isinstance(obj, np.ndarray):
                            return obj.tolist()
                        return super().default(obj)
                
                json.dump(data, f, indent=2, cls=NumpyEncoder)
                
            print(f"Converted {csv_path} to {json_path}")
            return json_path
            
        except Exception as e:
            print(f"Error converting CSV to JSON: {e}")
            return False
    
    def json_to_csv(self, json_path, csv_path=None):
        """Convert a JSON simulation file to CSV format."""
        try:
            with open(json_path, 'r') as f:
                data = json.load(f)
                
            # If no output path specified, use the same name but with .csv extension
            if csv_path is None:
                csv_path = os.path.splitext(json_path)[0] + ".csv"
            
            # Extract parameters
            params = data.get("parameters", {})
            
            # Create rows for CSV
            rows = []
            
            if "metrics" in data and data["metrics"]:
                for step, metrics in sorted(data["metrics"].items(), key=lambda x: int(x[0])):
                    row = {
                        "step": step,
                        "run_id": data.get("id", ""),
                        "timestamp": data.get("timestamp", ""),
                        "name": data.get("name", "")
                    }
                    
                    # Add parameters
                    for param_name, param_value in params.items():
                        row[param_name] = param_value
                    
                    # Add metrics
                    for metric_name, metric_value in metrics.items():
                        row[metric_name] = metric_value
                    
                    rows.append(row)
            
            # Create DataFrame and save as CSV
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(csv_path, index=False)
                print(f"Converted {json_path} to {csv_path}")
                return csv_path
            else:
                print(f"No data to convert in {json_path}")
                return False
        
        except Exception as e:
            print(f"Error converting JSON to CSV: {e}")
            return False
    
    def plot_metric_from_csv(self, csv_path, metric, output_file=None, show=False):
        """Plot a metric from a CSV file."""
        df = self.load_csv(csv_path)
        if df is None:
            return False
            
        # Check if metric exists
        if metric not in df.columns:
            print(f"Metric '{metric}' not found in {csv_path}")
            return False
        
        # Create figure and axis
        fig, ax = plt.figure(figsize=(10, 6)), plt.gca()
        
        # Extract name for title
        name = df['name'].iloc[0] if 'name' in df.columns and len(df) > 0 else os.path.basename(csv_path)
        
        # Plot the metric
        ax.plot(df['step'], df[metric], linewidth=2, color=self.get_color_for_metric(metric))
        
        # Set axis labels and title
        ax.set_xlabel("Simulation Step")
        ax.set_ylabel(self.get_label_for_metric(metric))
        ax.set_title(f"{self.get_title_for_metric(metric)}: {name}")
        
        # Set y-axis limits based on metric
        if metric in ['avg_trust_government', 'avg_trust_corporate', 'avg_trust_influencer']:
            ax.set_ylim(0, 10)
        elif metric == 'avg_truth_assessment':
            ax.set_ylim(0, 1)
        
        # Add grid
        ax.grid(True, linestyle='--', alpha=0.7)
        
        # Save if output file is specified
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved chart to {output_file}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
        
        return fig
    
    def compare_csvs(self, csv_paths, metric, output_file=None, show=False):
        """Compare a specific metric across multiple CSV files."""
        # Create figure and axis
        fig, ax = plt.figure(figsize=(12, 7)), plt.gca()
        
        # Load and plot each CSV
        for i, csv_path in enumerate(csv_paths):
            df = self.load_csv(csv_path)
            if df is None:
                continue
                
            # Check if metric exists
            if metric not in df.columns:
                print(f"Metric '{metric}' not found in {csv_path}")
                continue
            
            # Get a color from the color cycle
            color = self.colors['run_colors'][i % len(self.colors['run_colors'])]
            
            # Get experiment name for label
            name = df['name'].iloc[0] if 'name' in df.columns and len(df) > 0 else os.path.basename(csv_path)
            label = f"{name} ({len(df)} steps)"
            
            # Plot the metric
            ax.plot(df['step'], df[metric], label=label, color=color, linewidth=2)
        
        # Set axis labels and title
        ax.set_xlabel("Simulation Step")
        ax.set_ylabel(self.get_label_for_metric(metric))
        
        # Format the metric name for the title
        ax.set_title(f"Comparison of {self.get_title_for_metric(metric)} Across Experiments")
        
        # Set y-axis limits based on metric
        if metric in ['avg_trust_government', 'avg_trust_corporate', 'avg_trust_influencer']:
            ax.set_ylim(0, 10)
        elif metric == 'avg_truth_assessment':
            ax.set_ylim(0, 1)
        
        # Add grid and legend
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='best')
        
        # Save if output file is specified
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved comparison chart to {output_file}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
            
        return fig
        
    def compare_accuracy_spread(self, csv_path, output_file=None, show=False):
        """
        Compare the spread of content based on accuracy categories (true/false/fuzzy).
        
        Args:
            csv_path: Path to the CSV file to analyze
            output_file: Optional path to save the visualization
            show: Whether to display the visualization
            
        Returns:
            Matplotlib figure
        """
        df = self.load_csv(csv_path)
        if df is None:
            return False
            
        # Find accuracy spread metrics
        accuracy_metrics = [
            'avg_spread_true_content',
            'avg_spread_fuzzy_content',
            'avg_spread_false_content'
        ]
        
        # Check if metrics exist
        available_metrics = [m for m in accuracy_metrics if m in df.columns]
        if not available_metrics:
            print(f"No content accuracy spread metrics found in {csv_path}")
            return False
            
        # Create a figure with two subplots
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))
        fig.suptitle("Information Spread by Content Accuracy", fontsize=16)
        
        # Plot 1: Line chart showing spread over time
        # Define colors and labels for accuracy categories
        accuracy_colors = {
            'avg_spread_true_content': '#2ca02c',  # Green for true content
            'avg_spread_fuzzy_content': '#ff7f0e',  # Orange for fuzzy content
            'avg_spread_false_content': '#d62728'   # Red for false content
        }
        
        accuracy_labels = {
            'avg_spread_true_content': 'True Content (≥70% accurate)',
            'avg_spread_fuzzy_content': 'Fuzzy Content (30-70% accurate)',
            'avg_spread_false_content': 'False Content (≤30% accurate)'
        }
        
        # Plot each accuracy category
        for metric in available_metrics:
            if metric in df.columns:
                ax1.plot(df['step'], df[metric], 
                         label=accuracy_labels.get(metric, metric),
                         color=accuracy_colors.get(metric, 'gray'),
                         linewidth=2)
                
        # Plot styling
        name = df['name'].iloc[0] if 'name' in df.columns and len(df) > 0 else os.path.basename(csv_path)
        ax1.set_title(f"Content Spread Over Time by Accuracy: {name}")
        ax1.set_xlabel("Simulation Step")
        ax1.set_ylabel("Average Nodes Reached")
        ax1.grid(True, linestyle='--', alpha=0.7)
        ax1.legend(loc='upper left')
        
        # Plot 2: Bar chart showing final spread and content counts
        final_step_data = df.iloc[-1]
        
        # Create bar positions
        bar_width = 0.35
        x = np.arange(len(available_metrics))
        
        # Extract spread values and counts
        spread_values = [final_step_data[m] for m in available_metrics]
        
        # Get content counts if available
        count_metrics = ['count_true_content', 'count_fuzzy_content', 'count_false_content']
        count_values = []
        has_counts = True
        
        for i, metric in enumerate(available_metrics):
            count_metric = metric.replace('avg_spread_', 'count_')
            if count_metric in df.columns:
                count_values.append(final_step_data[count_metric])
            else:
                has_counts = False
                break
                
        # Set up twin axis if we have count data
        if has_counts and count_values:
            ax2_twin = ax2.twinx()
            
            # Create the first bars (average spread)
            bars1 = ax2.bar(x - bar_width/2, spread_values, bar_width, 
                            color=[accuracy_colors[m] for m in available_metrics],
                            label='Avg. Spread')
            
            # Create the second bars (content count)
            bars2 = ax2_twin.bar(x + bar_width/2, count_values, bar_width, 
                                color=[self._lighten_color(accuracy_colors[m]) for m in available_metrics],
                                label='Content Count', alpha=0.7)
            
            # Set labels
            ax2.set_xlabel('Content Type')
            ax2.set_ylabel('Average Spread (nodes)')
            ax2_twin.set_ylabel('Number of Content Items')
            
            # Create legend
            ax2.legend(handles=[bars1[0], bars2[0]], 
                      labels=['Avg. Spread', 'Content Count'],
                      loc='upper left')
        else:
            # Just create spread bars
            ax2.bar(x, spread_values, 
                   color=[accuracy_colors[m] for m in available_metrics])
            ax2.set_xlabel('Content Type')
            ax2.set_ylabel('Average Spread (nodes)')
            
        # Set x-ticks with category names
        display_names = [accuracy_labels[m].split(' ')[0] for m in available_metrics]
        ax2.set_xticks(x)
        ax2.set_xticklabels(display_names)
        
        # Adjust colors to lighten them
        ax2.set_title("Final Spread Comparison by Content Accuracy")
        ax2.grid(axis='y', linestyle='--', alpha=0.7)
        
        # Tight layout to avoid overlapping
        plt.tight_layout()
        fig.subplots_adjust(top=0.9)
        
        # Save if output file is specified
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved accuracy spread comparison to {output_file}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
            
        return fig
    
    def compare_truth_vs_falsehood(self, csv_paths, output_file=None, show=False):
        """
        Analyze how truth spreads compared to falsehood across multiple experiments.
        
        Args:
            csv_paths: List of paths to CSV files to analyze
            output_file: Optional path to save the visualization
            show: Whether to display the visualization
            
        Returns:
            Matplotlib figure
        """
        # Create figure with multiple subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("Truth vs. Falsehood in Information Flow", fontsize=16)
        
        # Flatten axes for easier indexing
        axes = axes.flatten()
        
        # Load data from all files
        all_data = []
        for csv_path in csv_paths:
            df = self.load_csv(csv_path)
            if df is None:
                continue
                
            # Check if required metrics exist
            required_metrics = ['avg_spread_true_content', 'avg_spread_false_content']
            if not all(metric in df.columns for metric in required_metrics):
                print(f"Missing required metrics in {csv_path}")
                continue
                
            # Get experiment name
            name = df['name'].iloc[0] if 'name' in df.columns else os.path.basename(csv_path)
            
            # Extract final values
            final_row = df.iloc[-1]
            
            # Store data for analysis
            experiment_data = {
                'name': name,
                'true_spread': final_row['avg_spread_true_content'],
                'false_spread': final_row['avg_spread_false_content'],
                'steps': len(df),
                'df': df
            }
            
            # Add fuzzy content if available
            if 'avg_spread_fuzzy_content' in df.columns:
                experiment_data['fuzzy_spread'] = final_row['avg_spread_fuzzy_content']
                
            # Calculate ratio of true:false spread
            experiment_data['true_false_ratio'] = (
                experiment_data['true_spread'] / experiment_data['false_spread'] 
                if experiment_data['false_spread'] > 0 else float('inf')
            )
            
            # Calculate maximum spread advantage (true - false) over time
            true_spread = df['avg_spread_true_content'].values
            false_spread = df['avg_spread_false_content'].values
            spread_diff = [t - f for t, f in zip(true_spread, false_spread)]
            experiment_data['max_spread_advantage'] = max(spread_diff)
            experiment_data['min_spread_advantage'] = min(spread_diff)
            
            all_data.append(experiment_data)
            
        if not all_data:
            print("No suitable data found for truth vs. falsehood analysis")
            return False
            
        # Sort data by true:false ratio
        all_data.sort(key=lambda x: x.get('true_false_ratio', 0), reverse=True)
        
        # 1. Bar chart comparing true vs. false spread across experiments
        ax = axes[0]
        experiment_names = [data['name'] for data in all_data]
        true_values = [data['true_spread'] for data in all_data]
        false_values = [data['false_spread'] for data in all_data]
        
        # Create positions for bars
        x = np.arange(len(experiment_names))
        width = 0.35
        
        # Create grouped bars
        ax.bar(x - width/2, true_values, width, color='#2ca02c', label='True Content')
        ax.bar(x + width/2, false_values, width, color='#d62728', label='False Content')
        
        # Add styling
        ax.set_title("Final Spread: Truth vs. Falsehood")
        ax.set_ylabel("Average Nodes Reached")
        ax.set_xticks(x)
        ax.set_xticklabels(experiment_names, rotation=45, ha='right')
        ax.legend()
        ax.grid(axis='y', alpha=0.3)
        
        # 2. Line chart showing truth:falsehood ratio
        ax = axes[1]
        ratios = [data.get('true_false_ratio', 0) for data in all_data]
        
        # Cap extreme values for better visualization
        capped_ratios = [min(ratio, 5) for ratio in ratios]
        
        # Create bars with gradient coloring based on ratio
        # Create a colormap from red to green
        colors = []
        norm = plt.Normalize(0, 5)  # Normalize between 0 and 5 (capped ratio)
        cmap = plt.cm.RdYlGn  # Red-Yellow-Green colormap
        
        for ratio in capped_ratios:
            if ratio == 5:  # This is a capped value, make it darker
                colors.append(cmap(norm(ratio)))
            else:
                colors.append(cmap(norm(ratio)))
                
        bars = ax.bar(x, capped_ratios, color=colors)
        
        # Add annotations for exact values
        for i, ratio in enumerate(ratios):
            if ratio > 5:
                ax.text(i, 5.2, f"{ratio:.1f}", ha='center', va='bottom', rotation=0,
                       color='black', fontweight='bold')
            elif ratio < 0.5:
                ax.text(i, ratio + 0.1, f"{ratio:.1f}", ha='center', va='bottom', 
                       color='white', fontweight='bold')
            else:
                ax.text(i, ratio + 0.1, f"{ratio:.1f}", ha='center', va='bottom', 
                       color='black')
                
        # Mark the parity line (1.0 - equal spread)
        ax.axhline(y=1.0, color='gray', linestyle='--', alpha=0.7)
        ax.text(len(experiment_names) - 0.5, 1.1, "Equal Spread", 
               ha='right', va='bottom', color='gray')
        
        # Add styling
        ax.set_title("Truth:Falsehood Spread Ratio")
        ax.set_ylabel("Ratio (True ÷ False)")
        ax.set_xticks(x)
        ax.set_xticklabels(experiment_names, rotation=45, ha='right')
        ax.grid(axis='y', alpha=0.3)
        
        # 3. Line chart showing spread advantage over time for a selected experiment
        ax = axes[2]
        
        # Choose the experiment with the highest truth advantage
        best_exp_idx = max(range(len(all_data)), 
                          key=lambda i: all_data[i].get('max_spread_advantage', 0))
        best_exp = all_data[best_exp_idx]
        
        # Get time steps
        steps = best_exp['df']['step'].values
        
        # Calculate and plot spread difference (true - false)
        true_spread = best_exp['df']['avg_spread_true_content'].values
        false_spread = best_exp['df']['avg_spread_false_content'].values
        diff = [t - f for t, f in zip(true_spread, false_spread)]
        
        # Plot with color gradient based on positive/negative values
        for i in range(1, len(steps)):
            if diff[i-1] >= 0 and diff[i] >= 0:
                # Both positive - use green
                ax.plot(steps[i-1:i+1], diff[i-1:i+1], color='#2ca02c', linewidth=2)
            elif diff[i-1] <= 0 and diff[i] <= 0:
                # Both negative - use red
                ax.plot(steps[i-1:i+1], diff[i-1:i+1], color='#d62728', linewidth=2)
            else:
                # Crossing zero - use transition color
                if diff[i-1] > 0:  # Positive to negative
                    ax.plot(steps[i-1:i+1], diff[i-1:i+1], color='#ff7f0e', linewidth=2)
                else:  # Negative to positive
                    ax.plot(steps[i-1:i+1], diff[i-1:i+1], color='#ff7f0e', linewidth=2)
                    
        # Add zero line
        ax.axhline(y=0, color='gray', linestyle='--', alpha=0.7)
        
        # Add styling
        ax.set_title(f"Truth Advantage Over Time: {best_exp['name']}")
        ax.set_xlabel("Simulation Step")
        ax.set_ylabel("Truth Advantage (True - False)")
        ax.grid(True, alpha=0.3)
        
        # Add annotations for max and min points
        max_idx = diff.index(max(diff))
        min_idx = diff.index(min(diff))
        
        ax.plot(steps[max_idx], diff[max_idx], 'go', markersize=8)
        ax.plot(steps[min_idx], diff[min_idx], 'ro', markersize=8)
        
        ax.annotate(f"Max: {diff[max_idx]:.1f}", 
                  (steps[max_idx], diff[max_idx]),
                  xytext=(5, 5), textcoords='offset points')
        
        if diff[min_idx] < 0:
            ax.annotate(f"Min: {diff[min_idx]:.1f}", 
                      (steps[min_idx], diff[min_idx]),
                      xytext=(5, -15), textcoords='offset points')
        
        # 4. Scatter plot comparing true vs false spread for all experiments
        ax = axes[3]
        
        # Create scatter plot
        scatter = ax.scatter([data['false_spread'] for data in all_data],
                           [data['true_spread'] for data in all_data],
                           c=[min(data.get('true_false_ratio', 0), 5) for data in all_data],
                           cmap='RdYlGn',
                           s=100,
                           alpha=0.8)
        
        # Add parity line (x=y)
        max_val = max(max(true_values), max(false_values))
        ax.plot([0, max_val], [0, max_val], 'k--', alpha=0.5)
        
        # Add experiment labels
        for i, name in enumerate(experiment_names):
            ax.annotate(name, 
                       (all_data[i]['false_spread'], all_data[i]['true_spread']),
                       xytext=(5, 5), textcoords='offset points',
                       fontsize=8)
        
        # Add styling
        ax.set_title("Truth vs. Falsehood Spread Comparison")
        ax.set_xlabel("False Content Spread")
        ax.set_ylabel("True Content Spread")
        ax.grid(True, alpha=0.3)
        
        # Add colorbar
        cbar = plt.colorbar(scatter, ax=ax)
        cbar.set_label('Truth:Falsehood Ratio')
        
        # Tight layout
        plt.tight_layout()
        fig.subplots_adjust(top=0.94)
        
        # Save if output file is specified
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved truth vs. falsehood analysis to {output_file}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
            
        return fig
    
    def _lighten_color(self, color, amount=0.5):
        """
        Lightens the given color by multiplying (1-luminosity) by the given amount.
        
        Args:
            color: Matplotlib color string, hex string, RGB tuple
            amount: Amount to lighten (0-1)
            
        Returns:
            Lightened color
        """
        import colorsys
        import matplotlib.colors as mc
        
        try:
            c = mc.cnames[color] if color in mc.cnames else color
            c = colorsys.rgb_to_hls(*mc.to_rgb(c))
            return colorsys.hls_to_rgb(c[0], 1 - amount * (1 - c[1]), c[2])
        except:
            return color
    
    def compare_source_spread(self, csv_path, output_file=None, show=False):
        """
        Compare the spread effectiveness of different source types over time.
        
        Args:
            csv_path: Path to the CSV file to analyze
            output_file: Optional path to save the visualization
            show: Whether to display the visualization
            
        Returns:
            Matplotlib figure
        """
        df = self.load_csv(csv_path)
        if df is None:
            return False
            
        # Find source spread metrics
        source_metrics = [col for col in df.columns if col.startswith('avg_spread_')]
        
        if not source_metrics:
            print(f"No source spread metrics found in {csv_path}")
            return False
            
        # Create figure
        fig, ax = plt.figure(figsize=(12, 7)), plt.gca()
        
        # Plot each source type
        for metric in source_metrics:
            source_type = metric.replace('avg_spread_', '')
            # Use custom colors based on source type
            if 'Corporate' in source_type:
                color = self.colors['trust']['corporate']
                label = 'Corporate Media'
            elif 'Government' in source_type:
                color = self.colors['trust']['government']
                label = 'Government Media'
            elif 'Influencer' in source_type:
                color = self.colors['trust']['influencer']
                label = 'Influencers'
            else:
                color = 'gray'
                label = source_type
                
            ax.plot(df['step'], df[metric], label=label, color=color, linewidth=2)
            
        # Plot average overall spread for comparison
        if 'avg_content_spread' in df.columns:
            ax.plot(df['step'], df['avg_content_spread'], label='Overall Average', 
                   color='black', linestyle='--', linewidth=1.5)
        
        # Plot styling
        name = df['name'].iloc[0] if 'name' in df.columns and len(df) > 0 else os.path.basename(csv_path)
        ax.set_title(f"Information Spread by Source Type: {name}")
        ax.set_xlabel("Simulation Step")
        ax.set_ylabel("Average Nodes Reached")
        ax.grid(True, linestyle='--', alpha=0.7)
        ax.legend(loc='upper left')
        
        # Save if output file is specified
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved source spread comparison to {output_file}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
            
        return fig
        
    def plot_information_spread(self, csv_paths, output_file=None, show=False):
        """
        Plot information spread metrics from multiple CSV files.
        
        Args:
            csv_paths: List of paths to CSV files to analyze
            output_file: Optional path to save the visualization
            show: Whether to display the visualization
            
        Returns:
            Matplotlib figure
        """
        # Create figure with multiple subplots
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        fig.suptitle("Information Spread Analysis", fontsize=16)
        
        # Flatten axes for easier indexing
        axes = axes.flatten()
        
        # Spread metrics to extract (if available)
        spread_metrics = [
            'avg_content_spread',
            'max_content_spread',
            'viral_content_count',
            'total_content_created'
        ]
        
        # Source-specific spread metrics
        source_metrics = []
        
        # Collect data from all CSV files
        all_data = {}
        experiment_names = []
        
        for csv_path in csv_paths:
            df = self.load_csv(csv_path)
            if df is None:
                continue
                
            # Get experiment name
            name = df['name'].iloc[0] if 'name' in df.columns else os.path.basename(csv_path)
            experiment_names.append(name)
            
            # For each metric, get the final value
            for metric in spread_metrics:
                if metric in df.columns:
                    if metric not in all_data:
                        all_data[metric] = []
                    final_value = df[metric].iloc[-1]
                    all_data[metric].append(final_value)
                    
            # Check for source-specific metrics
            for col in df.columns:
                if col.startswith('avg_spread_'):
                    if col not in source_metrics:
                        source_metrics.append(col)
                    if col not in all_data:
                        all_data[col] = []
                    final_value = df[col].iloc[-1]
                    all_data[col].append(final_value)
        
        # Now create visualizations
        
        # 1. Bar chart of average content spread
        if 'avg_content_spread' in all_data and len(all_data['avg_content_spread']) > 0:
            ax = axes[0]
            ax.bar(experiment_names, all_data['avg_content_spread'], color=self.colors['run_colors'])
            ax.set_title("Average Content Spread")
            ax.set_ylabel("Avg. Number of Nodes Reached")
            ax.set_xticklabels(experiment_names, rotation=45, ha='right')
            ax.grid(axis='y', alpha=0.3)
        
        # 2. Bar chart of max content spread
        if 'max_content_spread' in all_data and len(all_data['max_content_spread']) > 0:
            ax = axes[1]
            ax.bar(experiment_names, all_data['max_content_spread'], color=self.colors['run_colors'])
            ax.set_title("Maximum Content Reach")
            ax.set_ylabel("Max Number of Nodes Reached")
            ax.set_xticklabels(experiment_names, rotation=45, ha='right')
            ax.grid(axis='y', alpha=0.3)
        
        # 3. Bar chart of viral content count
        if 'viral_content_count' in all_data and len(all_data['viral_content_count']) > 0:
            ax = axes[2]
            ax.bar(experiment_names, all_data['viral_content_count'], color=self.colors['run_colors'])
            ax.set_title("Viral Content Count")
            ax.set_ylabel("Number of Viral Content Pieces")
            ax.set_xticklabels(experiment_names, rotation=45, ha='right')
            ax.grid(axis='y', alpha=0.3)
        
        # 4. Source type comparison
        if source_metrics and any(metric in all_data for metric in source_metrics):
            ax = axes[3]
            
            # Prepare data for grouped bar chart
            source_data = {}
            for metric in source_metrics:
                if metric in all_data and len(all_data[metric]) > 0:
                    source_type = metric.replace('avg_spread_', '')
                    source_data[source_type] = all_data[metric]
            
            if source_data:
                # Create grouped bar chart
                x = np.arange(len(experiment_names))
                width = 0.8 / len(source_data)
                
                for i, (source_type, values) in enumerate(source_data.items()):
                    ax.bar(x + (i - len(source_data)/2 + 0.5) * width, values, 
                           width=width, label=source_type)
                
                ax.set_title("Spread Effectiveness by Source Type")
                ax.set_ylabel("Average Nodes Reached")
                ax.set_xticks(x)
                ax.set_xticklabels(experiment_names, rotation=45, ha='right')
                ax.grid(axis='y', alpha=0.3)
                ax.legend()
            else:
                # No source-specific data
                ax.text(0.5, 0.5, "No source-specific spread data available", 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=12)
        else:
            # No source metrics available
            ax = axes[3]
            ax.text(0.5, 0.5, "No source-specific spread metrics available", 
                   horizontalalignment='center', verticalalignment='center',
                   transform=ax.transAxes, fontsize=12)
        
        # Handle case when no data is available
        if not all_data:
            for ax in axes:
                ax.text(0.5, 0.5, "No information spread data available", 
                       horizontalalignment='center', verticalalignment='center',
                       transform=ax.transAxes, fontsize=12)
        
        plt.tight_layout()
        fig.subplots_adjust(top=0.92)
        
        # Save if output file is specified
        if output_file:
            plt.savefig(output_file, dpi=300, bbox_inches='tight')
            print(f"Saved information spread visualization to {output_file}")
        
        # Show if requested
        if show:
            plt.show()
        else:
            plt.close(fig)
            
        return fig
    
    def get_color_for_metric(self, metric):
        """Get the appropriate color for a metric."""
        if metric == 'avg_trust_government':
            return self.colors['trust']['government']
        elif metric == 'avg_trust_corporate':
            return self.colors['trust']['corporate']
        elif metric == 'avg_trust_influencer':
            return self.colors['trust']['influencer']
        elif metric == 'avg_truth_assessment':
            return self.colors['truth']
        elif metric == 'polarization_index':
            return self.colors['polarization']
        else:
            return self.colors['run_colors'][0]
    
    def get_label_for_metric(self, metric):
        """Get the appropriate y-axis label for a metric."""
        if metric in ['avg_trust_government', 'avg_trust_corporate', 'avg_trust_influencer']:
            return "Average Trust Level (0-10)"
        elif metric == 'avg_truth_assessment':
            return "Average Truth Assessment (0-1)"
        elif metric == 'polarization_index':
            return "Polarization Index (0-1)"
        else:
            return metric
    
    def get_title_for_metric(self, metric):
        """Get a formatted title for a metric."""
        if metric == 'avg_trust_government':
            return "Trust in Government"
        elif metric == 'avg_trust_corporate':
            return "Trust in Corporate Media"
        elif metric == 'avg_trust_influencer':
            return "Trust in Influencers"
        elif metric == 'avg_truth_assessment':
            return "Truth Assessment"
        elif metric == 'polarization_index':
            return "Polarization Index"
        elif metric == 'avg_content_spread':
            return "Average Content Spread"
        elif metric == 'total_content_created':
            return "Total Content Created"
        elif metric == 'max_content_spread':
            return "Max Content Reach"
        elif metric == 'viral_content_count':
            return "Viral Content Count"
        elif metric.startswith('avg_spread_'):
            source_type = metric.replace('avg_spread_', '')
            return f"Average Spread - {source_type}"
        else:
            return metric.replace("avg_", "").replace("_", " ").title()
    
    def batch_convert_json_to_csv(self, directory):
        """Convert all JSON files in a directory to CSV format."""
        json_files = glob.glob(os.path.join(directory, "**", "*.json"), recursive=True)
        
        if not json_files:
            print(f"No JSON files found in {directory}")
            return []
        
        converted_files = []
        for json_file in json_files:
            csv_file = os.path.splitext(json_file)[0] + ".csv"
            if self.json_to_csv(json_file, csv_file):
                converted_files.append(csv_file)
        
        print(f"Converted {len(converted_files)} files")
        return converted_files
    
    def list_csv_files(self):
        """List all CSV files in the experiments directory."""
        csv_files = glob.glob(os.path.join(self.experiment_base_dir, "**", "*.csv"), recursive=True)
        return csv_files
    
    def generate_summary_report(self, csv_paths, output_file=None):
        """Generate a summary report of key metrics from multiple CSV files."""
        if not csv_paths:
            print("No CSV files provided")
            return False
        
        # Default output file
        if output_file is None:
            output_file = os.path.join(self.output_dir, "summary_report.csv")
        
        # Create summary data
        summary_data = []
        
        for csv_path in csv_paths:
            df = self.load_csv(csv_path)
            if df is None:
                continue
                
            # Skip files that don't have the required structure
            if 'step' not in df.columns:
                print(f"Skipping {csv_path}: No 'step' column found")
                continue
            
            # Get final step metrics
            final_step = df['step'].max()
            final_row = df[df['step'] == final_step].iloc[0]
            
            # Create summary row
            summary = {
                'file': os.path.basename(csv_path),
                'name': final_row.get('name', ''),
                'steps': int(final_step),
                'run_id': final_row.get('run_id', '')
            }
            
            # Extract key metrics at final step
            key_metrics = [
                'avg_trust_government', 'avg_trust_corporate', 'avg_trust_influencer',
                'avg_truth_assessment', 'polarization_index'
            ]
            
            for metric in key_metrics:
                if metric in final_row:
                    summary[metric] = final_row[metric]
            
            summary_data.append(summary)
        
        # Create DataFrame and save
        if summary_data:
            summary_df = pd.DataFrame(summary_data)
            summary_df.to_csv(output_file, index=False)
            print(f"Saved summary report to {output_file}")
            return output_file
        else:
            print("No data to summarize")
            return False

def is_float(value):
    """Check if a string can be converted to a float."""
    try:
        float(value)
        return True
    except:
        return False

def main():
    parser = argparse.ArgumentParser(description="Analyze InfoFlow experiment CSV files")
    
    # Main command specification
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # List CSV files command
    list_parser = subparsers.add_parser("list", help="List available CSV files")
    
    # Plot metric command
    plot_parser = subparsers.add_parser("plot", help="Plot a metric from a CSV file")
    plot_parser.add_argument("file", help="Path to CSV file")
    plot_parser.add_argument("--metric", "-m", default="avg_truth_assessment", 
                           help="Metric to plot (default: avg_truth_assessment)")
    plot_parser.add_argument("--output", "-o", help="Output image file path")
    plot_parser.add_argument("--show", action="store_true", help="Show plot")
    
    # Compare CSVs command
    compare_parser = subparsers.add_parser("compare", help="Compare a metric across multiple CSV files")
    compare_parser.add_argument("files", nargs="+", help="Paths to CSV files")
    compare_parser.add_argument("--metric", "-m", default="avg_truth_assessment", 
                              help="Metric to compare (default: avg_truth_assessment)")
    compare_parser.add_argument("--output", "-o", help="Output image file path")
    compare_parser.add_argument("--show", action="store_true", help="Show plot")
    
    # Compare source spread command
    source_spread_parser = subparsers.add_parser("source-spread", help="Compare spread effectiveness across different source types")
    source_spread_parser.add_argument("file", help="Path to CSV file")
    source_spread_parser.add_argument("--output", "-o", help="Output image file path")
    source_spread_parser.add_argument("--show", action="store_true", help="Show plot")
    
    # Compare accuracy spread command
    accuracy_spread_parser = subparsers.add_parser("accuracy-spread", help="Compare spread effectiveness by content accuracy (true/false/fuzzy)")
    accuracy_spread_parser.add_argument("file", help="Path to CSV file")
    accuracy_spread_parser.add_argument("--output", "-o", help="Output image file path")
    accuracy_spread_parser.add_argument("--show", action="store_true", help="Show plot")
    
    # Truth vs falsehood spread command
    truth_spread_parser = subparsers.add_parser("truth-vs-falsehood", help="Analyze how truth spreads compared to falsehood")
    truth_spread_parser.add_argument("files", nargs="+", help="Paths to CSV files")
    truth_spread_parser.add_argument("--output", "-o", help="Output image file path")
    truth_spread_parser.add_argument("--show", action="store_true", help="Show plot")
    
    # Convert CSV to JSON command
    to_json_parser = subparsers.add_parser("to-json", help="Convert a CSV file to JSON format")
    to_json_parser.add_argument("file", help="Path to CSV file")
    to_json_parser.add_argument("--output", "-o", help="Output JSON file path")
    
    # Convert JSON to CSV command
    to_csv_parser = subparsers.add_parser("to-csv", help="Convert a JSON file to CSV format")
    to_csv_parser.add_argument("file", help="Path to JSON file")
    to_csv_parser.add_argument("--output", "-o", help="Output CSV file path")
    
    # Batch convert command
    batch_parser = subparsers.add_parser("batch-convert", help="Convert all JSON files in a directory to CSV")
    batch_parser.add_argument("directory", help="Directory containing JSON files")
    
    # Generate summary report command
    summary_parser = subparsers.add_parser("summary", help="Generate a summary report of key metrics")
    summary_parser.add_argument("files", nargs="+", help="Paths to CSV files")
    summary_parser.add_argument("--output", "-o", help="Output CSV file path")
    
    # Information spread visualization command
    spread_parser = subparsers.add_parser("spread", help="Visualize information spread metrics")
    spread_parser.add_argument("files", nargs="+", help="Paths to CSV files")
    spread_parser.add_argument("--output", "-o", help="Output image file path")
    spread_parser.add_argument("--show", action="store_true", help="Show visualization")
    
    args = parser.parse_args()
    analyzer = CSVAnalyzer()
    
    if args.command == "list":
        csv_files = analyzer.list_csv_files()
        print(f"Found {len(csv_files)} CSV files:")
        for f in csv_files:
            print(f"  {f}")
    
    elif args.command == "plot":
        analyzer.plot_metric_from_csv(args.file, args.metric, args.output, args.show)
    
    elif args.command == "compare":
        analyzer.compare_csvs(args.files, args.metric, args.output, args.show)
    
    elif args.command == "to-json":
        analyzer.csv_to_json(args.file, args.output)
    
    elif args.command == "to-csv":
        analyzer.json_to_csv(args.file, args.output)
    
    elif args.command == "batch-convert":
        analyzer.batch_convert_json_to_csv(args.directory)
    
    elif args.command == "summary":
        analyzer.generate_summary_report(args.files, args.output)
        
    elif args.command == "spread":
        analyzer.plot_information_spread(args.files, args.output, args.show)
        
    elif args.command == "source-spread":
        analyzer.compare_source_spread(args.file, args.output, args.show)
        
    elif args.command == "accuracy-spread":
        analyzer.compare_accuracy_spread(args.file, args.output, args.show)
        
    elif args.command == "truth-vs-falsehood":
        analyzer.compare_truth_vs_falsehood(args.files, args.output, args.show)
    
    else:
        parser.print_help()

if __name__ == "__main__":
    main()