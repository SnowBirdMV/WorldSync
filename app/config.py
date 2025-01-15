"""
app/config.py

Holds global configuration data, constants, and environment variable setup.
"""

import os

# Directory for logging
LOG_DIR = 'logs'
LOG_FILE = 'warp_server.log'

# Data file for storing waypoints
DATA_FILE = 'waypoints.json'

# Distance threshold for deciding if a warp has moved enough
DISTANCE_THRESHOLD = 5  # blocks

# Default dimension
DEFAULT_DIMENSION = 'minecraft:overworld'

# Mapping internal dimension ID to Dynmap 'world' names
DIMENSION_TO_WORLD = {
    'minecraft:overworld': 'world',
    'minecraft:the_nether': 'DIM-1',
    'minecraft:the_end': 'DIM1',
    'pixelmon:ultra_space': 'pixelmon_ultra_space'
}

# RCON Configuration (from environment)
RCON_HOST = os.getenv('RCON_HOST', '127.0.0.1')
RCON_PORT = int(os.getenv('RCON_PORT', 25575))
RCON_PASSWORD = os.getenv('RCON_PASSWORD', 'default_password')

# API Key from environment
API_KEY = os.getenv('API_KEY', 'your-default-api-key')

# Local server world directory for Amulet merges
LOCAL_WORLD_DIR = "local_world"

# We'll reuse the same RCON config for Dynmap
DYNMAP_RCON_HOST = RCON_HOST
DYNMAP_RCON_PORT = RCON_PORT
DYNMAP_RCON_PASSWORD = RCON_PASSWORD

# For each dimension, define which Dynmap maps to render
DIMENSION_TO_MAPS = {
    'minecraft:overworld': ['flat', 'surface'],
    'minecraft:the_nether': ['flat'],
    'minecraft:the_end': ['flat'],
    'pixelmon:ultra_space': ['flat']
}
