# app/tasks/background_worker.py
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

# Track current job
current_job = None

def get_current_job():
    """Returns the path of the zip file currently being processed, or None."""
    global current_job
    return current_job

def get_pending_jobs():
    """
    Returns a list of the *remaining* queued zip paths (not including the currently processing one).
    Accessing process_queue.queue directly is not ideal, but for monitoring it’s acceptable if locked.
    """
    with lock:
        return list(process_queue.queue)

def background_worker():
    """
    The infinite loop that pulls zip paths off process_queue,
    merges them into local_world with Amulet, then cleans up.
    """
    logger = logging.getLogger(__name__)
    global current_job

    while True:
        zip_path = process_queue.get()  # blocks until an item arrives
        if zip_path is None:
            # Means "shut down" if we ever want to break the loop gracefully.
            break

        try:
            # Mark as current
            current_job = zip_path
            logger.info(f"[Background Worker] Starting merge for {zip_path}")
            process_zip(zip_path)
            logger.info(f"[Background Worker] Finished merge for {zip_path}")
        except Exception as e:
            logger.error(f"[Background Worker] Error processing {zip_path}: {e}", exc_info=True)
        finally:
            # Always remove the zip file afterward
            try:
                os.remove(zip_path)
                logger.info(f"[Background Worker] Deleted {zip_path} after processing.")
            except OSError as e:
                logger.warning(f"[Background Worker] Failed to delete {zip_path}: {e}")

            # Mark job as done and clear current_job
            current_job = None
            process_queue.task_done()

def process_zip(zip_path):
    """
    Extract the uploaded world, merges with local_world using Amulet, then saves/closes.
    """
    logger = logging.getLogger(__name__)

    with tempfile.TemporaryDirectory() as tmpdir:
        extracted_dir = os.path.join(tmpdir, "extracted_world")
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(extracted_dir)

        logger.info(f"Extracted {zip_path} into {extracted_dir}")

        uploaded_world = amulet.load_level(extracted_dir)
        local_world = amulet.load_level(LOCAL_WORLD_DIR)

        merge_amulet_worlds(uploaded_world, local_world)
        logger.info(f"Merged uploaded chunks from {zip_path} into local world at {LOCAL_WORLD_DIR}")

        # Save and close
        local_world.save()
        local_world.close()
        uploaded_world.close()
        logger.info(f"Saved and closed worlds for {zip_path}")
