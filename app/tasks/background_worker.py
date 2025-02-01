# app/tasks/background_worker.py
import queue
import os
import tempfile
import zipfile
import logging
from threading import Lock
from filelock import FileLock  # <-- Already imported
import amulet
from amulet.api.errors import ChunkLoadError, ChunkDoesNotExist
from app.utils.amulet_merge import merge_amulet_worlds
from app.config import LOCAL_WORLD_DIR

logger = logging.getLogger(__name__)
logger.propagate = True  # Ensure we use root logger handlers

process_queue = queue.Queue()
lock = Lock()
current_job = None

# Global lock file path for cross-process safety
WORLD_LOCK_PATH = os.path.join(LOCAL_WORLD_DIR, ".world_lock.lock")


def get_current_job():
    global current_job
    return current_job


def get_pending_jobs():
    with lock:
        return list(process_queue.queue)


def background_worker():
    global current_job
    while True:
        zip_path = process_queue.get()
        if zip_path is None:
            break

        try:
            current_job = zip_path
            logger.info(f"Starting merge for {zip_path}")
            process_zip(zip_path)
            logger.info(f"Finished merge for {zip_path}")
        except Exception as e:
            logger.error(f"Error processing {zip_path}: {e}", exc_info=True)
        finally:
            try:
                os.remove(zip_path)
                logger.info(f"Deleted {zip_path} after processing.")
            except OSError as e:
                logger.warning(f"Failed to delete {zip_path}: {e}")
            current_job = None
            process_queue.task_done()


def process_zip(zip_path):
    # Create cross-process file lock; wait indefinitely for the lock
    world_lock = FileLock(WORLD_LOCK_PATH, timeout=-1)

    with world_lock:  # Acquire the lock before processing
        with tempfile.TemporaryDirectory() as tmpdir:
            extracted_dir = os.path.join(tmpdir, "extracted_world")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extracted_dir)

            logger.debug(f"Extracted {zip_path} into {extracted_dir}")

            # Load worlds inside the lock context
            uploaded_world = amulet.load_level(extracted_dir)
            local_world = amulet.load_level(LOCAL_WORLD_DIR)

            try:
                # Import our new RCON helper functions
                from app.utils.rcon_helper import bluemap_stop, bluemap_start, cleanlight_at

                # Disable BlueMap before merging and saving chunks
                bluemap_stop()

                # Merge worlds and capture a list of merged chunks.
                # Each tuple is (effective_dimension, chunk_x, chunk_z)
                merged_chunks = merge_amulet_worlds(uploaded_world, local_world)
                logger.debug(f"Merged uploaded chunks from {zip_path}")

                # Save the local world after merging
                local_world.save()
                logger.info(f"Saved changes to {LOCAL_WORLD_DIR}")
            finally:
                local_world.close()
                uploaded_world.close()

            logger.info(f"Closed world handles for {zip_path}")

            # Import the dimension mapping from config
            from app.config import DIMENSION_TO_WORLD_PATH
            # Recalculate lighting for each merged chunk.
            # The cleanlight command takes the chunk coordinates, a radius, and the proper world folder.
            for (dim, cx, cz) in merged_chunks:
                mapped_world = DIMENSION_TO_WORLD_PATH.get(dim, "world")
                cleanlight_at(cx, cz, 1, mapped_world)

            # Re-enable BlueMap after lighting recalculations
            bluemap_start()
