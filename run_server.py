#!/usr/bin/env python3
"""
Flask web server for InfoFlow.

This script runs the Flask server for the InfoFlow web application.
"""

from infoflow.web import create_app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)