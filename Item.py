import Room
import Player


class Item:
    def __init__(self, name: str, room: Room, entry_description=None):
        # Initialise variables
        self.name = name
        self.room = room

        # A list of all commands which can be used on this object
        self.commands = []

        # The description when the player enters the room
        self.entry_description = entry_description

    # Checks if a command can be used on this item
    def can_use_command(self, command_name: str, player: Player = None):
        return command_name in self.commands

    # Called when the player performs a command on this item
    def do_command(self, command_name: str, player: Player = None):
        pass

    # Called when a player quits the game
    def on_player_quit(self, player: Player):
        pass

    # Called when a player enters the room
    def on_player_enter(self, player: Player):
        pass
