# app/config.py

import os
from dotenv import load_dotenv

# Load .env if present
load_dotenv()

# Directory for logging
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_FILE = os.getenv("LOG_FILE", "latest.log")

# Data file for storing waypoints
DATA_FILE = os.getenv("DATA_FILE", "waypoints.json")

# Distance threshold for deciding if a warp has moved enough
DISTANCE_THRESHOLD = int(os.getenv("DISTANCE_THRESHOLD", "5"))  # default 5 blocks

# Default dimension
DEFAULT_DIMENSION = os.getenv("DEFAULT_DIMENSION", "minecraft:overworld")

# Mapping from dimension ID => the .conf file in BlueMap's 'maps' folder
DIMENSION_TO_BLUEMAP_CONF = {
    'minecraft:overworld': os.getenv("BLUEMAP_CONF_OVERWORLD", "world.conf"),
    'minecraft:the_nether': os.getenv("BLUEMAP_CONF_NETHER", "dim-1.conf"),
    'minecraft:the_end': os.getenv("BLUEMAP_CONF_END", "dim1.conf"),
    'pixelmon:ultra_space': os.getenv("BLUEMAP_CONF_ULTRA_SPACE", "ultra_space.conf")
}

# The path to the folder that holds your BlueMap .conf files for each dimension
BLUEMAP_MAPS_PATH = os.getenv(
    "BLUEMAP_MAPS_PATH",
    "/Users/matthewvogt/PycharmProjects/WorldSync/server/plugins/BlueMap/maps"
)

# The name of the marker-set we manage for warps
WARP_MARKER_SET_ID = os.getenv("WARP_MARKER_SET_ID", "warp")

# RCON Configuration
RCON_HOST = os.getenv("RCON_HOST", "127.0.0.1")
RCON_PORT = int(os.getenv("RCON_PORT", "25575"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD", "default_password")

# API Key from environment
API_KEY = os.getenv("API_KEY", "your-default-api-key")

# Local server world directory for Amulet merges
LOCAL_WORLD_DIR = os.getenv("LOCAL_WORLD_DIR", "local_world")
