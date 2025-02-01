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

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Rest of your existing configuration
DISTANCE_THRESHOLD = int(os.getenv("DISTANCE_THRESHOLD", "5"))
DEFAULT_DIMENSION = os.getenv("DEFAULT_DIMENSION", "minecraft:overworld")
DIMENSION_TO_BLUEMAP_CONF = {
    'minecraft:overworld': os.getenv("BLUEMAP_CONF_OVERWORLD", "world.conf"),
    'minecraft:the_nether': os.getenv("BLUEMAP_CONF_NETHER", "dim-1.conf"),
    'minecraft:the_end': os.getenv("BLUEMAP_CONF_END", "dim1.conf"),
    'pixelmon:ultra_space': os.getenv("BLUEMAP_CONF_ULTRASPACE", "ultra_space.conf")
}
BLUEMAP_MAPS_PATH = os.getenv(
    "BLUEMAP_MAPS_PATH",
    "/Users/matthewvogt/PycharmProjects/WorldSync/server/plugins/BlueMap/maps"
)
WARP_MARKER_SET_ID = os.getenv("WARP_MARKER_SET_ID", "warp")
RCON_HOST = os.getenv("RCON_HOST", "127.0.0.1")
RCON_PORT = int(os.getenv("RCON_PORT", "25575"))
RCON_PASSWORD = os.getenv("RCON_PASSWORD", "default_password")
API_KEY = os.getenv("API_KEY", "your-default-api-key")
LOCAL_WORLD_DIR = os.getenv("LOCAL_WORLD_DIR", "local_world")
DATA_FILE = os.getenv("DATA_FILE", "waypoints.json")

# New mapping for dimension world folders used in lighting updates.
# These map the dimension IDs to the actual world folder paths used in the cleanlight command.
DIMENSION_TO_WORLD_PATH = {
    "minecraft:overworld": os.getenv("DIMENSION_WORLD_OVERWORLD", "world"),
    "minecraft:the_nether": os.getenv("DIMENSION_WORLD_NETHER", "world/DIM-1"),
    "minecraft:the_end": os.getenv("DIMENSION_WORLD_END", "world/DIM1"),
    "pixelmon:ultra_space": os.getenv("DIMENSION_WORLD_ULTRASPACE", "world/dimensions/pixelmon/ultra_space")
}
