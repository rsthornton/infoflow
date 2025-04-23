# Comprehensive Guide: Deploying InfoFlow on Render with a Custom Domain

This guide provides detailed instructions for deploying the InfoFlow project on Render.com and connecting it to your custom domain.

## Table of Contents

1. [Introduction to Render](#introduction-to-render)
2. [Setting Up Your Render Account](#setting-up-your-render-account)
3. [Preparing Your InfoFlow Project](#preparing-your-infoflow-project)
4. [Deploying to Render](#deploying-to-render)
5. [Setting Up Your Custom Domain](#setting-up-your-custom-domain)
6. [Database Configuration](#database-configuration)
7. [Environment Variables](#environment-variables)
8. [Monitoring and Logs](#monitoring-and-logs)
9. [Updating Your Deployment](#updating-your-deployment)
10. [Troubleshooting Common Issues](#troubleshooting-common-issues)
11. [Performance Optimization](#performance-optimization)
12. [Advanced Configuration](#advanced-configuration)

## Introduction to Render

Render is a cloud platform that makes it easy to deploy web services, static sites, and databases. It's designed to be simple yet powerful, with features like automatic HTTPS, GitHub integration, and global CDN. For the InfoFlow project, Render offers an ideal deployment environment with minimal configuration.

**Benefits for InfoFlow:**
- Zero DevOps required
- Automatic HTTPS
- Custom domain support
- Persistent disk storage
- Built-in logging and monitoring
- Reasonable free tier

## Setting Up Your Render Account

1. **Create an account**
   - Go to [render.com](https://render.com) and sign up for a free account
   - You can sign up using GitHub for seamless integration

2. **Verify your email** and complete the initial setup

3. **Set up billing information (optional)**
   - The free tier is sufficient for demonstration purposes
   - For production use, you may want to upgrade to a paid plan

## Preparing Your InfoFlow Project

Before deploying to Render, you need to make a few adjustments to your project:

### 1. Add Required Files

Create the following files in your project root:

#### Create `render.yaml` for Blueprint Deployment

```yaml
services:
  - type: web
    name: infoflow
    env: python
    plan: free
    buildCommand: pip install -r config/requirements.txt && pip install -e .
    startCommand: gunicorn "infoflow.web:create_app()" --bind 0.0.0.0:$PORT
    envVars:
      - key: PYTHON_VERSION
        value: 3.8.0
      - key: FLASK_ENV
        value: production
      - key: FLASK_DEBUG
        value: 0
    disk:
      name: infoflow-data
      mountPath: /data
      sizeGB: 1
```

#### Add Gunicorn to Your Requirements

Add gunicorn to your `config/requirements.txt` file:
```
gunicorn>=20.1.0
```

### 2. Update Database and File Storage Paths

Create a file called `infoflow/utils/deployment_config.py`:

```python
"""
Configuration utilities for deployment environments.
"""

import os
from pathlib import Path

def get_data_directory():
    """
    Get the appropriate data directory based on the environment.
    
    Returns:
        Path object pointing to the data directory
    """
    # Check if we're running on Render
    if os.environ.get('RENDER'):
        # Use the persistent disk path
        data_dir = Path('/data')
    else:
        # Local development fallback
        data_dir = Path(os.getcwd()) / 'data'
    
    # Ensure the directory exists
    os.makedirs(data_dir, exist_ok=True)
    
    # Create subdirectories
    os.makedirs(data_dir / 'exports', exist_ok=True)
    os.makedirs(data_dir / 'plots', exist_ok=True)
    
    return data_dir
```

### 3. Update Database Path in StatsCollector

Modify `infoflow/utils/simple_stats.py` to use the deployment configuration:

```python
# Add near the top of the file
from infoflow.utils.deployment_config import get_data_directory

# Then modify the __init__ method
def __init__(self, db_path=None):
    """
    Initialize the stats collector.
    """
    if db_path is None:
        # Get the appropriate data directory
        data_dir = get_data_directory()
        db_path = data_dir / "simulation_stats.db"

    self.db_path = str(db_path)
    self.run_id = str(uuid.uuid4())[:8]
    self.init_db()
```

Also update all static methods in `simple_stats.py` that access the database:

```python
@staticmethod
def get_recent_runs(limit=10):
    # ...
    data_dir = get_data_directory()
    db_path = data_dir / "simulation_stats.db"
    # ...

@staticmethod
def get_run_metadata(run_id):
    # ...
    data_dir = get_data_directory()
    db_path = data_dir / "simulation_stats.db"
    # ...

@staticmethod
def get_run_data(run_id):
    # ...
    data_dir = get_data_directory()
    db_path = data_dir / "simulation_stats.db"
    # ...

@staticmethod
def export_run(run_id, filepath=None):
    # ...
    if not filepath:
        export_dir = get_data_directory() / "exports"
        os.makedirs(export_dir, exist_ok=True)
        filepath = export_dir / f"simulation_{run_id}.json"
    # ...
```

### 4. Update Chart Generation in Routes

Modify the chart generation code in `infoflow/web/routes.py` to use the persistent storage when necessary:

```python
# Add import at the top
from infoflow.utils.deployment_config import get_data_directory

# Then modify the chart directory definition in metrics_dashboard and generate_metrics_charts functions:

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
    # Fallback to a directory in persistent storage
    data_dir = get_data_directory()
    static_dir = os.path.join(str(data_dir), "charts")
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

### 5. Create a Procfile (Optional but Recommended)

Create a `Procfile` in your project root:

```
web: gunicorn "infoflow.web:create_app()" --bind 0.0.0.0:$PORT --log-file -
```

### 6. Ensure Matplotlib Uses a Non-Interactive Backend

Create a small initialization module at `infoflow/utils/init_env.py`:

```python
"""
Initialize environment settings for different deployment scenarios.
"""

import os
import matplotlib

# Force matplotlib to use a non-interactive backend on servers
if os.environ.get('RENDER') or os.environ.get('PRODUCTION'):
    matplotlib.use('Agg')
```

Then import this at the top of `infoflow/web/__init__.py`:

```python
# Initialize environment first
from infoflow.utils.init_env import *
```

## Deploying to Render

Now that your project is prepared, you can deploy it to Render:

### Method 1: Blueprint Deployment (Recommended)

1. **Push your changes to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Render deployment"
   git push
   ```

2. **Create a new Web Service in Render**
   - Go to your Render dashboard
   - Click "New +" button
   - Select "Blueprint"
   - Connect your GitHub account if not already connected
   - Select your InfoFlow repository
   - Render will automatically detect the `render.yaml` file
   - Click "Apply" to deploy

3. **Monitor the deployment**
   - Render will show the build logs in real-time
   - Wait for the deployment to complete
   - You'll receive a URL for your application (e.g., `https://infoflow.onrender.com`)

### Method 2: Manual Web Service Configuration

If you prefer to configure the service manually:

1. **Go to your Render dashboard**
   - Click "New +" button
   - Select "Web Service"

2. **Connect your repository**
   - Connect your GitHub account
   - Select your InfoFlow repository

3. **Configure your service**
   - Name: `infoflow` (or any name you prefer)
   - Environment: `Python`
   - Region: Choose the region closest to your users
   - Branch: `main` (or your deployment branch)
   - Build Command: `pip install -r config/requirements.txt && pip install -e .`
   - Start Command: `gunicorn "infoflow.web:create_app()" --bind 0.0.0.0:$PORT`
   - Plan: Free

4. **Add environment variables**
   - PYTHON_VERSION: `3.8.0`
   - FLASK_ENV: `production`
   - FLASK_DEBUG: `0`

5. **Set up disk storage**
   - Click "Advanced" 
   - Under "Disks", add a new disk:
     - Name: `infoflow-data`
     - Mount Path: `/data`
     - Size: 1 GB

6. **Create Web Service**
   - Click "Create Web Service"
   - Monitor the deployment logs

## Setting Up Your Custom Domain

After your InfoFlow application is deployed and working on Render's default subdomain, you can connect your custom domain:

### 1. Add Your Custom Domain in Render

1. **Go to your Web Service dashboard**
   - Select the InfoFlow service you just deployed

2. **Navigate to the "Settings" tab**
   - Scroll down to "Custom Domains"
   - Click "Add Custom Domain"

3. **Enter your domain**
   - Type your domain name (e.g., `infoflow.example.com`)
   - Click "Save"

4. **Note the verification instructions**
   - Render will provide DNS records that you need to add to your domain registrar

### 2. Configure DNS Records at Your Domain Registrar

1. **Log in to your domain registrar**
   - This could be Namecheap, GoDaddy, Google Domains, etc.

2. **Add a CNAME record** (for subdomains like `infoflow.example.com`)
   - Type: `CNAME`
   - Host/Name: `infoflow` (or whatever subdomain you want)
   - Value/Target: Your Render URL (e.g., `infoflow.onrender.com`)
   - TTL: `3600` (or recommended value)

   **OR**

   **Add an ANAME/ALIAS record** (for apex domains like `example.com`)
   - Type: `ANAME` or `ALIAS` (depends on your registrar)
   - Host/Name: `@`
   - Value/Target: Your Render URL (e.g., `infoflow.onrender.com`)
   - TTL: `3600` (or recommended value)

3. **Wait for DNS propagation**
   - This can take anywhere from a few minutes to 48 hours
   - You can check propagation status using tools like [dnschecker.org](https://dnschecker.org)

4. **Verify domain ownership**
   - Render will automatically verify your domain once DNS propagation is complete
   - Render will also automatically provision an SSL certificate via Let's Encrypt

## Database Configuration

InfoFlow uses SQLite, which works well with Render's persistent disk storage:

### 1. Understanding Persistent Storage on Render

- Render provides persistent SSD storage for your application
- The disk is mounted at the path you specified in your configuration (`/data` in our example)
- This storage persists across deployments and restarts

### 2. Database Backup Strategies

1. **Scheduled backups using Render Cron Jobs**

   Create a new file `scripts/backup_db.py`:

   ```python
   #!/usr/bin/env python3
   """
   Script to backup the InfoFlow database to cloud storage.
   """
   
   import os
   import shutil
   import datetime
   from pathlib import Path
   from infoflow.utils.deployment_config import get_data_directory
   
   def backup_database():
       """Create a backup of the SQLite database."""
       # Get data directory and database path
       data_dir = get_data_directory()
       db_path = data_dir / "simulation_stats.db"
       
       # Create backups directory if it doesn't exist
       backup_dir = data_dir / "backups"
       os.makedirs(backup_dir, exist_ok=True)
       
       # Create a timestamped backup file
       timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
       backup_path = backup_dir / f"simulation_stats_{timestamp}.db"
       
       # Copy the database file
       shutil.copy2(db_path, backup_path)
       print(f"Database backed up to {backup_path}")
       
       # Clean up old backups (keep only the 5 most recent)
       backup_files = sorted(backup_dir.glob("simulation_stats_*.db"))
       for old_backup in backup_files[:-5]:
           os.remove(old_backup)
           print(f"Removed old backup: {old_backup}")
       
   if __name__ == "__main__":
       backup_database()
   ```

2. **Set up a Cron Job on Render**
   - Go to your Render dashboard
   - Click "New +" and select "Cron Job"
   - Name: `infoflow-db-backup`
   - Schedule: `0 0 * * *` (daily at midnight)
   - Command: `python scripts/backup_db.py`
   - Connect it to the same repository as your web service

### 3. Testing Database Connectivity

Create a file `scripts/test_db.py`:

```python
#!/usr/bin/env python3
"""
Test database connectivity and functionality.
"""

from infoflow.utils.simple_stats import StatsCollector
import os
from pathlib import Path

def test_database():
    """Test database connection and basic operations."""
    try:
        # Initialize collector (creates DB if it doesn't exist)
        collector = StatsCollector()
        print(f"Database initialized at: {collector.db_path}")
        
        # Start a test run
        test_params = {"test": True, "environment": "render"}
        run_id = collector.start_run(test_params)
        print(f"Test run started with ID: {run_id}")
        
        # Record some test metrics
        collector.record_step(0, {"test_metric": 1.0})
        print("Test metrics recorded")
        
        # Retrieve and validate
        run_data = StatsCollector.get_run_data(run_id)
        if run_data and run_data.get("metrics") and "0" in run_data["metrics"]:
            print("Successfully retrieved test data")
            return True
        else:
            print("Failed to retrieve test data")
            return False
            
    except Exception as e:
        print(f"Database test failed with error: {e}")
        return False

if __name__ == "__main__":
    success = test_database()
    exit(0 if success else 1)
```

Run this script on Render via the Shell tab to verify database functionality.

## Environment Variables

### 1. Essential Environment Variables

Render allows you to set environment variables for your service. Here are the key variables you should configure:

- **FLASK_ENV**: Set to `production` for deployment
- **FLASK_DEBUG**: Set to `0` for production
- **PYTHON_VERSION**: Set to `3.8.0` or your preferred version

### 2. Adding Custom Environment Variables

You can add additional environment variables for application configuration:

1. **Go to your Web Service dashboard**
   - Select the InfoFlow service
   - Go to the "Environment" tab

2. **Add variables as needed**
   - Example: `MAX_SIMULATION_STEPS`: `100`
   - Example: `DEFAULT_NETWORK_TYPE`: `small_world`

3. **Accessing variables in your code**
   ```python
   import os
   
   max_steps = int(os.environ.get('MAX_SIMULATION_STEPS', 50))
   network_type = os.environ.get('DEFAULT_NETWORK_TYPE', 'small_world')
   ```

### 3. Sensitive Information

For sensitive information like API keys:

1. **Add as Secret Environment Variables**
   - In Render, all environment variables are treated securely
   - They're encrypted at rest and never logged

2. **Access in code the same way as regular environment variables**
   ```python
   api_key = os.environ.get('API_KEY')
   ```

## Monitoring and Logs

### 1. Accessing Logs

Render provides comprehensive logging for your application:

1. **Go to your Web Service dashboard**
   - Select the InfoFlow service
   - Click on the "Logs" tab

2. **View different log types**
   - Build logs: Show the deployment process
   - Runtime logs: Show application output
   - Events: Show service lifecycle events

### 2. Custom Logging Configuration

Enhance your application's logging to make it more useful in production:

1. **Create a logging configuration**

   Create a file `infoflow/utils/logging_config.py`:

   ```python
   """
   Configure logging for different environments.
   """
   
   import os
   import sys
   import logging
   
   def configure_logging(app=None):
       """
       Configure logging for the application.
       
       Args:
           app: Flask application (optional)
       """
       # Determine if we're in production
       is_production = os.environ.get('RENDER') or os.environ.get('FLASK_ENV') == 'production'
       
       # Set up format based on environment
       if is_production:
           log_format = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
           log_level = logging.INFO
       else:
           log_format = '[%(asctime)s] %(levelname)s in %(module)s [%(pathname)s:%(lineno)d]: %(message)s'
           log_level = logging.DEBUG
       
       # Configure root logger
       root_logger = logging.getLogger()
       root_logger.setLevel(log_level)
       
       # Create console handler if it doesn't exist
       if not root_logger.handlers:
           console_handler = logging.StreamHandler(sys.stdout)
           console_handler.setLevel(log_level)
           formatter = logging.Formatter(log_format)
           console_handler.setFormatter(formatter)
           root_logger.addHandler(console_handler)
       
       # Configure Flask logger if app provided
       if app:
           app.logger.setLevel(log_level)
           
           # Ensure Flask uses our handlers
           for handler in root_logger.handlers:
               app.logger.addHandler(handler)
   ```

2. **Use this configuration in your application**
   
   Update `infoflow/web/__init__.py`:

   ```python
   from infoflow.utils.init_env import *
   from infoflow.utils.logging_config import configure_logging
   from flask import Flask
   
   def create_app():
       """Create and configure the Flask application."""
       app = Flask(__name__)
       
       # Configure logging
       configure_logging(app)
       
       # Load configuration
       app.config.from_object("config")
       
       # Register routes
       from infoflow.web import routes
       app.register_blueprint(routes.bp)
       
       return app
   ```

### 3. Monitoring Application Health

Add a health check endpoint to monitor your application:

Update `infoflow/web/routes.py`:

```python
@bp.route("/health")
def health_check():
    """
    Health check endpoint for monitoring.
    
    Returns:
        JSON response with application health status
    """
    health = {
        "status": "healthy",
        "version": getattr(infoflow, "__version__", "unknown"),
        "database_connected": False
    }
    
    # Check database connectivity
    try:
        # Try to connect to the database
        collector = StatsCollector()
        conn = sqlite3.connect(collector.db_path, timeout=5)
        conn.execute("SELECT 1")
        conn.close()
        health["database_connected"] = True
    except Exception as e:
        app.logger.error(f"Database health check failed: {e}")
        health["status"] = "degraded"
        health["database_error"] = str(e)
    
    # Return status code based on health
    status_code = 200 if health["status"] == "healthy" else 503
    return jsonify(health), status_code
```

## Updating Your Deployment

### 1. Continuous Deployment

Render can automatically deploy updates when you push to your repository:

1. **Automatic deployments are enabled by default**
   - Each push to your configured branch will trigger a new build

2. **To disable automatic deployments**
   - Go to your Web Service dashboard
   - Select the "Settings" tab
   - Scroll to "Auto-Deploy"
   - Toggle it off if you prefer manual deployments

### 2. Manual Deployment

You can also manually deploy your application:

1. **Go to your Web Service dashboard**
   - Click the "Manual Deploy" button
   - Select "Deploy latest commit" or "Deploy specific commit"

2. **Monitor the deployment**
   - Render will show the build logs in real-time
   - Your service will be updated once the build completes

### 3. Database Migrations

For SQLite schema changes, create a migrations script:

```python
#!/usr/bin/env python3
"""
Database migration script for InfoFlow.
"""

import sqlite3
import logging
from infoflow.utils.deployment_config import get_data_directory

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

def run_migrations():
    """Run all pending database migrations."""
    data_dir = get_data_directory()
    db_path = data_dir / "simulation_stats.db"
    
    logger.info(f"Running migrations on database: {db_path}")
    
    # Connect to the database
    conn = sqlite3.connect(db_path)
    c = conn.cursor()
    
    # Create migrations table if it doesn't exist
    c.execute("""
    CREATE TABLE IF NOT EXISTS migrations (
        id INTEGER PRIMARY KEY,
        name TEXT UNIQUE,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    
    # Get list of applied migrations
    c.execute("SELECT name FROM migrations")
    applied = set(row[0] for row in c.fetchall())
    
    # Define migrations
    migrations = [
        {
            "name": "add_content_metrics_table",
            "sql": """
            CREATE TABLE IF NOT EXISTS content_metrics (
                id INTEGER PRIMARY KEY,
                run_id TEXT,
                step INTEGER,
                content_id TEXT,
                shares INTEGER,
                truth_score REAL,
                FOREIGN KEY (run_id) REFERENCES simulation_runs (run_id)
            )
            """
        },
        # Add more migrations here as needed
    ]
    
    # Apply pending migrations
    for migration in migrations:
        name = migration["name"]
        if name not in applied:
            logger.info(f"Applying migration: {name}")
            try:
                c.execute(migration["sql"])
                c.execute("INSERT INTO migrations (name) VALUES (?)", (name,))
                conn.commit()
                logger.info(f"Successfully applied migration: {name}")
            except Exception as e:
                logger.error(f"Migration failed: {name}")
                logger.error(str(e))
                conn.rollback()
        else:
            logger.info(f"Migration already applied: {name}")
    
    # Close the connection
    conn.close()
    logger.info("Migrations completed")

if __name__ == "__main__":
    run_migrations()
```

## Troubleshooting Common Issues

### 1. Deployment Failures

**Issue**: Your deployment fails during the build process.

**Solutions**:
- Check the build logs for specific errors
- Ensure all dependencies are listed in `requirements.txt`
- Verify that your `render.yaml` file is correctly formatted
- Test locally with `pip install -r config/requirements.txt && pip install -e .`

### 2. Application Crashes

**Issue**: Your application starts but crashes shortly after.

**Solutions**:
- Check the runtime logs for error messages
- Ensure database paths are correctly configured for Render
- Verify that matplotlib is using a non-interactive backend
- Add more detailed logging to identify the source of the crash

### 3. Database Connectivity Issues

**Issue**: Application can't connect to or write to the database.

**Solutions**:
- Ensure the disk is properly mounted at `/data`
- Check permissions on the data directory
- Verify that the database path is correctly configured
- Run the database test script via Render Shell

### 4. Custom Domain Not Working

**Issue**: Your custom domain isn't connecting to your Render service.

**Solutions**:
- Double-check DNS settings at your domain registrar
- Ensure you've added the correct CNAME or ALIAS record
- Wait for DNS propagation (can take up to 48 hours)
- Verify SSL certificate provision in Render dashboard

### 5. Slow Performance

**Issue**: Your application is running slowly on Render.

**Solutions**:
- Check if you're on the free tier (which has CPU/RAM limitations)
- Optimize database queries
- Implement caching for expensive operations
- Consider upgrading to a paid plan for more resources

## Performance Optimization

### 1. Caching Strategies

Implement caching to improve performance:

```python
# Add to infoflow/utils/cache.py
"""
Simple caching utilities for InfoFlow.
"""

import time
import functools

# Simple in-memory cache
_cache = {}

def timed_cache(seconds=300):
    """
    Decorator that caches a function's return value for a specified period.
    
    Args:
        seconds: Number of seconds to cache the result
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create a cache key from function name and arguments
            key = str(func.__name__) + str(args) + str(kwargs)
            
            # Check if the result is cached and not expired
            if key in _cache:
                result, timestamp = _cache[key]
                if time.time() - timestamp < seconds:
                    return result
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            _cache[key] = (result, time.time())
            return result
        return wrapper
    return decorator
```

Then use this decorator in your code:

```python
from infoflow.utils.cache import timed_cache

@timed_cache(seconds=60)
def get_cached_network_data(model):
    """Get network data with caching."""
    # Expensive operation to extract network data
    return data
```

### 2. Optimizing Matplotlib Usage

Matplotlib can be resource-intensive. Optimize its usage with these strategies:

1. **Use a streamlined backend**
   ```python
   import matplotlib
   matplotlib.use('Agg')  # Non-interactive backend for servers
   ```

2. **Reuse figures and axes**
   ```python
   fig, ax = plt.subplots(figsize=(8, 5))
   # Reuse ax for multiple plots
   ax.clear()
   ```

3. **Close figures explicitly**
   ```python
   plt.close(fig)  # Release memory
   ```

4. **Generate charts on demand, not in advance**
   ```python
   @bp.route("/api/chart/<chart_name>")
   def get_chart(chart_name):
       """Generate and serve a chart on demand."""
       # Generate the chart here
       return send_file(chart_path)
   ```

### 3. Database Optimization

Optimize SQLite performance:

1. **Add indexes for frequently queried columns**
   ```python
   c.execute("CREATE INDEX IF NOT EXISTS idx_timestep_data_run_id ON timestep_data (run_id)")
   c.execute("CREATE INDEX IF NOT EXISTS idx_timestep_data_step ON timestep_data (step)")
   ```

2. **Use connection pooling**
   ```python
   # Create a connection pool module
   """
   SQLite connection pool for InfoFlow.
   """
   
   import sqlite3
   import threading
   from infoflow.utils.deployment_config import get_data_directory
   
   class SQLiteConnectionPool:
       """Simple connection pool for SQLite."""
       
       _instance = None
       _lock = threading.Lock()
       
       @classmethod
       def get_instance(cls):
           """Get singleton instance of the connection pool."""
           if cls._instance is None:
               with cls._lock:
                   if cls._instance is None:
                       cls._instance = SQLiteConnectionPool()
           return cls._instance
       
       def __init__(self):
           """Initialize the connection pool."""
           self.connections = []
           self.max_connections = 5
           self.db_path = str(get_data_directory() / "simulation_stats.db")
           
       def get_connection(self):
           """Get a connection from the pool or create a new one."""
           with self._lock:
               if self.connections:
                   return self.connections.pop()
               else:
                   conn = sqlite3.connect(self.db_path, timeout=10)
                   conn.execute("PRAGMA journal_mode=WAL")
                   return conn
       
       def return_connection(self, conn):
           """Return a connection to the pool."""
           with self._lock:
               if len(self.connections) < self.max_connections:
                   self.connections.append(conn)
               else:
                   conn.close()
   ```

## Advanced Configuration

### 1. Setting Up Authentication

For protected endpoints, implement basic authentication:

1. **Add Flask-HTTPAuth to your requirements**:
   ```
   pip install Flask-HTTPAuth
   ```

2. **Implement authentication**:
   ```python
   # In infoflow/web/auth.py
   """
   Authentication utilities for the InfoFlow web interface.
   """
   
   import os
   from flask_httpauth import HTTPBasicAuth
   from werkzeug.security import generate_password_hash, check_password_hash
   
   # Create auth object
   auth = HTTPBasicAuth()
   
   # User database (in production, use environment variables)
   users = {
       "admin": generate_password_hash(os.environ.get("ADMIN_PASSWORD", "default_password"))
   }
   
   @auth.verify_password
   def verify_password(username, password):
       """Verify username and password."""
       if username in users and check_password_hash(users.get(username), password):
           return username
       return None
   ```

3. **Use authentication in routes**:
   ```python
   # In routes.py
   from infoflow.web.auth import auth
   
   @bp.route("/admin/dashboard")
   @auth.login_required
   def admin_dashboard():
       """Admin dashboard that requires authentication."""
       return render_template("admin_dashboard.html", username=auth.current_user())
   ```

### 2. Implementing Background Tasks

For long-running tasks, implement a background worker:

1. **Create a worker script**:
   ```python
   # In scripts/worker.py
   """
   Background worker for long-running InfoFlow tasks.
   """
   
   import os
   import time
   import threading
   import json
   from pathlib import Path
   import queue
   
   from infoflow.core.model import create_model
   from infoflow.utils.simple_stats import StatsCollector
   from infoflow.utils.deployment_config import get_data_directory
   
   # Task queue
   task_queue = queue.Queue()
   
   # Results storage
   task_results = {}
   
   def worker_thread():
       """Worker thread that processes tasks from the queue."""
       while True:
           try:
               # Get a task from the queue
               task_id, task_type, params = task_queue.get()
               
               # Process the task
               if task_type == "simulation":
                   run_simulation(task_id, params)
               elif task_type == "analysis":
                   run_analysis(task_id, params)
               else:
                   task_results[task_id] = {
                       "status": "error",
                       "error": f"Unknown task type: {task_type}"
                   }
               
               # Mark the task as done
               task_queue.task_done()
           except Exception as e:
               print(f"Error in worker thread: {e}")
               time.sleep(1)  # Avoid spinning if there's a persistent error
   
   def start_worker():
       """Start the worker thread."""
       thread = threading.Thread(target=worker_thread, daemon=True)
       thread.start()
       return thread
   
   def enqueue_task(task_type, params):
       """
       Add a task to the queue.
       
       Args:
           task_type: Type of task (e.g., "simulation", "analysis")
           params: Parameters for the task
           
       Returns:
           Task ID
       """
       task_id = f"task_{int(time.time())}_{len(task_results) + 1}"
       task_queue.put((task_id, task_type, params))
       task_results[task_id] = {"status": "queued"}
       return task_id
   
   def get_task_status(task_id):
       """Get the status of a task."""
       return task_results.get(task_id, {"status": "not_found"})
   
   def run_simulation(task_id, params):
       """Run a simulation task."""
       try:
           # Update task status
           task_results[task_id] = {"status": "running", "progress": 0}
           
           # Create stats collector
           collector = StatsCollector()
           collector.run_id = task_id
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
               
               # Update task status
               progress = (step + 1) / steps
               task_results[task_id] = {"status": "running", "progress": progress}
           
           # Complete the task
           task_results[task_id] = {
               "status": "completed",
               "run_id": collector.run_id,
               "steps": steps,
               "completion_time": time.time()
           }
           
       except Exception as e:
           print(f"Error in simulation task {task_id}: {e}")
           task_results[task_id] = {
               "status": "failed",
               "error": str(e),
               "completion_time": time.time()
           }
   
   def run_analysis(task_id, params):
       """Run an analysis task."""
       # Similar implementation as run_simulation
       pass
   
   # Start the worker thread when this module is imported
   worker_thread_instance = start_worker()
   ```

2. **Add API endpoints for background tasks**:
   ```python
   # In routes.py
   import sys
   import importlib.util
   
   # Load the worker module
   worker_path = Path(__file__).parent.parent.parent / "scripts" / "worker.py"
   spec = importlib.util.spec_from_file_location("worker", worker_path)
   worker = importlib.util.module_from_spec(spec)
   spec.loader.exec_module(worker)
   
   @bp.route("/api/start-task", methods=["POST"])
   def start_task():
       """Start a task in the background."""
       data = request.json
       task_type = data.get("task_type")
       params = data.get("params", {})
       
       task_id = worker.enqueue_task(task_type, params)
       return jsonify({"status": "success", "task_id": task_id})
   
   @bp.route("/api/task-status/<task_id>", methods=["GET"])
   def get_task_status(task_id):
       """Get the status of a background task."""
       status = worker.get_task_status(task_id)
       return jsonify({"status": "success", "task": status})
   ```

## Conclusion

This comprehensive guide has provided detailed instructions for deploying the InfoFlow project on Render with a custom domain. By following these steps, you can have a professional, secure, and reliable deployment of your application.

The optimizations and advanced configurations outlined in this guide will help you scale your application as needed, while the troubleshooting section should assist with resolving common issues.

Remember that Render's free tier is suitable for demonstration purposes, but for production use, you may want to consider upgrading to a paid plan for better performance and more resources.

For additional assistance:
- Consult the [Render documentation](https://render.com/docs)
- Join the [Render community](https://community.render.com/)
- Visit the [Render status page](https://status.render.com/) for service updates