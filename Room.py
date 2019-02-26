from Player import Player
"""
A room is an area of the game in which player actions can take place.

Attributes:
"""


class Room:
    def __init__(self, title: str, description: str, connections: dict, items: list=[]):
        self.title = title
        self.description = description
        self.connections = connections
        self.items = items
        self.dungeon = None

    """
    Called whenever a player enters the room
    """
    def on_enter(self, player: Player):
        self.broadcast("<+action><+player>%s<-player> entered the room.<-action><br>" % player.name, [player])
        self.on_player_look(player)

        # Call item entry callbacks
        for item in self.items:
            item.on_player_enter(player)

    """
    Called whenever a player exits the room
    """
    def on_exit(self, player: Player, direction: str):
        self.broadcast("<+action><+player>%s<-player> went %s<-action><br>" % (player.name, direction), [player])

    """Called when a player tries to move in a direction.
    
    Returns: If the move was successful, the destination room."""
    def try_go(self, direction: str):
        if direction in self.connections and self.connections[direction] in self.dungeon.rooms:
            # Return the room at this target
            return self.dungeon.rooms[self.connections[direction]]
        else:
            # We can't go there!
            return None

    """Called when the player uses the look command"""
    def on_player_look(self, player: Player):
        # Send the room title
        player.output("<+room_title>" + self.title + "<-room_title>")

        # Send the room info
        room_info = "<+room_info>"
        room_info += self.description + "<br><br>"

        # Display item-specific entry descriptions
        for item in self.items:
            room_info += "* %s" % item.entry_description

        # Display names of other players in this room
        for other_player in self.dungeon.players:
            if other_player is not player and other_player.room is self:
                room_info += "* <+player>%s<-player> is here.<br>" % other_player.name

        # Send to the player
        room_info += "<-room_info><br>"
        player.output(room_info)

    """Broadcasts some text to every player in the room"""
    def broadcast(self, text_to_broadcast: str, exclude_players: list = None):
        for player in self.dungeon.players:
            # Broadcast to every player in the room, except excluded players
            if player.room is self and (exclude_players is None or player not in exclude_players):
                player.output(text_to_broadcast)

    def update(self):
        pass
