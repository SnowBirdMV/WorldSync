# app/utils/compressed_rotating_handler.py
import os
import logging
import zipfile
from logging.handlers import RotatingFileHandler
from datetime import datetime
from dateutil import tz


class CompressedRotatingFileHandler(RotatingFileHandler):
	def __init__(self, filename, mode='a', maxBytes=0, backupCount=0, encoding=None, delay=False):
		# Create logs directory if needed
		os.makedirs(os.path.dirname(filename), exist_ok=True)

		# Rotate existing log on startup
		if os.path.exists(filename):
			self._rotate_on_startup(filename)

		super().__init__(filename, mode, maxBytes, backupCount, encoding, delay)

	def _rotate_on_startup(self, filename):
		"""Rotate and compress existing log file on application start"""
		timestamp = datetime.now(tz=tz.gettz()).strftime('%Y-%m-%d_%H-%M-%S')
		base_name = os.path.basename(filename)
		archive_name = f"{base_name}.{timestamp}.zip"
		archive_path = os.path.join(os.path.dirname(filename), archive_name)

		with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
			zipf.write(filename, arcname=base_name)

		os.remove(filename)

	def doRollover(self):
		"""Rotate and compress when maxBytes is reached"""
		if self.stream:
			self.stream.close()
			self.stream = None

		timestamp = datetime.now(tz=tz.gettz()).strftime('%Y-%m-%d_%H-%M-%S')
		base_name = os.path.basename(self.baseFilename)
		archive_name = f"{base_name}.{timestamp}.zip"
		archive_path = os.path.join(os.path.dirname(self.baseFilename), archive_name)

		# Compress current log
		with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
			zipf.write(self.baseFilename, arcname=base_name)

		# Remove original log file
		if os.path.exists(self.baseFilename):
			os.remove(self.baseFilename)

		# Create new log file
		if not self.delay:
			self.stream = self._open()
