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
    if "world_zip" not in request.files:
        logger.warning("Missing 'world_zip' in request")
        return jsonify({"error": "No 'world_zip' file found"}), 400

    uploaded_file = request.files["world_zip"]
    if not uploaded_file.filename.endswith('.zip'):
        logger.warning(f"Invalid file type: {uploaded_file.filename}")
        return jsonify({"error": "Uploaded file must be a zip archive."}), 400

    temp_dir = tempfile.mkdtemp(prefix="upload_")
    saved_zip_path = os.path.join(temp_dir, uploaded_file.filename)
    uploaded_file.save(saved_zip_path)

    logger.info(f"Received ZIP {uploaded_file.filename}, queued for merge")
    process_queue.put(saved_zip_path)

    return jsonify({"status": "ok", "message": "File queued for merging"}), 200

@merges_bp.route("/merge/status", methods=["GET"])
def merge_status():
    current = get_current_job()
    pending = get_pending_jobs()
    return jsonify({
        "current_job": current,
        "pending_jobs": pending,
        "queue_size": len(pending)
    }), 200
