from Player import Player
"""
A room is an area of the game in which player actions can take place.

Instance attributes:
    x: the X (west to east) coordinate of the room
    y: the Y (north to south coordinate of the room)
"""


class Room:
    def __init__(self, x: int, y: int, description: str, connections: list):
        self.x = x
        self.y = y
        self.description = description
        self.connections = connections

    """
    Called whenever a player enters the room
    """
    def on_enter(self, player: Player):
        # Display the room description to the player
        player.output(self.description)

    def try_go(self, direction: str):
        # Figure out which coordinates to move to
        destination_name = ""

        if direction == "north":
            destination_name = "%d,%d" % (self.x, self.y - 1)
        elif direction == "east":
            destination_name = "%d,%d" % (self.x + 1, self.y)
        elif direction == "south":
            destination_name = "%d,%d" % (self.x, self.y + 1)
        elif direction == "west":
            destination_name = "%d,%d" % (self.x - 1, self.y)

        # Can we go there?
        if destination_name in self.connections and destination_name in self.dungeon.rooms:
            return self.dungeon.rooms[destination_name]
        else:
            return None
