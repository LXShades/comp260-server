import time
import threading

from Dungeon import Dungeon
from Player import Player
from Room import Room
from Server import Server
from Global import Global

"""The game! This is where everything runs.

Creating it runs it

Attributes:
    dungeon: The dungeon the game takes place in!
    player: The local player; this will change when this game is translated to a MUD.
"""


class Game:
    def __init__(self):
        # Init vars
        self.is_local_client_closing = False
        Global.is_server = True  # Used for client spawning

        # Create the dungeon
        self.dungeon = Dungeon()

        # Create the server interface
        self.server = Server(self.dungeon)

        # Create a client for the local test player (temp). Comment this out when a player-less server is desired
        self.start_local_client()

        # Run the game loop
        self.game_loop()

    def game_loop(self):
        while not self.is_local_client_closing:
            # Update the game
            self.dungeon.update()

            time.sleep(0.1)

    def start_local_client(self):
        # Start the client thread
        threading.Thread(target=self.create_local_client, daemon=True).start()

    def create_local_client(self):
        # Create a local client!
        from Client import Client
        Client()

        # Client has closed, shutdown
        self.is_local_client_closing = True
