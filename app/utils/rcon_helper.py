"""
app/utils/rcon_helper.py

Provides functions for interacting with the server via RCON,
including a context manager and the Dynmap sync logic.
"""

import logging
from rcon import Client

from app.config import (
    RCON_HOST,
    RCON_PORT,
    RCON_PASSWORD,
    DIMENSION_TO_WORLD
)


def rcon_client(host, port, password):
    """
    A context manager for establishing an RCON client connection,
    closing it automatically after use.
    """
    return Client(host=host, port=port, passwd=password)


def parse_dmarker_list(output):
    """
    Parses the output from `/dmarker list set:warps` into a dictionary of markers.
    Example line:
      NEW: label:"NEW WARP", set:warps, world:world, x:79.0, y:78.0, z:16.0, icon:portal, markup:false
    """
    markers = {}
    lines = output.strip().split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        if ': ' not in line:
            logging.warning(f"Skipping malformed line: {line}")
            continue
        marker_id, properties = line.split(': ', 1)
        parts = properties.split(', ')
        marker = {}
        for part in parts:
            if ':' not in part:
                continue
            key, value = part.split(':', 1)
            value = value.strip()
            # strip quotes if present
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            marker[key.lower()] = value
        if marker_id:
            markers[marker_id] = marker
    logging.debug(f"Parsed Markers: {markers}")
    return markers


def sync_waypoints(waypoints):
    """
    Synchronizes local waypoints to Dynmap via RCON (using the 'warps' marker set).
    """
    try:
        with rcon_client(RCON_HOST, RCON_PORT, RCON_PASSWORD) as client:
            logging.info("RCON connection established for waypoint sync.")

            # 1) Fetch existing markers from Dynmap
            dmarker_list_command = 'dmarker list set:warps'
            response = client.run(dmarker_list_command)
            logging.debug(f"RCON Response for '{dmarker_list_command}':\n{response}")

            current_markers = parse_dmarker_list(response)
            logging.info(f"Fetched {len(current_markers)} markers from Dynmap (set=warps).")

            # 2) Build desired markers from local `waypoints`
            desired_markers = {}
            for wp in waypoints:
                marker_id = wp['name']
                desired_markers[marker_id] = wp

            # 3) Determine add/delete/move
            markers_to_add = []
            markers_to_delete = []
            markers_to_move = []

            for marker_id, wp in desired_markers.items():
                if marker_id not in current_markers:
                    # Need to add
                    markers_to_add.append(wp)
                else:
                    current_wp = current_markers[marker_id]
                    # Compare coords & dimension
                    need_move = (
                        float(current_wp.get('x', 0)) != wp['x'] or
                        float(current_wp.get('y', 0)) != wp['y'] or
                        float(current_wp.get('z', 0)) != wp['z'] or
                        DIMENSION_TO_WORLD.get(wp['dimension']) != current_wp.get('world')
                    )
                    if need_move:
                        markers_to_move.append(wp)

            for marker_id in current_markers:
                if marker_id not in desired_markers:
                    markers_to_delete.append(marker_id)

            logging.info(f"Markers to add: {markers_to_add}")
            logging.info(f"Markers to move: {markers_to_move}")
            logging.info(f"Markers to delete: {markers_to_delete}")

            # 4) Delete
            for marker_id in markers_to_delete:
                delete_cmd = f'dmarker delete set:warps id:{marker_id}'
                resp = client.run(delete_cmd)
                logging.debug(f"Delete {marker_id} -> {resp}")

            # 5) Move (delete + add)
            for wp in markers_to_move:
                marker_id = wp['name']
                delete_cmd = f'dmarker delete set:warps id:{marker_id}'
                add_cmd = (
                    f'dmarker add id:{marker_id} "{wp["name"]}" icon:portal '
                    f'set:warps x:{wp["x"]} y:{wp["y"]} z:{wp["z"]} '
                    f'world:{DIMENSION_TO_WORLD.get(wp["dimension"])}'
                )
                del_resp = client.run(delete_cmd)
                logging.debug(f"Move-Delete {marker_id} -> {del_resp}")
                add_resp = client.run(add_cmd)
                logging.debug(f"Move-Add {marker_id} -> {add_resp}")

            # 6) Add
            for wp in markers_to_add:
                marker_id = wp['name']
                add_cmd = (
                    f'dmarker add id:{marker_id} "{wp["name"]}" icon:portal '
                    f'set:warps x:{wp["x"]} y:{wp["y"]} z:{wp["z"]} '
                    f'world:{DIMENSION_TO_WORLD.get(wp["dimension"])}'
                )
                add_resp = client.run(add_cmd)
                logging.debug(f"Add {marker_id} -> {add_resp}")

            logging.info("Waypoint synchronization complete.")

    except Exception as e:
        logging.error(f"An error occurred during waypoint sync: {e}", exc_info=True)
