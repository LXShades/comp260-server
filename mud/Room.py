from Player import Player
from Database import Database

import json

"""
A room is an area of a dungeon connected by possible rooms to the north, east, south or west

Attributes:
    dungeon: Reference to the dungeon that owns this room
    title: The title of the room
    description: The description of the room displayed to players when they enter.
    connections: A dictionary of rooms "east", "west", "north" or "south" of this room
    items: List of active items in the room
"""


class Room:
    def __init__(self, title, description, connections, items=None):
        self.title = title
        self.description = description
        self.connections = connections
        self.items = items
        self.dungeon = None

        if items is None:
            # Create a new list for items.
            # BUG FIXED: items was originally a default parameter, items=[], but this was being shared across all rooms!
            self.items = []

    """Called whenever a player enters the room
    
    Attributes:
        player: The player entering the room
    """
    def on_enter(self, player):
        self.broadcast("<+action><+player>%s<-player> entered the room.<-action><br>" % player.name, [player])
        self.on_player_look(player)

        # Call item entry callbacks
        for item in self.items:
            item.on_player_enter(player)

    """Called whenever a player exits the room
    
    Attributes:
        player: The player exiting the room
        direction: The direction the player is going in
    """
    def on_exit(self, player, direction):
        self.broadcast("<+action><+player>%s<-player> went %s<-action><br>" % (player.name, direction), [player])

    """Called when a player tries to move in a direction.
    
    Attributes:
        direction: The direction to move in. "north", "south", "east" or "west"
    Returns: If the move was successful, the destination room.
"""
    def try_go(self, direction):
        if direction in self.connections and self.connections[direction] in self.dungeon.rooms:
            # Return the room at this target
            return self.dungeon.rooms[self.connections[direction]]
        else:
            # We can't go there!
            return None

    """Called when the player uses the look command
    
    Attributes:
        player: The player looking around
    """
    def on_player_look(self, player):
        # Send the room title
        player.output("<+room_title>" + self.title + "<-room_title>")

        # Send the room info
        room_info = "<+room_info>"
        room_info += self.description + "<br><br>"

        # Display item-specific entry descriptions
        for item in self.items:
            room_info += "* %s (<+command>%s<-command>)<br>" % (item.entry_description, "<-command>, <+command>".join(list(item.commands.keys())))

        # Display names of other players in this room
        for other_player in self.dungeon.players:
            if other_player is not player and other_player.room is self:
                room_info += "* <+player>%s<-player> is here.<br>" % other_player.name

        # Send to the player
        room_info += "<-room_info><br>"
        player.output(room_info)

    """Broadcasts some text to every player in the room"""
    def broadcast(self, text_to_broadcast, exclude_players = None):
        for player in self.dungeon.players:
            # Broadcast to every player in the room, except excluded players
            if player.room is self and (exclude_players is None or player not in exclude_players):
                player.output(text_to_broadcast)

    """Called during game update. Overridable"""
    def update(self):
        pass

    def save(self):
        # Save the item list
        Database.room_db.execute("""
            UPDATE rooms
            SET items = (?)

            WHERE title IS (?)""",
                (json.dumps([(x.id, x.custom_data) for x in self.items]), self.title))
        Database.player_db.commit()

    """Adds an item to the room"""
    def add_item(self, item):
        if item.player is not None:
            item.player.remove_from_inventory(item)

        self.items.append(item)
        item.room = self

    """Removes an item from the room"""
    def remove_item(self, item):
        self.items.remove(item)
        item.room = None
