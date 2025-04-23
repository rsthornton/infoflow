#!/usr/bin/env python
"""
Research Question Analysis Tool for InfoFlow Experiments

This script provides automated analysis for the primary research questions
using the CSV analyzer as the underlying engine.

Usage:
  python research_analysis.py [command] [options]

Commands:
  trust-analysis     Analyze the relationship between trust and information ecosystem health
  network-analysis   Analyze how network connectivity influences information spread
  belief-analysis    Analyze how belief resistance affects trust evaluation
  generate-report    Generate comprehensive reports for all research questions
"""

import os
import sys
import glob
import subprocess
import argparse
import datetime

# Base directories
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
EXPERIMENTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, '..'))
DATA_DIR = os.path.join(EXPERIMENTS_DIR, 'data')
TRUST_DIR = os.path.join(DATA_DIR, 'trust-experiments')
NETWORK_DIR = os.path.join(DATA_DIR, 'network-experiments')
COGNITIVE_DIR = os.path.join(DATA_DIR, 'cognitive-experiments')
VISUALIZATIONS_DIR = os.path.join(EXPERIMENTS_DIR, 'visualizations')

# CSV analyzer path
CSV_ANALYZER = os.path.join(SCRIPT_DIR, 'csv_analyzer.py')

def setup_output_dir(research_area):
    """Set up output directory for visualizations."""
    output_dir = os.path.join(VISUALIZATIONS_DIR, research_area)
    os.makedirs(output_dir, exist_ok=True)
    
    # Create a timestamped subdirectory
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_subdir = os.path.join(output_dir, f"analysis_{timestamp}")
    os.makedirs(output_subdir, exist_ok=True)
    
    return output_subdir

def run_csv_analyzer(command, args, output_path=None):
    """Run the CSV analyzer with the given command and arguments."""
    cmd = ['python', CSV_ANALYZER, command] + args
    if output_path:
        cmd += ['--output', output_path]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    # Check for errors
    if result.returncode != 0:
        print(f"Warning: Command failed with error:")
        print(result.stderr)
        print("This is likely due to incompatible file formats and can be safely ignored for some files.")
        print("The analysis will continue with the compatible files.")
    elif result.stderr:
        # Print warnings even if the command succeeded
        print(result.stderr)

def analyze_trust_research_question():
    """
    Analyze the relationship between institutional trust and 
    a healthy social media information ecosystem.
    """
    output_dir = setup_output_dir("trust")
    trust_csvs = glob.glob(os.path.join(TRUST_DIR, "*.csv"))
    
    if not trust_csvs:
        print("Error: No trust experiment CSV files found")
        return False
    
    # Analysis 1: Trust level comparison
    print("\n==== Analyzing Trust Levels Across Experiments ====")
    run_csv_analyzer('compare', trust_csvs + ['--metric', 'avg_trust_government'], 
                    os.path.join(output_dir, 'govt_trust_comparison.png'))
    
    # Analysis 2: Trust impact on truth assessment
    print("\n==== Analyzing Trust Impact on Truth Assessment ====")
    run_csv_analyzer('compare', trust_csvs + ['--metric', 'avg_truth_assessment'], 
                    os.path.join(output_dir, 'truth_assessment_comparison.png'))
    
    # Analysis 3: Truth vs. falsehood spread
    print("\n==== Analyzing Truth vs. Falsehood Spread ====")
    run_csv_analyzer('truth-vs-falsehood', trust_csvs, 
                    os.path.join(output_dir, 'truth_vs_falsehood.png'))
    
    # Analysis 4: Generate trust summary report
    print("\n==== Generating Trust Summary Report ====")
    run_csv_analyzer('summary', trust_csvs, 
                    os.path.join(output_dir, 'trust_summary.csv'))
    
    print(f"\nTrust analysis complete. Visualizations saved to {output_dir}")
    return True

def analyze_network_research_question():
    """
    Analyze how the amount and types of connectivity in social media networks 
    influence how information spreads.
    """
    output_dir = setup_output_dir("network")
    network_csvs = glob.glob(os.path.join(NETWORK_DIR, "*.csv"))
    
    if not network_csvs:
        print("Error: No network experiment CSV files found")
        return False
    
    # Analysis 1: Information spread comparison
    print("\n==== Analyzing Information Spread Across Network Types ====")
    run_csv_analyzer('spread', network_csvs, 
                    os.path.join(output_dir, 'network_spread_comparison.png'))
    
    # Analysis 2: Source spread effectiveness
    print("\n==== Analyzing Source Spread Effectiveness ====")
    for csv_file in network_csvs:
        filename = os.path.basename(csv_file)
        output_name = f"source_spread_{os.path.splitext(filename)[0]}.png"
        run_csv_analyzer('source-spread', [csv_file], 
                        os.path.join(output_dir, output_name))
    
    # Analysis 3: Generate network summary report
    print("\n==== Generating Network Summary Report ====")
    run_csv_analyzer('summary', network_csvs, 
                    os.path.join(output_dir, 'network_summary.csv'))
    
    print(f"\nNetwork analysis complete. Visualizations saved to {output_dir}")
    return True

def analyze_belief_research_question():
    """
    Analyze how resistance to update one's beliefs affects information trust evaluation.
    """
    output_dir = setup_output_dir("belief")
    cognitive_csvs = glob.glob(os.path.join(COGNITIVE_DIR, "*.csv"))
    
    if not cognitive_csvs:
        print("Error: No cognitive experiment CSV files found")
        return False
    
    # Analysis 1: Accuracy spread by cognitive factors
    print("\n==== Analyzing Content Accuracy Spread ====")
    for csv_file in cognitive_csvs:
        filename = os.path.basename(csv_file)
        output_name = f"accuracy_spread_{os.path.splitext(filename)[0]}.png"
        run_csv_analyzer('accuracy-spread', [csv_file], 
                        os.path.join(output_dir, output_name))
    
    # Analysis 2: Generate cognitive summary report
    print("\n==== Generating Belief Resistance Summary Report ====")
    run_csv_analyzer('summary', cognitive_csvs, 
                    os.path.join(output_dir, 'cognitive_summary.csv'))
    
    print(f"\nBelief resistance analysis complete. Visualizations saved to {output_dir}")
    return True

def generate_comprehensive_report():
    """Generate comprehensive reports for all research questions."""
    trust_output = setup_output_dir("trust")
    network_output = setup_output_dir("network")
    belief_output = setup_output_dir("belief")
    
    print("\n==== Generating Comprehensive Research Reports ====")
    
    # Trust analysis
    trust_csvs = glob.glob(os.path.join(TRUST_DIR, "*.csv"))
    if trust_csvs:
        run_csv_analyzer('summary', trust_csvs, 
                        os.path.join(trust_output, 'trust_summary.csv'))
        run_csv_analyzer('truth-vs-falsehood', trust_csvs, 
                        os.path.join(trust_output, 'trust_truth_falsehood_analysis.png'))
        print(f"Trust report saved to {trust_output}")
    
    # Network analysis
    network_csvs = glob.glob(os.path.join(NETWORK_DIR, "*.csv"))
    if network_csvs:
        run_csv_analyzer('summary', network_csvs, 
                        os.path.join(network_output, 'network_summary.csv'))
        run_csv_analyzer('spread', network_csvs, 
                        os.path.join(network_output, 'network_spread_analysis.png'))
        print(f"Network report saved to {network_output}")
    
    # Cognitive analysis
    cognitive_csvs = glob.glob(os.path.join(COGNITIVE_DIR, "*.csv"))
    if cognitive_csvs:
        run_csv_analyzer('summary', cognitive_csvs, 
                        os.path.join(belief_output, 'cognitive_summary.csv'))
        print(f"Belief resistance report saved to {belief_output}")
    
    # Create a cross-analysis report if we have data for at least two areas
    if (len(trust_csvs) > 0 and len(network_csvs) > 0) or \
       (len(trust_csvs) > 0 and len(cognitive_csvs) > 0) or \
       (len(network_csvs) > 0 and len(cognitive_csvs) > 0):
        cross_output = setup_output_dir("cross_analysis")
        all_csvs = trust_csvs + network_csvs + cognitive_csvs
        run_csv_analyzer('summary', all_csvs, 
                        os.path.join(cross_output, 'cross_area_summary.csv'))
        print(f"Cross-area analysis saved to {cross_output}")
    
    print("\nComprehensive reports generated.")
    return True

def main():
    parser = argparse.ArgumentParser(
        description="Research Question Analysis Tool for InfoFlow Experiments"
    )
    
    # Create subparsers for different commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Trust analysis command
    trust_parser = subparsers.add_parser(
        "trust-analysis", help="Analyze the relationship between trust and information ecosystem health"
    )
    
    # Network analysis command
    network_parser = subparsers.add_parser(
        "network-analysis", help="Analyze how network connectivity influences information spread"
    )
    
    # Belief analysis command
    belief_parser = subparsers.add_parser(
        "belief-analysis", help="Analyze how belief resistance affects trust evaluation"
    )
    
    # Generate report command
    report_parser = subparsers.add_parser(
        "generate-report", help="Generate comprehensive reports for all research questions"
    )
    
    args = parser.parse_args()
    
    if args.command == "trust-analysis":
        analyze_trust_research_question()
    elif args.command == "network-analysis":
        analyze_network_research_question()
    elif args.command == "belief-analysis":
        analyze_belief_research_question()
    elif args.command == "generate-report":
        generate_comprehensive_report()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()