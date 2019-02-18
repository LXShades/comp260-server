import time
import threading

from Dungeon import Dungeon
from Player import Player
from Room import Room
from Server import Server
from Client import Client

"""The game! This is where everything runs.

Creating it runs it

Attributes:
    dungeon: The dungeon the game takes place in!
    player: The local player; this will change when this game is translated to a MUD.
"""


class Game:
    def __init__(self):
        # Create the dungeon
        self.dungeon = Dungeon()

        # Create the server interface
        self.server = Server(self.dungeon)

        # Create a client for the local test player (temp). Comment this out when a player-less server is desired
        self.local_client = None
        threading.Thread(target=self.create_local_client, daemon=True).start()

        # Run the game loop
        self.game_loop()

    def game_loop(self):
        while True:
            # Update the game
            self.dungeon.update()

            time.sleep(0.1)

    def create_local_client(self):
        self.local_client = Client()
