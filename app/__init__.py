import os
import logging
import threading
from flask import Flask
from dotenv import load_dotenv

from app.tasks.background_worker import background_worker
from app.routes.waypoints import waypoints_bp
from app.routes.merges import merges_bp
# from app.config import LOG_DIR, LOG_FILE  # no rotation logic in here

def create_app():
    load_dotenv()

    app = Flask(__name__)

    # Register Blueprints
    app.register_blueprint(waypoints_bp, url_prefix='/api')
    app.register_blueprint(merges_bp)

    # Start background worker
    worker_thread = threading.Thread(target=background_worker, daemon=True)
    worker_thread.start()

    return app
