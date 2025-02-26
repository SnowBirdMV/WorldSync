# app/routes/waypoints.py
import os
import json
import logging
from math import sqrt
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from app.schemas.warp_schema import WarpSchema
from app.config import (
    DATA_FILE,
    DISTANCE_THRESHOLD,
    DEFAULT_DIMENSION
)
from app.routes.auth import require_api_key
from app.utils.bluemap_helper import sync_waypoints_bluemap

waypoints_bp = Blueprint('waypoints', __name__)

# Load existing waypoints (existing code remains the same)
if os.path.exists(DATA_FILE):
    with open(DATA_FILE, 'r') as f:
        waypoints = json.load(f)
    updated = False
    for wp in waypoints:
        if 'dimension' not in wp:
            wp['dimension'] = DEFAULT_DIMENSION
            updated = True
    if updated:
        with open(DATA_FILE, 'w') as f:
            json.dump(waypoints, f, indent=4)
else:
    waypoints = []

def save_waypoints():
    with open(DATA_FILE, 'w') as f:
        json.dump(waypoints, f, indent=4)

def is_far_enough(new_wp, existing_wp):
    """Existing implementation remains the same"""
    if new_wp['dimension'] != existing_wp['dimension']:
        return True
    distance = sqrt(
        (new_wp['x'] - existing_wp['x']) ** 2 +
        (new_wp['y'] - existing_wp['y']) ** 2 +
        (new_wp['z'] - existing_wp['z']) ** 2
    )
    return distance > DISTANCE_THRESHOLD

warp_schema = WarpSchema()

@waypoints_bp.route('/waypoints', methods=['POST'])
@require_api_key
def receive_waypoints():
    """Updated endpoint with force-refresh support"""
    global waypoints
    data = request.get_json()

    # Get force-refresh parameter from query string
    force_refresh = request.args.get('force-refresh', 'false').lower() == 'true'

    if not data or not isinstance(data, list):
        return jsonify({'error': 'Expected a JSON list of warps'}), 400

    updated_count = 0
    added_count = 0
    changes_detected = False

    for warp_data in data:
        try:
            warp = warp_schema.load(warp_data)
        except ValidationError as err:
            logging.warning(f"Invalid warp data: {warp_data}, Errors: {err.messages}")
            continue

        warp_name = warp['name']
        x = warp['x']
        y = warp['y']
        z = warp['z']
        dimension = warp['dimension']

        # Existing validation checks remain the same
        MIN_COORD = -30000000
        MAX_COORD = 30000000
        MIN_Y = 0
        MAX_Y = 256
        if not (MIN_COORD <= x <= MAX_COORD and MIN_COORD <= z <= MAX_COORD and MIN_Y <= y <= MAX_Y):
            logging.warning(f"Invalid coords for warp '{warp_name}': x={x},y={y},z={z}")
            continue

        existing_warp = next(
            (wp for wp in waypoints
             if wp['name'].lower() == warp_name.lower() and wp.get('dimension', DEFAULT_DIMENSION) == dimension),
            None
        )

        if existing_warp:
            if is_far_enough({'x': x, 'y': y, 'z': z, 'dimension': dimension}, existing_warp):
                existing_warp.update({'x': x, 'y': y, 'z': z})
                updated_count += 1
                changes_detected = True
            else:
                logging.info(f"Warp '{warp_name}' not updated. Distance <= {DISTANCE_THRESHOLD}.")
        else:
            waypoints.append({
                'name': warp_name,
                'x': x,
                'y': y,
                'z': z,
                'dimension': dimension
            })
            added_count += 1
            changes_detected = True

    # Save if changes detected or forced refresh
    if changes_detected or force_refresh:
        if changes_detected:
            save_waypoints()
            logging.info(f"Saving {len(waypoints)} waypoints to disk")

        logging.info(f"Syncing waypoints to BlueMap (force={force_refresh})")
        sync_waypoints_bluemap(waypoints)

    message = f"Processed {len(data)} warps. Updated: {updated_count}, Added: {added_count}"
    if force_refresh:
        message += " | Forced BlueMap refresh"

    logging.info(message)
    return jsonify({'message': message}), 200

@waypoints_bp.route('/waypoints', methods=['GET'])
def get_waypoints_api():
    """Existing implementation remains the same"""
    return jsonify(waypoints), 200
