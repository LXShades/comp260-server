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
            player.room.broadcast("<+event>%s picks up a <+item>%s<-item><br>" % (player.name, self.name), [player])
            player.add_to_inventory(self)
        else:
            player.output("<+error>You already have this.<-error>")

    def cmd_give(self, player, parameters):
        if len(parameters) > 0:
            target_player = [p for p in player.dungeon.players if p.room == player.room and p.name.lower() == parameters[0].lower()]

            if len(target_player) > 0:
                player.output("<event>You forcibly give the <+item>%s<-item> to <+player>%s<-player><-event><br>" % (self.name, target_player[0].name))
                target_player[0].output("<event><+player>%s<-player> forcibly hands you a <+item>%s<-item><-event><br>" % (player.name, self.name))

                if self.player is not None:
                    self.player.remove_from_inventory(self)
                elif self.room is not None:
                    self.room.remove_item(self)

                target_player[0].add_to_inventory(self)
        else:
            player.output("<+info>Usage: give [item] [player]<-info><br>")

    def cmd_drop(self, player, parameters):
        if self.room is None and self.player is player:
            player.output("<+event>You aggressively drop the <+item>%s<-item> onto the floor.<-event><br><br>" % self.name)
            player.room.broadcast("<+event><+player>%s<-player> drops a <+item>%s<-item> onto the floor.<br>" % (player.name, self.name), [player])

            # Drop the item into the room
            player.remove_from_inventory(self)

    def cmd_read(self, player, parameters):
        pass

    def cmd_whisper(self, player, parameters):
        if len(parameters) > 0:
            text = " ".join(parameters)
            player.output("<+event>You whisper to the <+item>%s<-item>...it will remember that.<-event><br>" % (self.name))
            self.custom_data["message"] = text
        else:
            player.output("<+info>Usage: whisper [item] [message]<-info><br>")

    def cmd_squeak(self, player, parameters):
        if "message" in self.custom_data:
            player.output("<+event>You squeak the <+item>%s<-item>. It whispers into your ears...<br><br>%s" % (self.name, self.custom_data["message"]))
        else:
            player.output("<+event>You squeak the <+item>%s<-item>. It makes a light, wheezing sound<-event><br>" % self.name)

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
