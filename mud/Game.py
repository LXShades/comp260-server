import time
import threading

from Dungeon import Dungeon
from Player import Player
from Room import Room
from Server import Server
from Global import Global
from Database import Database

"""The game! This is where everything runs.

Creating it runs it

Attributes:
    dungeon: The dungeon the game takes place in!
    player: The local player; this will change when this game is translated to a MUD.
    do_shutdown: If there is a local client for testing, closing the local client will close the server for convenience.
"""


class Game:
    def __init__(self):
        print("Starting server...")

        # Init vars
        Global.is_server = True  # Used for local client spawning

        # Initialise the database system
        Database.startup()

        # Create the dungeon
        self.dungeon = Dungeon()

        # Create the server interface
        self.server = Server(self.dungeon)

        # Create a client for the local player (for testing).
        self.do_shutdown = False
        self.create_local_client()  # Comment this out unless a test client is desired

        # Run the game loop
        self.game_loop()

        # Shut down the database
        Database.shutdown()

    """The main game loop. This updates the dungeons and all player events"""
    def game_loop(self):
        while not self.do_shutdown:
            # Update the game
            self.dungeon.update()

            time.sleep(0.1)

        self.dungeon.destroy()

    """Creates the local client for testing"""
    def create_local_client(self):
        # Start the client thread
        threading.Thread(target=self.local_client_thread, daemon=True).start()

    """Local client thread for testing"""
    def local_client_thread(self):
        # Create a local client!
        from ClientApp import ClientApp
        ClientApp()

        # Client has closed, shutdown
        self.do_shutdown = True
