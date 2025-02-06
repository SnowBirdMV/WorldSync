# app/config.py
import os
from dotenv import load_dotenv

load_dotenv()

# Logging Configuration
LOG_DIR = os.getenv("LOG_DIR", "logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
GUNICORN_ACCESS_LOG = os.getenv("GUNICORN_ACCESS_LOG", "gunicorn_access.log")
GUNICORN_ERROR_LOG = os.getenv("GUNICORN_ERROR_LOG", "gunicorn_error.log")
APP_LOG = os.getenv("APP_LOG", "application.log")
MAX_LOG_BYTES = int(os.getenv("MAX_LOG_BYTES", "10485760"))
LOG_BACKUP_COUNT = int(os.getenv("LOG_BACKUP_COUNT", "5"))

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Data file configuration
DATA_FILE = os.getenv("DATA_FILE", "waypoints.json")

# Warp movement threshold
DISTANCE_THRESHOLD = int(os.getenv("DISTANCE_THRESHOLD", "5"))

# Default dimension setting
DEFAULT_DIMENSION = os.getenv("DEFAULT_DIMENSION", "minecraft:overworld")

# BlueMap configuration files mapping
DIMENSION_TO_BLUEMAP_CONF = {
    'minecraft:overworld': os.getenv("BLUEMAP_CONF_OVERWORLD", "world.conf"),
    'minecraft:the_nether': os.getenv("BLUEMAP_CONF_NETHER", "dim-1.conf"),
    'minecraft:the_end': os.getenv("BLUEMAP_CONF_END", "dim1.conf"),
    'pixelmon:ultra_space': os.getenv("BLUEMAP_CONF_ULTRA_SPACE", "ultra_space.conf")
}

# BlueMap maps path
BLUEMAP_MAPS_PATH = os.getenv(
    "BLUEMAP_MAPS_PATH",
    "/home/mcserver/BlueMap/config/maps"
)

# Warp marker set ID
WARP_MARKER_SET_ID = os.getenv("WARP_MARKER_SET_ID", "warp")

# RCON server configuration
RCON_HOST = os.getenv("RCON_HOST", "127.0.0.1")
RCON_PORT = int(os.getenv("RCON_PORT", "25575"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD", "default_password")

# API configuration
API_KEY = os.getenv("API_KEY", "your-default-api-key")

# Local server world directory for Amulet merges
LOCAL_WORLD_DIR = os.getenv("LOCAL_WORLD_DIR", "local_world")

# New BlueMap Jar configuration
BLUEMAP_JAR = os.getenv("BLUEMAP_JAR", "/home/mcserver/BlueMap/bluemap-5.5-cli.jar")
BLUEMAP_CONFIG_LOCATION = os.getenv("BLUEMAP_CONFIG_LOCATION", "/home/mcserver/BlueMap/config")
MC_VERSION = os.getenv("MC_VERSION", "1.20.2")
BLUEMAP_MODS = os.getenv("BLUEMAP_MODS", "/home/mcserver/BlueMap/mods")

# Configurable Java path (defaults to "java" if not set)
JAVA_PATH = os.getenv("JAVA_PATH", "java")

# BlueMap working directory (where BlueMap will render and output files)
BLUEMAP_WORKING_DIR = os.getenv("BLUEMAP_WORKING_DIR", "/Users/matthewvogt/PycharmProjects/WorldSync/BlueMap")

# New mapping for dimension world folders used in lighting updates.
DIMENSION_TO_WORLD_PATH = {
    "minecraft:overworld": os.getenv("DIMENSION_WORLD_OVERWORLD", "world"),
    "minecraft:the_nether": os.getenv("DIMENSION_WORLD_NETHER", "world/DIM-1"),
    "minecraft:the_end": os.getenv("DIMENSION_WORLD_END", "world/DIM1"),
    "pixelmon:ultra_space": os.getenv("DIMENSION_WORLD_ULTRASPACE", "world/dimensions/pixelmon/ultra_space")
}
