"""
app/utils/rcon_helper.py

Provides a context manager for interacting with the server via RCON,
plus a function to reload BlueMap after we update our .conf files.
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
            response = client.run("bluemap reload")
            logging.info(f"Executed bluemap reload -> Response: {response}")
    except Exception as e:
        logging.error(f"Failed to reload BlueMap via RCON: {e}", exc_info=True)
