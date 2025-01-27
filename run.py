import logging
import os
import zipfile
from datetime import datetime
from app.config import LOG_DIR, LOG_FILE
from app import create_app

def rotate_log_file():
    old_log_path = os.path.join(LOG_DIR, LOG_FILE)
    if os.path.exists(old_log_path):
        mtime = os.path.getmtime(old_log_path)
        ts_str = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d_%H-%M-%S')
        zip_filename = os.path.join(LOG_DIR, f"log_{ts_str}.zip")

        with zipfile.ZipFile(zip_filename, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(old_log_path, arcname=f"log_{ts_str}.log")
        os.remove(old_log_path)

# Clear old handlers
for handler in logging.root.handlers[:]:
    logging.root.removeHandler(handler)

# Ensure logs folder
os.makedirs(LOG_DIR, exist_ok=True)

# Rotate
rotate_log_file()

# Configure new log file
logging.basicConfig(
    filename=os.path.join(LOG_DIR, LOG_FILE),
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

app = create_app()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, threaded=True, debug=False)
