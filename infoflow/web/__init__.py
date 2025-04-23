"""Flask application factory for InfoFlow web interface."""

from flask import Flask


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__)

    # Load configuration
    app.config.from_object("config")

    # Register routes
    from infoflow.web import routes

    app.register_blueprint(routes.bp)

    return app
