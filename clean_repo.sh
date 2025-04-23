#\!/bin/bash
# Script to clean the repository before committing to GitHub

# Remove Python bytecode files
find . -name "__pycache__" -type d -exec rm -rf {} +
find . -name "*.pyc" -delete
find . -name "*.pyo" -delete
find . -name "*.pyd" -delete

# Remove Mac OS specific files
find . -name ".DS_Store" -delete
find . -name "._*" -delete

# Remove temporary test files
rm -f random-test_run_*.json

echo "Repository cleaned for GitHub"
