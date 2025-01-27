"""
app/config.py

Holds global configuration data, constants, and environment variable setup.
"""

import os

# Directory for logging
LOG_DIR = 'logs'
LOG_FILE = 'latest.log'

# Data file for storing waypoints
DATA_FILE = 'waypoints.json'

# Distance threshold for deciding if a warp has moved enough
DISTANCE_THRESHOLD = 5  # blocks

# Default dimension
DEFAULT_DIMENSION = 'minecraft:overworld'

# Mapping from dimension ID => the .conf file in BlueMap's 'maps' folder
DIMENSION_TO_BLUEMAP_CONF = {
    'minecraft:overworld': 'world.conf',
    'minecraft:the_nether': 'dim-1.conf',       # or 'DIM-1.conf', depending on your environment
    'minecraft:the_end': 'dim1.conf',
    'pixelmon:ultra_space': 'ultra_space.conf'
}

# The path to the folder that holds your BlueMap .conf files for each dimension
BLUEMAP_MAPS_PATH = "/Users/matthewvogt/PycharmProjects/WorldSync/server/plugins/BlueMap/maps"

# The name of the marker-set we manage for warps
WARP_MARKER_SET_ID = "warp"

# RCON Configuration (from environment) - kept so we can do '/bluemap reload'
RCON_HOST = os.getenv('RCON_HOST', '127.0.0.1')
RCON_PORT = int(os.getenv('RCON_PORT', 25575))
RCON_PASSWORD = os.getenv('RCON_PASSWORD', 'default_password')

# API Key from environment
API_KEY = os.getenv('API_KEY', 'your-default-api-key')

# Local server world directory for Amulet merges
LOCAL_WORLD_DIR = "local_world"
