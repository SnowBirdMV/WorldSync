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

def update_conf_with_waypoints(conf_lines, waypoints):
    """
    Given the lines of a .conf file, inject/update the "warp" marker-set’s "markers" block
    so that it exactly reflects the list of waypoints. (We do a naive text-based approach.)
    """
    # Build the string block for all warp markers
    warp_markers_str = build_warp_markers_block(waypoints)

    out = []
    in_marker_sets = False
    brace_level = 0
    warp_block_found = False
    skip_warp_block = False

    i = 0
    while i < len(conf_lines):
        line = conf_lines[i]

        # Detect marker-sets: {
        if not in_marker_sets:
            if "marker-sets:" in line:
                in_marker_sets = True
            out.append(line)
            i += 1
            continue

        # Once inside marker-sets, track braces to know when we exit
        brace_level += line.count('{')
        brace_level -= line.count('}')

        # If we left marker-sets (brace_level < 1), just append rest
        if brace_level < 1:
            # If we never found warp_block, insert it now
            if not warp_block_found:
                out.append(f"    {WARP_MARKER_SET_ID}: {{\n")
                out.append("        markers: {\n")
                out.append(warp_markers_str)
                out.append("        }\n    }\n")
            out.append(line)
            in_marker_sets = False
            i += 1
            continue

        # If we see the warp marker-set start, we'll skip lines until its closing brace
        if not warp_block_found and f"{WARP_MARKER_SET_ID}:" in line:
            warp_block_found = True
            skip_warp_block = True
            # Insert the warp set heading
            out.append(f"        {WARP_MARKER_SET_ID}: {{\n")
            i += 1
            continue

        # If skipping existing warp block lines, detect closing braces
        if skip_warp_block:
            brace_level_in_block = 0
            # In the line we are about to skip, if there's an opening brace, track it
            if '{' in line:
                brace_level_in_block += 1

            # Move forward to find the matching close
            while i < len(conf_lines):
                if '{' in conf_lines[i]:
                    brace_level_in_block += 1
                if '}' in conf_lines[i]:
                    brace_level_in_block -= 1
                i += 1
                if brace_level_in_block <= 0:
                    break

            # Insert our new warp block
            out.append("            markers: {\n")
            out.append(warp_markers_str)
            out.append("            }\n        }\n")
            skip_warp_block = False
            continue

        # Otherwise, just copy lines
        out.append(line)
        i += 1

    return out


def build_warp_markers_block(waypoints):
    """
    Builds the lines defining all warp-markers for the given list of waypoints
    as "html" markers.
    """
    lines = []
    for wp in waypoints:
        marker_id = wp['name']
        x = wp['x']
        y = wp['y']
        z = wp['z']
        label = wp['name']

        lines.append(f"                {marker_id}: {{")
        lines.append(f"                    type: \"html\"")
        lines.append(f"                    position: {{ x: {x}, y: {y}, z: {z} }}")
        lines.append(f"                    label: \"{label}\"")
        # For HTML content, you can add more advanced styling if desired:
        lines.append(f"                    html: \"<div style='color: white;'>{label}</div>\"")
        lines.append(f"                    anchor: {{ x: 0, y: 0 }}")
        lines.append(f"                    sorting: 0")
        lines.append(f"                    listed: true")
        lines.append(f"                    min-distance: 0")
        lines.append(f"                    max-distance: 10000000")
        lines.append(f"                }}")

    # Return as a single string with newlines
    return "\n".join(lines) + "\n"
