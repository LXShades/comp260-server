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
        self.broadcast("<i><+player>%s<-player> entered the room.</i><br>" % player.name, [player])
        self.on_player_look(player)

        # Call item entry callbacks
        for item in self.items:
            item.on_player_enter(player)

    """
    Called whenever a player exits the room
    """
    def on_exit(self, player: Player, direction: str):
        self.broadcast("<i><+player>%s<-player> went %s</i><br>" % (player.name, direction), [player])

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
        # Display the room description to the player
        player.output(self.description + "<br>")

        # Display item-specific entry descriptions to the player
        for item in self.items:
            player.output("* %s" % item.entry_description)

        # Display names of other players in this room
        for other_player in self.dungeon.players:
            if other_player is not player and other_player.room is self:
                player.output("* <+player>%s<-player> is here.<br>" % other_player.name)

    """Broadcasts some text to every player in the room"""
    def broadcast(self, text_to_broadcast: str, exclude_players: list = None):
        for player in self.dungeon.players:
            # Broadcast to every player in the room, except excluded players
            if player.room is self and (exclude_players is None or player not in exclude_players):
                player.output(text_to_broadcast)

    def update(self):
        pass
