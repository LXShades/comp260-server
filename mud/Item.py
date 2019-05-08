import Room
import Player

"""A (typically interactable in some way) item.

Attributes:
    name: Name of the item
    entry_description: The item description given to players when they enter the room
    room: The room the item sits in (if applicable)
    player: The player owning the item (if applicable)
    commands: A dictionary of commands, along with the default text to be shown when the command is used.
              If there is an on_%s implementation on the object, where %s is the command name, it will be called.
    
"""


class Item:

    def __init__(self, item_id, name, entry_description=None, commands=None):
        # Initialise variables
        self.id = item_id
        self.name = name
        self.room = None
        self.player = None
        self.custom_data = {}

        if commands is not None:
            self.commands = commands
        else:
            self.commands = {}

        # The description when the player enters the room
        self.entry_description = entry_description

    def clone(self):
        copy = Item(self.id, self.name, self.entry_description, dict(self.commands))
        copy.room = self.room
        copy.player = self.player
        return copy

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
    def do_command(self, command_name, player, parameters):
        if hasattr(self, "cmd_%s" % command_name):
            # Print command message
            getattr(self, "cmd_%s" % command_name)(player, parameters)
            return True
        return False

    """(Default command) adds the item to the player's inventory"""
    def cmd_take(self, player, parameters):
        if self.player is None:
            player.output("<+event>You take the <+item>%s<-item>.<-event><br><br>" % self.name)
            player.add_to_inventory(self)
        else:
            player.output("<+error>You already have this.<-error>")

    def cmd_give(self, player, parameters):
        #target_player = [p in self.player.]
        # forcibly give an item to the player

    def cmd_drop(self, player, parameters):
        if self.room is None and self.player is player:
            player.output("<+event>You aggressively drop the <+item>%s<-item> onto the floor.<-event><br><br>" % self.name)

            # Drop the item into the room
            player.remove_from_inventory(self)
            player.room.add_item(self)

    def cmd_read(self, player, parameters):
        player.output("jflrekjkltjrkletj<br>")

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
