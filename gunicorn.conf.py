# gunicorn.conf.py
import os
import logging
import sys
from app.utils.compressed_rotating_handler import CompressedRotatingFileHandler
from gunicorn.glogging import Logger

# Server config
bind = os.getenv('BIND', '0.0.0.0:5001')
workers = 1
loglevel = os.getenv('LOG_LEVEL', 'info').lower()
accesslog = '-'  # Disable default access log
errorlog = '-'  # Disable default error log

# Logging config
LOG_DIR = os.getenv("LOG_DIR", "logs")
MAX_BYTES = 10 * 1024 * 1024  # 10 MB
BACKUP_COUNT = 5  # Number of compressed archives to keep


class UnifiedLogger(Logger):
	def setup(self, cfg):
		super().setup(cfg)

		# Formatters
		std_formatter = logging.Formatter(
			'[%(asctime)s] [%(process)d] [%(levelname)s] %(message)s'
		)
		access_formatter = logging.Formatter('%(message)s')

		# Application log handler (compressed rotation)
		app_handler = CompressedRotatingFileHandler(
			os.path.join(LOG_DIR, os.getenv("APP_LOG", "application.log")),
			maxBytes=MAX_BYTES,
			backupCount=BACKUP_COUNT
		)
		app_handler.setFormatter(std_formatter)

		# Console handler
		console_handler = logging.StreamHandler(sys.stdout)
		console_handler.setFormatter(std_formatter)

		# Configure root logger
		root_logger = logging.getLogger()
		root_logger.setLevel(os.getenv("LOG_LEVEL", "INFO").upper())
		root_logger.handlers = [app_handler, console_handler]

		# Configure Gunicorn's specific logs
		self.error_log = root_logger
		self.access_log = logging.getLogger('gunicorn.access')
		self.access_log.propagate = False

		# Access log handler (compressed rotation)
		access_handler = CompressedRotatingFileHandler(
			os.path.join(LOG_DIR, os.getenv("GUNICORN_ACCESS_LOG", "gunicorn_access.log")),
			maxBytes=MAX_BYTES,
			backupCount=BACKUP_COUNT
		)
		access_handler.setFormatter(access_formatter)
		self.access_log.addHandler(access_handler)

		# Suppress noisy loggers
		for name in ['werkzeug', 'amulet', 'filelock']:
			logging.getLogger(name).setLevel(logging.WARNING)


logger_class = UnifiedLogger
