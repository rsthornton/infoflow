# InfoFlow: Social Media Information Flow Simulation

> **2025 Update**: A streamlined CSV-based analysis framework has been implemented! See the [CSV Analysis Framework](#csv-analysis-framework) section.

An agent-based model simulating how information flows through social media networks. The model focuses on how truth assessments form and propagate as users interact with content from different social media sources. It captures how corporate social media accounts, social media influencers, government social media accounts, and regular users interact within various social network structures to influence perceptions of truth and trust dynamics.

## Features

- Spectrum of truth values for claims (0-1 scale) rather than binary true/false
- Diverse social media account types (corporate, influencer, government) with distinct behavior patterns
- Realistic user cognitive models including confirmation bias, critical thinking, and social conformity
- Customizable social network structures (small-world, scale-free, random) modeling different platform dynamics
- Trust dynamics between users and different types of social media accounts
- Truth assessment evolution as users consume and share content
- Individual agent tracking with detailed history visualization
- Interactive network visualization with multiple layouts and visualization modes
- Comprehensive export system (CSV, JSON data, chart images, interactive HTML)
- Interactive visualization using Mesa 3 and Flask
- Comprehensive parameter controls with intuitive UI organization
- Statistics collection system for data-driven analysis
- Simulation comparison tools for parameter impact assessment

## Project Organization

The project follows a clean, modular structure:

```
infoflow/                  # Main package
├── __init__.py            # Package exports
├── agents/                # Agent implementations
│   ├── base.py            # Base agent classes (BaseAgent, CitizenAgent, SocialMediaAgent)
│   └── media/             # Specialized media agent implementations
│       ├── base.py        # Media agent base class
│       ├── corporate.py   # Corporate media agent implementation
│       ├── government.py  # Government media agent implementation
│       └── influencer.py  # Social media influencer agent implementation
├── core/                  # Core model components 
│   ├── model.py           # Main simulation model (InformationFlowModel)
│   └── network.py         # Network creation and utility functions
├── data/                  # Data collection and analysis
│   ├── collectors.py      # Data collection utilities
│   ├── metrics.py         # Simulation metrics definitions
│   └── visualization.py   # Plotting and visualization tools
├── utils/                 # Utility functions
│   ├── helpers.py         # General helper functions
│   └── simple_stats.py    # Statistics collection system
└── web/                   # Flask web components
    ├── routes.py          # API endpoints
    └── templates/         # Web interface templates

experiments/               # Experiment framework
├── analysis/              # Analysis tools
│   ├── csv_analyzer.py    # CSV analysis tool
│   ├── list_data.py       # Data inventory tool
│   ├── organize_csv.py    # CSV file organizer
│   └── research_analysis.py # Research question analysis
├── data/                  # Organized experiment data
│   ├── trust-experiments/ # Trust-related experiments
│   ├── network-experiments/ # Network structure experiments
│   └── cognitive-experiments/ # Cognitive experiments
├── exports/               # Temporary location for exported CSV files
├── visualizations/        # Generated visualizations
├── GUIDE.md               # User guide for the experiment framework
└── research-questions.md  # Core research questions

config/                    # Configuration files
docs/                      # Documentation
tests/                     # Test suite
```

## Key Concepts

- **Truth Assessment**: Users' evaluation of how true a claim is (0-1 scale)
- **Political Bias**: How social media content is framed (-5 to +5 anti-Trump to pro-Trump scale)
- **Social Media Account Types**: Different sources (corporate accounts, influencers, government accounts) with varying authority and credibility
- **Social Network Structure**: How connections between users affect information flow on platforms
- **Trust Levels**: How users adjust trust in different social media account types based on perceived accuracy
- **Publication Rate**: How frequently social media accounts post content (0-1 scale)
- **Influence Reach**: Proportion of users a social media account can reach (0-1 scale)
- **Critical Thinking**: User ability to evaluate source credibility (0-10 scale)
- **Trust Dynamics**: How trust in social media information sources evolves over time
- **Content Sharing**: How users decide which content to share with their network connections

## Installation

This project requires Python 3.11 or higher due to Mesa 3 requirements.

### IMPORTANT: Setup Instructions (Follow In Order)

1. **Verify Python Version**: Ensure you have Python 3.11+ installed
   ```bash
   python --version
   ```

2. **Create a Virtual Environment**:
   ```bash
   # Using venv (recommended)
   python -m venv env
   
   # Activate the environment
   # On Windows:
   env\Scripts\activate
   # On macOS/Linux:
   source env/bin/activate
   ```

3. **Install Dependencies**:
   ```bash
   # Using pip (easiest option)
   pip install -r config/requirements.txt
   ```

4. **Verify Your Setup**:
   ```bash
   python verify_setup.py
   ```
   This script will check that all required packages are installed correctly.

5. **If Verification Fails**:
   - Check Python version (must be 3.11+)
   - Ensure pip is up to date (`pip install --upgrade pip`)
   - Try installing with development mode: `pip install -e .`

### Alternative: Using conda

If you prefer conda for environment management:

```bash
# Create the conda environment
conda env create -f config/environment.yml

# Activate the environment
conda activate infoflow

# Verify setup
python verify_setup.py
```

## Running the Web Application

To run the web interface:

```bash
python run_server.py
```

Then visit [http://127.0.0.1:5001](http://127.0.0.1:5001) in your browser.

The web interface provides several pages:
- **Home**: Project overview
- **Run Simulation**: Configure and run simulations with various parameters
- **Simulation History**: View, compare, and analyze past simulation runs

## CSV Analysis Framework

The new CSV-based analysis framework simplifies research workflow and focuses on answering core research questions:

### Research Questions

1. **What is the relationship between institutional trust and a healthy social media information ecosystem?**
2. **How does the amount, and the types of connectivity in social media networks influence how information spreads?**
3. **How does resistance to update one's beliefs affect information trust evaluation?**

### Streamlined Workflow

1. **Run experiments** in the web interface
2. **Export CSV files** to the `experiments/exports` directory
3. **Organize files** using the CSV organizer
4. **Analyze data** using the CSV analyzer

```bash
# Organize exported CSV files
python experiments/analysis/organize_csv.py --all

# List available data
python experiments/analysis/list_data.py

# Plot a specific metric
python experiments/analysis/csv_analyzer.py plot experiments/data/trust-experiments/high-trust-1.csv --metric avg_trust_government --show

# Compare metrics across experiments
python experiments/analysis/csv_analyzer.py compare experiments/data/trust-experiments/*.csv --metric avg_truth_assessment --show

# Analyze information spread
python experiments/analysis/csv_analyzer.py source-spread experiments/data/trust-experiments/high-trust-1.csv --show

# Compare truth vs. falsehood spread
python experiments/analysis/csv_analyzer.py truth-vs-falsehood experiments/data/trust-experiments/*.csv --show

# Run research-focused analysis
python experiments/analysis/research_analysis.py trust-analysis
```

For detailed instructions, see the `experiments/GUIDE.md` file.

## Managing Simulation Runs

The project includes a utility script to manage simulation runs:

```bash
# List recent simulation runs
python delete_runs.py --list

# Delete a specific simulation run by ID
python delete_runs.py --delete RUN_ID

# Delete all simulation runs (with confirmation prompt)
python delete_runs.py --delete-all
```

## Running Tests

To run the full test suite:

```bash
python run_tests.py
```

## Documentation

The project includes comprehensive documentation in the `docs/` directory:

- [**Project Overview**](docs/PROJECT_OVERVIEW.md): Introduction to project concepts and architecture
- [**Code Structure**](docs/CODE_STRUCTURE.md): Details of code organization

## Project Status (April 2025)

The InfoFlow project has completed major development milestones and is ready for use in educational and research contexts. Recent developments include:

- **Streamlined CSV Analysis Framework**: Simple, focused analysis tools aligned with research questions
- **Enhanced Information Spread Metrics**: Tracking of source-specific and accuracy-specific spread
- **Truth vs. Falsehood Analysis**: Tools to compare how true and false content spreads through networks
- **Research-Focused Analysis Tools**: Automated analysis aligned with core research questions
- **Automated Data Organization**: Tools for organizing exported CSV files by experiment type
- **Data Inventory System**: Command-line tools for listing available experiment data
- **Enhanced Visualization Capabilities**: Improved charts for trust dynamics and information spread

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Author

Shingai Thornton  
Email: rthornton@binghamton.edu
