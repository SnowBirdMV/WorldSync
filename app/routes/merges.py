"""
app/routes/merges.py

Contains the Flask route for uploading a zipped world file,
which is queued for background merging using Amulet.
"""

from flask import Blueprint, request, jsonify
from app.tasks.background_worker import process_queue

merges_bp = Blueprint('merges', __name__)

@merges_bp.route("/merge", methods=["POST"])
def merge_worlds():
    """
    Immediately accepts a zipped world, places it in a queue,
    and returns 200 OK. The background worker merges it later.
    """
    if "world_zip" not in request.files:
        return jsonify({"error": "No 'world_zip' file found"}), 400

    uploaded_file = request.files["world_zip"]

    if not uploaded_file.filename.endswith('.zip'):
        return jsonify({"error": "Uploaded file must be a zip archive."}), 400

    import tempfile
    import os

    temp_dir = tempfile.mkdtemp(prefix="upload_")
    saved_zip_path = os.path.join(temp_dir, uploaded_file.filename)
    uploaded_file.save(saved_zip_path)

    process_queue.put(saved_zip_path)

    return jsonify({"status": "ok", "message": "File accepted and queued for merging"}), 200
