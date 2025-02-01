"""
app/utils/rcon_helper.py

Provides a context manager for interacting with the server via RCON,
plus functions to control BlueMap and to recalculate chunk lighting.
"""

import logging
from rcon import Client
from app.config import RCON_HOST, RCON_PORT, RCON_PASSWORD

def rcon_client():
    """
    A context manager for establishing an RCON client connection,
    closing it automatically after use.
    """
    return Client(host=RCON_HOST, port=RCON_PORT, passwd=RCON_PASSWORD)

def bluemap_reload():
    """
    Instructs the Minecraft server to reload BlueMap's configuration.
    This picks up any changes we've made to the marker .conf files.
    """
    try:
        with rcon_client() as client:
            response = client.run("bluemap reload light")
            logging.info(f"Executed bluemap reload -> Response: {response}")
    except Exception as e:
        logging.error(f"Failed to reload BlueMap via RCON: {e}", exc_info=True)

def bluemap_stop():
    """
    Disables BlueMap to prevent rendering issues during world merging.
    """
    try:
        with rcon_client() as client:
            response = client.run("bluemap stop")
            logging.info(f"Executed bluemap stop -> Response: {response}")
    except Exception as e:
        logging.error(f"Failed to stop BlueMap via RCON: {e}", exc_info=True)

def bluemap_start():
    """
    Re-enables BlueMap after world merging and lighting recalculations are complete.
    """
    try:
        with rcon_client() as client:
            response = client.run("bluemap start")
            logging.info(f"Executed bluemap start -> Response: {response}")
    except Exception as e:
        logging.error(f"Failed to start BlueMap via RCON: {e}", exc_info=True)

def cleanlight_at(chunk_x, chunk_z, chunk_radius, world):
    """
    Regenerates lighting for a specific chunk using the cleanlight command.
    Command syntax: /cleanlight at [chunk_x] [chunk_z] [chunk_radius] (world)
    """
    try:
        with rcon_client() as client:
            command = f"cleanlight at {chunk_x} {chunk_z} {chunk_radius} {world}"
            response = client.run(command)
            logging.info(f"Executed cleanlight command at ({chunk_x}, {chunk_z}) -> Response: {response}")
    except Exception as e:
        logging.error(f"Failed to execute cleanlight command for chunk ({chunk_x}, {chunk_z}): {e}", exc_info=True)
