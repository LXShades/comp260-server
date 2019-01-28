from Dungeon import Dungeon
from Player import Player
from Room import Room

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

        # Create the player
        self.player = Player(self.dungeon.rooms["0,0"])

        # Run the game loop
        self.game_loop()

    def game_loop(self):
        while 1:
            user_input: str = input("Enter a command")

            parameters: list = user_input.lower().split(" ")
            command: str = parameters[0]

            # Go to another room
            if command == "go":
                self.player.go(parameters[1])
