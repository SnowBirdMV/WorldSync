# app/__init__.py
import logging
from flask import Flask
from dotenv import load_dotenv


def create_app():
	load_dotenv()
	app = Flask(__name__)

	# Get root logger configuration
	root_logger = logging.getLogger()
	app.logger.handlers = root_logger.handlers
	app.logger.setLevel(root_logger.level)
	app.logger.propagate = False  # Prevent Flask-specific propagation

	# Register blueprints
	from app.routes.waypoints import waypoints_bp
	from app.routes.merges import merges_bp
	app.register_blueprint(waypoints_bp, url_prefix='/api')
	app.register_blueprint(merges_bp)

	# Start background worker
	from app.tasks.background_worker import background_worker
	import threading
	worker_thread = threading.Thread(target=background_worker, daemon=True)
	worker_thread.start()

	return app
