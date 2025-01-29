# app/routes/merges.py
from flask import Blueprint, request, jsonify
import logging
import os
import tempfile

from app.tasks.background_worker import process_queue, get_current_job, get_pending_jobs

merges_bp = Blueprint('merges', __name__)
logger = logging.getLogger(__name__)

@merges_bp.route("/merge", methods=["POST"])
def merge_worlds():
    """
    Accepts a .zip file, saves it to a temp directory, and queues it for background processing.
    """
    if "world_zip" not in request.files:
        logger.warning("POST /merge called without 'world_zip' in request.")
        return jsonify({"error": "No 'world_zip' file found"}), 400

    uploaded_file = request.files["world_zip"]
    if not uploaded_file.filename.endswith('.zip'):
        logger.warning(f"POST /merge called with non-zip file: {uploaded_file.filename}")
        return jsonify({"error": "Uploaded file must be a zip archive."}), 400

    temp_dir = tempfile.mkdtemp(prefix="upload_")
    saved_zip_path = os.path.join(temp_dir, uploaded_file.filename)
    uploaded_file.save(saved_zip_path)

    logger.info(f"Received ZIP {uploaded_file.filename}, saved to {saved_zip_path}, now queuing for merge.")
    process_queue.put(saved_zip_path)

    return jsonify({"status": "ok", "message": "File accepted and queued for merging"}), 200

@merges_bp.route("/merge/status", methods=["GET"])
def merge_status():
    """
    Returns JSON with:
      - current_job: the path to the .zip currently being processed (or None)
      - pending_jobs: list of .zip paths waiting in the queue
      - queue_size: how many items are waiting
    """
    current = get_current_job()
    pending = get_pending_jobs()
    status = {
        "current_job": current,
        "pending_jobs": pending,
        "queue_size": len(pending)
    }
    return jsonify(status), 200
