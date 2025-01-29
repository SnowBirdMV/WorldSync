# app/utils/bluemap_helper.py
import os
import logging
from app.config import (
    BLUEMAP_MAPS_PATH,
    DIMENSION_TO_BLUEMAP_CONF,
    WARP_MARKER_SET_ID
)
from app.utils.rcon_helper import bluemap_reload

logger = logging.getLogger(__name__)

def sync_waypoints_bluemap(all_waypoints):
    dimension_map = {}
    for wp in all_waypoints:
        dim = wp.get('dimension')
        dimension_map.setdefault(dim, []).append(wp)

    for dim, wps in dimension_map.items():
        conf_filename = DIMENSION_TO_BLUEMAP_CONF.get(dim)
        if not conf_filename:
            logger.warning(f"No BlueMap .conf for dimension '{dim}'")
            continue

        conf_path = os.path.join(BLUEMAP_MAPS_PATH, conf_filename)
        if not os.path.isfile(conf_path):
            logger.warning(f"Config not found: {conf_path}")
            continue

        with open(conf_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        updated_lines = update_conf_with_waypoints(lines, wps)

        with open(conf_path, 'w', encoding='utf-8') as f:
            f.writelines(updated_lines)

        logger.info(f"Synced {len(wps)} waypoints to {conf_filename}")

    bluemap_reload()

# Rest of the file remains the same as your original implementation
# (update_conf_with_waypoints and build_warp_markers_block functions)
