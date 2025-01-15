"""
app/utils/dynmap.py

Contains utility functions for instructing Dynmap to perform chunk-by-chunk radius renders,
and polling until no render jobs are active.
"""

import time
import logging
from collections import defaultdict

from app.config import (
    DIMENSION_TO_WORLD,
    DIMENSION_TO_MAPS,
    DYNMAP_RCON_HOST,
    DYNMAP_RCON_PORT,
    DYNMAP_RCON_PASSWORD
)
from app.utils.rcon_helper import rcon_client


def chunk_by_chunk_dynmap(chunks_list):
    """
    For each updated chunk, we run a small radius render (like 8 blocks),
    for each map in that dimension, then wait until Dynmap has no active job.
    Then proceed to next chunk.
    """
    dimension_chunks = defaultdict(list)
    for (dimension, cx, cz) in chunks_list:
        dimension_chunks[dimension].append((cx, cz))

    with rcon_client(DYNMAP_RCON_HOST, DYNMAP_RCON_PORT, DYNMAP_RCON_PASSWORD) as client:
        for dimension, coords in dimension_chunks.items():
            if dimension not in DIMENSION_TO_WORLD:
                logging.warning(f"No Dynmap world found for dimension '{dimension}'. Skipping.")
                continue

            dynmap_world = DIMENSION_TO_WORLD[dimension]
            maps_for_dimension = DIMENSION_TO_MAPS.get(dimension, [])
            if not maps_for_dimension:
                logging.warning(f"No maps defined for dimension '{dimension}'. Skipping.")
                continue

            for (cx, cz) in coords:
                block_x = cx << 4
                block_z = cz << 4
                radius = 8  # small radius for a single chunk

                for map_name in maps_for_dimension:
                    cmd = (
                        f"dynmap radiusrender {dynmap_world} "
                        f"{block_x} {block_z} {radius}"
                    )
                    response = client.run(cmd)
                    logging.debug(
                        f"[chunk_by_chunk_dynmap] dimension={dimension}, "
                        f"map={map_name}, chunk=({cx},{cz}), block=({block_x},{block_z}), "
                        f"radius={radius} -> {response}"
                    )
                    # After issuing this chunk's render, wait for no active jobs
                    wait_for_dynmap_no_active_jobs(client)


def wait_for_dynmap_no_active_jobs(client):
    """
    Poll /dynmap stats until there's no 'Active render jobs:' line that contains dimension names.
    If the substring after 'Active render jobs:' is empty or starts with 'Chunk Loading Statistics:',
    we assume no jobs are active.
    """
    while True:
        resp = client.run("dynmap stats")
        idx = resp.find("Active render jobs:")
        if idx == -1:
            # Means we didn't find that line, likely no jobs
            break

        after_str = resp[idx + len("Active render jobs:"):].strip()
        # If it's empty or just 'Chunk Loading Statistics:' => no actual job
        if not after_str or after_str.startswith("Chunk Loading Statistics:"):
            # No active dimension listed => done
            break

        # Otherwise, there's something like "world" or "DIM1" => still rendering
        logging.debug(f"Dynmap still rendering. 'Active render jobs:' => {after_str}")
        time.sleep(5)
