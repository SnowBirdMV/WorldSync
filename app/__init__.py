"""
app/__init__.py

Sets up the Flask application by creating and configuring the app instance,
initializing logging, environment variables, and starting the background worker.
"""

import os
import logging
import threading

from flask import Flask
from dotenv import load_dotenv

from app.config import LOG_DIR, LOG_FILE
from app.tasks.background_worker import background_worker, process_queue

# Load environment variables from .env file as soon as possible
load_dotenv()


def create_app():
    """
    Creates and configures the Flask application, including logging
    and registering blueprints/routes.
    """
    # Ensure the logging directory exists
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)

    # Configure logging
    logging.basicConfig(
        filename=os.path.join(LOG_DIR, LOG_FILE),
        level=logging.DEBUG,  # Set to DEBUG for detailed logs
        format='%(asctime)s %(levelname)s: %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    app = Flask(__name__)

    # Register Blueprints (Waypoints, Merges, etc.)
    from app.routes.waypoints import waypoints_bp
    from app.routes.merges import merges_bp

    app.register_blueprint(waypoints_bp, url_prefix='/api')
    app.register_blueprint(merges_bp)

    # Start background worker thread for Amulet merges
    worker_thread = threading.Thread(target=background_worker, daemon=True)
    worker_thread.start()

    return app
