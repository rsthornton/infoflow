#!/usr/bin/env python3
"""
Environment verification script for InfoFlow 2.0
This script helps verify that your environment is correctly set up.
"""

import sys
import importlib
import platform
import subprocess
import os

def check_python_version():
    """Check if Python version meets requirements."""
    print(f"Python version: {platform.python_version()}")
    if sys.version_info < (3, 11):
        print("⚠️  WARNING: InfoFlow 2.0 requires Python 3.11 or higher")
        print("   Your current Python version is too old")
        return False
    else:
        print("✓ Python version is compatible")
        return True

def check_package(package_name, min_version=None):
    """Check if package is installed and meets minimum version requirements."""
    try:
        module = importlib.import_module(package_name)
        if hasattr(module, '__version__'):
            version = module.__version__
        elif hasattr(module, 'VERSION'):
            version = module.VERSION
        else:
            version = "unknown"
        
        if min_version and version != "unknown":
            from packaging import version as version_parser
            if version_parser.parse(version) < version_parser.parse(min_version):
                print(f"⚠️  {package_name} version {version} is installed but {min_version}+ is required")
                return False
            else:
                print(f"✓ {package_name} {version} is installed (minimum: {min_version})")
                return True
        else:
            print(f"✓ {package_name} {version} is installed")
            return True
    except ImportError:
        print(f"⚠️  {package_name} is not installed")
        return False

def check_mesa_features():
    """Check if Mesa has the required features."""
    try:
        import mesa
        print(f"Mesa version: {mesa.__version__}")
        
        # Check for AgentSet from mesa.agent
        try:
            from mesa.agent import AgentSet
            print("✓ AgentSet is available")
        except ImportError:
            print("⚠️  AgentSet is not available in mesa.agent")
            return False
        
        # Check for create_agents on Agent class
        if hasattr(mesa.Agent, 'create_agents'):
            print("✓ create_agents method is available")
        else:
            print("⚠️  create_agents method is not available on mesa.Agent")
            return False
        
        return True
    except ImportError:
        print("⚠️  Mesa is not installed")
        return False

def main():
    """Run all verification checks."""
    print("InfoFlow 2.0 Environment Verification")
    print("=" * 40)
    
    # Check Python version
    python_ok = check_python_version()
    
    print("\nChecking required packages:")
    # Check core packages
    mesa_ok = check_package("mesa", "3.0.0")
    numpy_ok = check_package("numpy", "1.24.0")
    networkx_ok = check_package("networkx", "3.1")
    matplotlib_ok = check_package("matplotlib", "3.7.0")
    flask_ok = check_package("flask", "2.3.0")
    
    # If Mesa is installed, check its features
    mesa_features_ok = check_mesa_features() if mesa_ok else False
    
    # Overall status
    print("\nEnvironment Status:")
    if all([python_ok, mesa_ok, numpy_ok, networkx_ok, matplotlib_ok, flask_ok, mesa_features_ok]):
        print("✅ Success! Your environment is correctly set up for InfoFlow 2.0")
        return 0
    else:
        print("❌ Some requirements are missing or outdated")
        print("\nTo fix these issues:")
        print("1. Make sure you have Python 3.11+ installed")
        print("2. Install dependencies with: pip install -r config/requirements.txt")
        print("3. Or create a conda environment with: conda env create -f config/environment.yml")
        return 1

if __name__ == "__main__":
    sys.exit(main())