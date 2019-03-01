import Room
import Player

"""A (typically interactable in some way) item.

Attributes:
    name: Name of the item
    entry_description: The item description given to players when they enter the room
    commands: A list of object commands which can be used on this object by players. [To be implemented]
    
"""


class Item:
    def __init__(self, name: str, entry_description: str=None):
        # Initialise variables
        self.name = name
        self.room = None

        # A map of all commands which can be used on this object
        self.commands = {}

        # The description when the player enters the room
        self.entry_description = entry_description

    """Whether a command can be used on this item
    
    Attributes:
        command_name: Name of the command
        player: The player trying to use a command
    """
    def can_use_command(self, command_name: str, player: Player=None):
        return command_name in self.commands

    """Performs a command on this item
    
    Attributes:
        command_name: Name of the command
        player: The player trying to use the command
    """
    def do_command(self, command_name: str, player: Player = None):
        pass

    """Called when a player quits the game
    
    Attributes:
        player: The player quitting
    """
    def on_player_quit(self, player: Player):
        pass

    """Called when a player enters the room this item is in
    
    Attributes:
        player: The player entering the room
    """
    def on_player_enter(self, player: Player):
        pass
