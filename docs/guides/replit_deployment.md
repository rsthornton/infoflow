# Comprehensive Guide: Deploying InfoFlow on Replit

This guide provides detailed instructions for deploying the InfoFlow project on Replit, including configuration, database setup, troubleshooting, and custom domain setup.

## Table of Contents

1. [Introduction to Replit](#introduction-to-replit)
2. [Setting Up Your Replit Account](#setting-up-your-replit-account)
3. [Creating Your InfoFlow Repl](#creating-your-infoflow-repl)
4. [Project Configuration](#project-configuration)
5. [Database Configuration](#database-configuration)
6. [Static Files and Assets](#static-files-and-assets)
7. [Environment Variables](#environment-variables)
8. [Running and Testing](#running-and-testing)
9. [Custom Domain Setup](#custom-domain-setup)
10. [Performance Optimization](#performance-optimization)
11. [Troubleshooting Common Issues](#troubleshooting-common-issues)
12. [Advanced Configuration](#advanced-configuration)

## Introduction to Replit

Replit (formerly Repl.it) is a browser-based integrated development environment (IDE) that lets you code, build, and deploy applications directly from your browser. It's particularly well-suited for educational projects, prototypes, and small web applications.

**Benefits for InfoFlow:**
- Zero local setup required
- Instant deployment
- Built-in version control
- Shareable URLs for demos
- Collaborative coding features

## Setting Up Your Replit Account

1. **Create an account**
   - Go to [replit.com](https://replit.com) and sign up for a free account
   - Verify your email address

2. **Explore the dashboard**
   - Familiarize yourself with the Replit interface
   - Browse templates and explore example projects

## Creating Your InfoFlow Repl

### Method 1: Starting from GitHub

1. **Click "Create Repl"**
   - From your dashboard, click the "+ Create Repl" button

2. **Import from GitHub**
   - Select the "Import from GitHub" tab
   - Paste your InfoFlow repository URL
   - If the repository is private, you'll need to connect your GitHub account

3. **Configure the repl**
   - Set the language to "Python"
   - Name your repl (e.g., "InfoFlow-Simulation")
   - Click "Import from GitHub"

### Method 2: Starting from Scratch

1. **Click "Create Repl"**
   - From your dashboard, click the "+ Create Repl" button

2. **Select template**
   - Choose "Python" or "Flask" as the template
   - Name your repl (e.g., "InfoFlow-Simulation")
   - Click "Create Repl"

3. **Upload your files**
   - Use the "Upload file" button to upload your project files
   - Alternatively, you can create files from scratch or use the terminal to clone your repo

## Project Configuration

### Required Configuration Files

1. **Create a `main.py` file** in the root directory:
   ```python
   #!/usr/bin/env python3
   """
   Main entry point for Replit deployment of InfoFlow.
   """
   import os
   from infoflow.web import create_app

   # Create Flask application
   app = create_app()

   # Configure for Replit environment
   if __name__ == "__main__":
       # Replit expects the server to listen on 0.0.0.0:8080
       port = int(os.environ.get('PORT', 8080))
       app.run(host='0.0.0.0', port=port, debug=False)
   ```

2. **Create a `.replit` file**:
   ```
   entrypoint = "main.py"
   modules = ["python-3.8:v18-20230807-322e88b"]

   [nix]
   channel = "stable-23_05"

   [env]
   PYTHONPATH = "${REPL_HOME}"
   FLASK_ENV = "production"
   FLASK_APP = "main.py"

   [packager]
   language = "python3"

   [packager.features]
   enabledForHosting = true
   packageSearch = true
   guessImports = true

   [languages]
   [languages.python3]
   pattern = "**/*.py"
   syntax = "python"

   [deployment]
   run = ["python3", "main.py"]
   deploymentTarget = "cloudrun"
   ```

3. **Create a `pyproject.toml` file**:
   ```toml
   [tool.poetry]
   name = "infoflow"
   version = "0.1.0"
   description = "Information flow simulation in social networks"
   authors = ["Your Name <your.email@example.com>"]

   [tool.poetry.dependencies]
   python = ">=3.8,<3.9"
   mesa = "^3.0.0"
   networkx = "^3.1"
   numpy = "^1.24.0"
   matplotlib = "^3.7.0"
   seaborn = "^0.12.0"
   scipy = "^1.10.0"
   flask = "^2.3.0"
   pandas = "^2.0.0"
   solara = "^1.0.0"
   gunicorn = "^20.1.0"

   [build-system]
   requires = ["poetry-core>=1.0.0"]
   build-backend = "poetry.core.masonry.api"
   ```

4. **Create a `requirements.txt` file** in the root (backup for Poetry):
   ```
   mesa>=3.0.0
   networkx>=3.1
   numpy>=1.24.0
   matplotlib>=3.7.0
   seaborn>=0.12.0
   scipy>=1.10.0
   flask>=2.3.0
   pandas>=2.0.0
   solara>=1.0.0
   gunicorn>=20.1.0
   ```

5. **Create a `replit.nix` file** for system dependencies:
   ```nix
   { pkgs }: {
     deps = [
       pkgs.python38
       pkgs.python38Packages.pip
       pkgs.python38Packages.venv
       pkgs.python38Packages.wheel
       pkgs.python38Packages.setuptools
       pkgs.gcc
     ];
   }
   ```

### Setup Install Script

Create a `setup.sh` file in the root directory:

```bash
#!/bin/bash

# Make sure we're in the project root
cd "$(dirname "$0")"

# Create necessary directories
mkdir -p data data/exports data/plots logs

# Install dependencies
pip install -r requirements.txt
pip install -e .

# Initialize the database
python -c "from infoflow.utils.simple_stats import StatsCollector; StatsCollector()"

echo "Setup complete! Run 'python main.py' to start the server."
```

Make it executable:
```bash
chmod +x setup.sh
```

## Database Configuration

### Modify Database Path for Persistent Storage

Create a file called `replit_config.py` in the `infoflow/utils` directory:

```python
"""
Replit-specific configuration utilities.
"""

import os
from pathlib import Path

def get_replit_data_dir():
    """Get the persistent data directory for Replit."""
    # Check if we're running on Replit
    if os.environ.get('REPL_ID') and os.environ.get('REPL_SLUG'):
        # Use the persistent storage location
        data_dir = Path(os.environ.get('REPL_HOME', '/home/runner')) / 'data'
    else:
        # Local development fallback
        data_dir = Path(os.getcwd()) / 'data'
    
    # Ensure the directory exists
    os.makedirs(data_dir, exist_ok=True)
    return data_dir
```

Now modify `infoflow/utils/simple_stats.py` to use this function:

```python
# Add near the top of the file
from infoflow.utils.replit_config import get_replit_data_dir

# Then modify the __init__ method
def __init__(self, db_path=None):
    """
    Initialize the stats collector.
    """
    if db_path is None:
        # Get the appropriate data directory
        data_dir = get_replit_data_dir()
        db_path = data_dir / "simulation_stats.db"

    self.db_path = str(db_path)
    self.run_id = str(uuid.uuid4())[:8]
    self.init_db()
```

Also update the static methods in `simple_stats.py` to use the same function:

```python
@staticmethod
def get_recent_runs(limit=10):
    # ...
    # Use Replit-aware data directory
    data_dir = get_replit_data_dir()
    db_path = data_dir / "simulation_stats.db"
    # ...

@staticmethod
def get_run_metadata(run_id):
    # ...
    data_dir = get_replit_data_dir()
    db_path = data_dir / "simulation_stats.db"
    # ...

@staticmethod
def get_run_data(run_id):
    # ...
    data_dir = get_replit_data_dir()
    db_path = data_dir / "simulation_stats.db"
    # ...
```

## Static Files and Assets

### Ensure Chart Generation Works

1. **Update the charts directory in `infoflow/web/routes.py`**:

```python
# For the metrics_dashboard function and generate_metrics_charts function:

# Define the directory to save charts
try:
    # Get the absolute path to the web module directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define static/charts directory path from the web module
    static_dir = os.path.join(current_dir, "static", "charts")
    
    # Ensure the directory exists
    os.makedirs(static_dir, exist_ok=True)
    print(f"Using charts directory: {static_dir}")
except Exception as e:
    print(f"Error creating charts directory: {e}")
    # Fallback to a directory in Replit's persistent storage
    from infoflow.utils.replit_config import get_replit_data_dir
    static_dir = os.path.join(str(get_replit_data_dir()), "charts")
    try:
        os.makedirs(static_dir, exist_ok=True)
        print(f"Using fallback charts directory: {static_dir}")
    except Exception as e2:
        print(f"Error creating fallback charts directory: {e2}")
        # Last resort - use a temp directory
        import tempfile
        static_dir = tempfile.mkdtemp(prefix="infoflow_charts_")
        print(f"Using temporary charts directory: {static_dir}")
```

## Environment Variables

### Setting Up Environment Variables

1. **Create a `.env` file** (optional, for local development):
   ```
   FLASK_ENV=development
   FLASK_DEBUG=1
   ```

2. **Configure environment variables in Replit**:
   - Click on the "Secrets" tool in the left sidebar (lock icon)
   - Add the following environment variables:
     - Key: `FLASK_ENV`, Value: `production`
     - Key: `FLASK_DEBUG`, Value: `0`

## Running and Testing

### Initial Setup

1. **Run the setup script**:
   ```bash
   ./setup.sh
   ```

2. **Test the installation**:
   ```bash
   python -c "import infoflow; print(f'InfoFlow version: {infoflow.__version__ if hasattr(infoflow, \"__version__\") else \"Unknown\"}')"
   ```

3. **Start the server**:
   ```bash
   python main.py
   ```

4. **Access your application**
   - Click on the "Webview" tab or use the provided URL (e.g., https://infoflow.yourusername.repl.co)

## Custom Domain Setup

### Setting Up a Custom Domain (Replit Core or Hacker Plan Required)

1. **Purchase a domain** from a provider like Namecheap, GoDaddy, or Google Domains

2. **Configure in Replit**:
   - Go to your repl's "Settings" tab
   - Scroll down to "Custom domains" 
   - Click "Add custom domain"
   - Enter your domain (e.g., infoflow.example.com)
   - Follow the instructions to verify ownership

3. **Configure DNS Settings**:
   - At your domain registrar, add the following records:
     - Type: `A`, Name: `@`, Value: `replit's IP address` (provided in Replit's instructions)
     - Type: `CNAME`, Name: `www`, Value: `yourusername.repl.co`

4. **Wait for DNS propagation** (can take up to 48 hours, but usually much faster)

5. **Enable HTTPS**:
   - Replit will automatically provision an SSL certificate through Let's Encrypt

## Performance Optimization

### Optimizing for Replit's Environment

1. **Minimize matplotlib overhead**:
   ```python
   # Add to main.py
   import matplotlib
   matplotlib.use('Agg')  # Use non-interactive backend
   ```

2. **Implement caching for expensive operations**:
   ```python
   # Example caching for network data
   from functools import lru_cache
   
   @lru_cache(maxsize=32)
   def get_cached_network_data(model_id):
       # Your network data generation code
       return data
   ```

3. **Optimize database queries**:
   - Add indexes for frequent queries
   - Limit result sets
   - Use connection pooling

4. **Implement lazy loading of assets**:
   - Use JavaScript to load charts and visualizations only when needed

## Troubleshooting Common Issues

### Issue: Package Installation Failures

**Problem**: Dependencies fail to install correctly.
**Solution**: 
1. Try installing problematic packages individually:
   ```bash
   pip install numpy
   pip install scipy
   pip install matplotlib
   ```
2. Check if you need to install system dependencies via Nix

### Issue: Database Permission Errors

**Problem**: SQLite database cannot be written.
**Solution**:
1. Ensure you're using the Replit persistent storage location
2. Check file permissions:
   ```bash
   ls -la $(python -c "from infoflow.utils.replit_config import get_replit_data_dir; print(get_replit_data_dir())")
   ```
3. Try recreating the database:
   ```bash
   rm $(python -c "from infoflow.utils.replit_config import get_replit_data_dir; print(get_replit_data_dir() / 'simulation_stats.db')")
   python -c "from infoflow.utils.simple_stats import StatsCollector; StatsCollector()"
   ```

### Issue: Charts Not Displaying

**Problem**: Charts are not generated or not displaying in the web interface.
**Solution**:
1. Check the chart directory permissions and existence:
   ```bash
   ls -la $(python -c "import os; from infoflow.web import routes; print(os.path.join(os.path.dirname(os.path.abspath(routes.__file__)), 'static', 'charts'))")
   ```
2. Ensure matplotlib is using the non-interactive backend:
   ```python
   import matplotlib
   matplotlib.use('Agg')
   ```
3. Add debugging output to track chart generation:
   ```python
   print(f"Saving chart to: {chart_path}")
   ```

### Issue: Application Crashes or Times Out

**Problem**: The application crashes or times out during complex operations.
**Solution**:
1. Implement background tasks for long-running operations
2. Add timeouts to prevent hanging:
   ```python
   from functools import timeout
   
   @timeout(seconds=10)
   def long_running_operation():
       # Your code here
       pass
   ```
3. Monitor memory usage and optimize resource-intensive operations

## Advanced Configuration

### Implementing a Worker Process for Long-Running Simulations

1. **Create a worker.py file**:
   ```python
   """
   Background worker for long-running simulations.
   """
   import time
   import os
   import json
   from pathlib import Path
   import threading
   
   from infoflow.core.model import create_model
   from infoflow.utils.simple_stats import StatsCollector
   
   class SimulationWorker:
       def __init__(self):
           self.active_jobs = {}
           self.results = {}
           self.lock = threading.Lock()
       
       def start_simulation(self, params):
           """Start a simulation in a background thread."""
           job_id = f"job_{int(time.time())}"
           
           # Create a thread for this job
           thread = threading.Thread(
               target=self._run_simulation,
               args=(job_id, params),
               daemon=True
           )
           
           with self.lock:
               self.active_jobs[job_id] = {
                   "thread": thread,
                   "status": "starting",
                   "params": params,
                   "start_time": time.time()
               }
           
           # Start the thread
           thread.start()
           return job_id
       
       def _run_simulation(self, job_id, params):
           """Run the simulation (called in background thread)."""
           try:
               with self.lock:
                   self.active_jobs[job_id]["status"] = "running"
               
               # Create stats collector
               collector = StatsCollector()
               collector.run_id = job_id
               collector.start_run(params)
               
               # Create and run model
               model = create_model(**params)
               
               # Run for specified steps
               steps = params.get("steps", 10)
               for step in range(steps):
                   model.step()
                   
                   # Collect metrics
                   metrics = {
                       "avg_trust_government": model.datacollector.model_vars["Trust in Government"][-1],
                       "avg_trust_corporate": model.datacollector.model_vars["Trust in Corporate Media"][-1],
                       "avg_trust_influencer": model.datacollector.model_vars["Trust in Influencers"][-1],
                       "avg_truth_assessment": model.datacollector.model_vars["Average Truth Assessment"][-1],
                   }
                   
                   collector.record_step(step, metrics)
                   
                   # Update status
                   with self.lock:
                       self.active_jobs[job_id]["progress"] = (step + 1) / steps
               
               # Get data from model
               data = model.datacollector.get_model_vars_dataframe().to_dict("records")
               
               # Store result
               with self.lock:
                   self.results[job_id] = {
                       "status": "completed",
                       "data": data,
                       "run_id": collector.run_id,
                       "completion_time": time.time()
                   }
                   self.active_jobs[job_id]["status"] = "completed"
           
           except Exception as e:
               print(f"Error in simulation job {job_id}: {e}")
               with self.lock:
                   self.active_jobs[job_id]["status"] = "failed"
                   self.active_jobs[job_id]["error"] = str(e)
                   self.results[job_id] = {
                       "status": "failed",
                       "error": str(e),
                       "completion_time": time.time()
                   }
       
       def get_job_status(self, job_id):
           """Get the status of a job."""
           with self.lock:
               if job_id in self.active_jobs:
                   return self.active_jobs[job_id]
               if job_id in self.results:
                   return self.results[job_id]
               return {"status": "not_found"}
       
       def get_all_jobs(self):
           """Get a list of all jobs."""
           with self.lock:
               jobs = []
               for job_id, job_info in self.active_jobs.items():
                   jobs.append({
                       "job_id": job_id,
                       "status": job_info["status"],
                       "start_time": job_info["start_time"],
                       "progress": job_info.get("progress", 0)
                   })
               return jobs
   
   # Create a singleton worker instance
   worker = SimulationWorker()
   ```

2. **Add API endpoints in routes.py**:
   ```python
   from worker import worker
   
   @bp.route("/api/start-background-simulation", methods=["POST"])
   def start_background_simulation():
       """Start a simulation in the background."""
       params = request.json
       job_id = worker.start_simulation(params)
       return jsonify({"status": "success", "job_id": job_id})
   
   @bp.route("/api/job-status/<job_id>", methods=["GET"])
   def get_job_status(job_id):
       """Get the status of a background job."""
       status = worker.get_job_status(job_id)
       return jsonify({"status": "success", "job": status})
   ```

### Implementing Session Management

1. **Add Flask-Session to your dependencies**:
   ```
   pip install Flask-Session
   ```

2. **Configure session in __init__.py**:
   ```python
   from flask import Flask
   from flask_session import Session
   
   def create_app():
       """Create and configure the Flask application."""
       app = Flask(__name__)
       
       # Configure sessions
       app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-key-for-development-only")
       app.config["SESSION_TYPE"] = "filesystem"
       app.config["SESSION_FILE_DIR"] = os.path.join(os.environ.get('REPL_HOME', os.getcwd()), "flask_session")
       app.config["SESSION_PERMANENT"] = False
       app.config["PERMANENT_SESSION_LIFETIME"] = 86400  # 24 hours
       
       Session(app)
       
       # Load configuration
       app.config.from_object("config")
       
       # Register routes
       from infoflow.web import routes
       app.register_blueprint(routes.bp)
       
       return app
   ```

3. **Use sessions in your routes**:
   ```python
   from flask import session
   
   @bp.route("/api/save-preferences", methods=["POST"])
   def save_preferences():
       preferences = request.json
       session["user_preferences"] = preferences
       return jsonify({"status": "success"})
   
   @bp.route("/api/get-preferences", methods=["GET"])
   def get_preferences():
       preferences = session.get("user_preferences", {})
       return jsonify({"status": "success", "preferences": preferences})
   ```

## Conclusion

This comprehensive guide should help you successfully deploy the InfoFlow project on Replit. Remember that Replit's free tier has resource limitations that may affect performance for complex simulations. Consider upgrading to a paid plan if you need more resources or plan to use this deployment for production purposes.

For further assistance:
- Explore Replit's documentation at [docs.replit.com](https://docs.replit.com)
- Join the Replit community forum at [replit.com/talk](https://replit.com/talk)
- Contact the InfoFlow project maintainers for project-specific questions