# app/__init__.py
import os
import logging
import threading
from flask import Flask
from dotenv import load_dotenv

from app.tasks.background_worker import background_worker
from app.routes.waypoints import waypoints_bp
from app.routes.merges import merges_bp

def create_app():
    load_dotenv()

    app = Flask(__name__)

    # Register Blueprints
    app.register_blueprint(waypoints_bp, url_prefix='/api')
    app.register_blueprint(merges_bp)

    # --- Configure Logging with Gunicorn ---
    # Gunicorn populates 'gunicorn.error' logger; attach its handlers to our Flask app logger.
    gunicorn_logger = logging.getLogger('gunicorn.error')
    if gunicorn_logger and gunicorn_logger.handlers:
        app.logger.handlers = gunicorn_logger.handlers
        app.logger.setLevel(gunicorn_logger.level)
    else:
        # If not running under Gunicorn, fallback to a basic config
        logging.basicConfig(level=logging.DEBUG)

    # Start background worker thread (daemon)
    worker_thread = threading.Thread(target=background_worker, daemon=True)
    worker_thread.start()

    return app
