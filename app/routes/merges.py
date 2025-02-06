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
    job = get_current_job()
    pending = get_pending_jobs()

    # Only include chunk info if the current stage is 'amulet merge'
    if job and job.get("stage") == "amulet merge":
        total_chunks = job.get("total_chunks")
        current_chunk = job.get("current_chunk")
    else:
        total_chunks = None
        current_chunk = None

    # Only include render progress if the current stage is 'bluemap render'
    render_progress = job.get("render_progress") if job and job.get("stage") == "bluemap render" else None

    return jsonify({
        "current_job": job.get("current_job") if job else None,
        "stage": job.get("stage") if job else None,
        "total_chunks": total_chunks,
        "current_chunk": current_chunk,
        "render_progress": render_progress,
        "pending_jobs": pending,
        "queue_size": len(pending)
    }), 200
