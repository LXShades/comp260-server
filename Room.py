from Player import Player
"""
A room is an area of the game in which player actions can take place.

Instance attributes:
    x: the X (west to east) coordinate of the room
    y: the Y (north to south coordinate of the room)
"""


class Room:
    def __init__(self, title: str, description: str, connections: dict, items: list=[]):
        self.title = title
        self.description = description
        self.connections = connections
        self.items = items

    """
    Called whenever a player enters the room
    """
    def on_enter(self, player: Player):
        # Display the room description to the player
        player.output(self.description)

        # Display item-specific entry descriptions to the player
        for item in self.items:
            player.output(item.entry_description)

        # Call item entry callbacks
        for item in self.items:
            item.on_player_enter(player)

    def try_go(self, direction: str):
        if direction in self.connections and self.connections[direction] in self.dungeon.rooms:
            # Return the room at this target
            return self.dungeon.rooms[self.connections[direction]]
        else:
            # We can't go there!
            return None

    def update(self):
        pass