import Room


"""A player in the game!

Attributes:
    room: current Room that the player is in
"""


class Player:
    """Creates the player in the given room

    Parameters:
        room: the room to spawn in
    """
    def __init__(self, room: Room):
        # Output an initial message to the player
        self.output("""You have entered the dungeon...
Type 'help' at any time to see your list of commands. Consider using the 'walk into' command to 'walk into the door'.
""")

        self.room = room
        self.room.on_enter(self)

    """Outputs a string to the player

    string: the string to output to the player
    Returns: nothing
    """
    def output(self, string: str):
        # Todo: Networking stuff later
        print(string)

    def go(self, direction: str):
        # Try and enter the new room
        new_room = self.room.try_go(direction)

        if new_room is not None:
            # In we go!
            self.room = new_room
            new_room.on_enter(self)
