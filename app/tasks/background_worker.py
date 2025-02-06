# app/tasks/background_worker.py
import queue
import os
import tempfile
import zipfile
import logging
import subprocess
import re
from threading import Lock
from filelock import FileLock
import amulet
from amulet.api.errors import ChunkLoadError, ChunkDoesNotExist
from app.utils.amulet_merge import merge_amulet_worlds
from app.config import LOCAL_WORLD_DIR, DIMENSION_TO_WORLD_PATH

logger = logging.getLogger(__name__)
logger.propagate = True  # Ensure we use root logger handlers

# Queue for processing incoming ZIP files
process_queue = queue.Queue()
lock = Lock()

# Global status for the current job (used for reporting progress)
job_status = {
    "current_job": None,     # Full path of the ZIP file being processed
    "stage": None,           # "amulet merge" or "bluemap render"
    "total_chunks": 0,       # Total number of non-empty chunks that will be changed (calculated once at the start)
    "current_chunk": 0,      # Count of merged chunks processed so far
    "render_progress": None, # Latest render progress from BlueMap (if in render stage)
}

# Global lock file path for cross-process safety
WORLD_LOCK_PATH = os.path.join(LOCAL_WORLD_DIR, ".world_lock.lock")


def get_current_job():
    global job_status
    return job_status if job_status["current_job"] is not None else None


def get_pending_jobs():
    with lock:
        return list(process_queue.queue)


def background_worker():
    global job_status
    while True:
        zip_path = process_queue.get()
        if zip_path is None:
            break

        try:
            # Set up the current job status
            job_status["current_job"] = zip_path
            job_status["stage"] = "amulet merge"
            job_status["total_chunks"] = 0
            job_status["current_chunk"] = 0
            job_status["render_progress"] = None

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
            # Reset job status after finishing
            job_status["current_job"] = None
            job_status["stage"] = None
            job_status["total_chunks"] = 0
            job_status["current_chunk"] = 0
            job_status["render_progress"] = None
            process_queue.task_done()


def process_zip(zip_path):
    from app.utils.rcon_helper import bluemap_stop

    # Create cross-process file lock; wait indefinitely for the lock
    world_lock = FileLock(WORLD_LOCK_PATH, timeout=-1)
    with world_lock:
        with tempfile.TemporaryDirectory() as tmpdir:
            extracted_dir = os.path.join(tmpdir, "extracted_world")
            with zipfile.ZipFile(zip_path, 'r') as zf:
                zf.extractall(extracted_dir)

            logger.debug(f"Extracted {zip_path} into {extracted_dir}")

            # Load the uploaded and local worlds
            uploaded_world = amulet.load_level(extracted_dir)
            local_world = amulet.load_level(LOCAL_WORLD_DIR)

            try:
                # Stop BlueMap via RCON before starting the merge
                bluemap_stop()

                # Calculate total number of non-empty chunks that will be merged at the start.
                from app.utils.amulet_merge import is_chunk_empty
                total_to_merge = 0
                for dimension in uploaded_world.dimensions:
                    coords = list(uploaded_world.all_chunk_coords(dimension))
                    for (cx, cz) in coords:
                        try:
                            chunk = uploaded_world.get_chunk(cx, cz, dimension)
                        except (ChunkLoadError, ChunkDoesNotExist):
                            continue
                        if not is_chunk_empty(chunk):
                            total_to_merge += 1
                job_status["total_chunks"] = total_to_merge
                logger.info(f"Total chunks to merge: {job_status['total_chunks']}")

                # Define a callback to update merge progress from Amulet merging
                def update_merge_progress(merged_count):
                    job_status["current_chunk"] = merged_count

                # Merge worlds; progress is updated during the merge process
                merged_chunks = merge_amulet_worlds(
                    uploaded_world, local_world, progress_callback=update_merge_progress
                )
                logger.debug(f"Merged {job_status['current_chunk']} uploaded chunks from {zip_path}")

                # Save the merged local world
                local_world.save()
                logger.info(f"Saved changes to {LOCAL_WORLD_DIR}")
            finally:
                local_world.close()
                uploaded_world.close()

            logger.info(f"Closed world handles for {zip_path}")

            # Recalculate lighting for each merged chunk (this stage does not update progress counters)
            for (dim, cx, cz) in merged_chunks:
                mapped_world = DIMENSION_TO_WORLD_PATH.get(dim, "world")
                from app.utils.rcon_helper import cleanlight_at
                cleanlight_at(cx, cz, 1, mapped_world)

            # Switch stage to BlueMap rendering and initialize render progress
            job_status["stage"] = "bluemap render"
            job_status["render_progress"] = None
            run_bluemap_render()


def run_bluemap_render():
    """
    Starts the BlueMap jar process and reads its output line‐by‐line.
    It parses lines matching progress updates (e.g.:
      Update map 'world': 0.301% (ETA: 8:38:20)
    ) and stores this information in job_status["render_progress"].
    When a line containing "Your maps are now all up-to-date!" is detected,
    the process is terminated.
    """
    from app.config import (
        BLUEMAP_JAR,
        BLUEMAP_CONFIG_LOCATION,
        MC_VERSION,
        BLUEMAP_MODS,
        DIMENSION_TO_BLUEMAP_CONF,
        JAVA_PATH,
        BLUEMAP_WORKING_DIR,
    )

    # Compute the --maps argument by stripping the '.conf' extension from each config filename
    maps_list = [conf.replace(".conf", "") for conf in DIMENSION_TO_BLUEMAP_CONF.values()]
    maps_arg = ",".join(maps_list)

    cmd = [
        JAVA_PATH, "-jar", BLUEMAP_JAR,
        "--config", BLUEMAP_CONFIG_LOCATION,
        "--watch",
        "--mc-version", MC_VERSION,
        "--mods", BLUEMAP_MODS,
        "--maps", maps_arg,
        "--render"
    ]

    logger.info(f"Starting BlueMap render process with command: {' '.join(cmd)}")
    process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        cwd=BLUEMAP_WORKING_DIR  # Set the working directory here
    )

    # Regular expression to capture render progress lines
    progress_pattern = re.compile(r"Update map '(.+?)':\s+([\d\.]+)%\s+\(ETA:\s+([^)]+)\)")
    try:
        while True:
            line = process.stdout.readline()
            if not line:
                break
            logger.info(f"BlueMap: {line.strip()}")

            # Check for progress update
            match = progress_pattern.search(line)
            if match:
                job_status["render_progress"] = {
                    "map": match.group(1),
                    "percent": float(match.group(2)),
                    "eta": match.group(3)
                }
            if "Your maps are now all up-to-date!" in line:
                logger.info("BlueMap render complete signal received.")
                break

        # Terminate the BlueMap process once rendering is complete
        process.terminate()
        process.wait(timeout=10)
        logger.info("BlueMap render process terminated.")
    except Exception as e:
        logger.error(f"Error during BlueMap render: {e}", exc_info=True)
        process.kill()
    finally:
        if process.poll() is None:
            process.kill()
