"""
app/tasks/background_worker.py

Contains the background worker logic that processes queued world merges
via Amulet.
"""

import queue
import os
import tempfile
import zipfile
import logging

from threading import Lock

import amulet
from amulet.api.errors import ChunkLoadError, ChunkDoesNotExist

from app.utils.amulet_merge import merge_amulet_worlds
from app.config import LOCAL_WORLD_DIR

process_queue = queue.Queue()
lock = Lock()

def background_worker():
    """
    Wait for zip paths in process_queue, process each in FIFO,
    merge them into local_world with Amulet. (No Dynmap references.)
    """
    while True:
        zip_path = process_queue.get()  # Block until an item arrives
        if zip_path is None:
            break  # Graceful shutdown if needed
        try:
            process_zip(zip_path)
        except Exception as e:
            logging.error(f"[Background Worker] Error processing {zip_path}: {e}", exc_info=True)
        # Remove the ZIP afterwards
        try:
            os.remove(zip_path)
        except OSError as e:
            logging.warning(f"Failed to delete {zip_path}: {e}")
        process_queue.task_done()

def process_zip(zip_path):
    """
    Extracts the uploaded world, merges with local_world using Amulet,
    then saves.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        extracted_dir = os.path.join(tmpdir, "extracted_world")
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extracted_dir)

        uploaded_world = amulet.load_level(extracted_dir)
        local_world = amulet.load_level(LOCAL_WORLD_DIR)

        merge_amulet_worlds(uploaded_world, local_world)

        local_world.save()
        local_world.close()
        uploaded_world.close()
