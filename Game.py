import time

from Dungeon import Dungeon
from Player import Player
from Room import Room
from Server import Server

"""The game! This is where everything runs.

Creating it runs it

Attributes:
    dungeon: The dungeon the game takes place in!
    player: The local player; this will change when this game is translated to a MUD.
"""


class Game:
    def __init__(self):
        # Create the server interface
        self.server = Server()

        # Create the dungeon
        self.dungeon = Dungeon()

        # Create the player
        self.player = Player(self.dungeon.rooms[self.dungeon.entry_room])

        # Run the game loop
        self.game_loop()

    def game_loop(self):
        while True:
            # Update the game
            self.dungeon.update()
            self.player.update()

            time.sleep(0.1)
