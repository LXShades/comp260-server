import Room
import Player

"""A (typically interactable in some way) item.

Attributes:
    name: Name of the item
    entry_description: The item description given to players when they enter the room
    commands: A dictionary of commands, along with the default text to be shown when the command is used.
              If there is an on_%s implementation on the object, where %s is the command name, it will be called.
    
"""


class Item:
    def __init__(self, name, entry_description=None, commands={}):
        # Initialise variables
        self.name = name
        self.room = None
        self.commands = commands

        # The description when the player enters the room
        self.entry_description = entry_description

    """Whether a command can be used on this item
    
    Attributes:
        command_name: Name of the command
        player: The player trying to use a command
    """
    def can_use_command(self, command_name, player=None):
        return command_name in self.commands

    """Performs a command on this item
    
    Attributes:
        command_name: Name of the command
        player: The player trying to use the command
    """
    def do_command(self, command_name, player = None):
        if hasattr(self, "on_%s" % command_name):
            # Print command message
            getattr(self, "on_%s" % command_name)
            return True
        return False

    """Called when a player quits the game
    
    Attributes:
        player: The player quitting
    """
    def on_player_quit(self, player):
        pass

    """Called when a player enters the room this item is in
    
    Attributes:
        player: The player entering the room
    """
    def on_player_enter(self, player):
        pass
