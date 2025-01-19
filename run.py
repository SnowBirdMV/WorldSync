"""
run.py

Entry point to start the Flask application, ensuring logs are written to file.
"""

import logging
import os

# Import your constants for log-paths
from app.config import LOG_DIR, LOG_FILE
from app import create_app

# 1) Clear out any old handlers so our config takes precedence.
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# 2) Make sure logs/ directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# 3) Configure the root logger to write DEBUG+ messages to file
logging.basicConfig(
    filename=os.path.join(LOG_DIR, LOG_FILE),
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# 4) Create the Flask app
app = create_app()

if __name__ == '__main__':
    # Enable debug=True if you wish, logging should still go to the file
    app.run(host='0.0.0.0', port=5001, threaded=True, debug=True)
