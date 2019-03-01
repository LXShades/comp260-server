import socket
from Room import Room
from Item import Item
from Player import Player

"""A dungeon containing players, and a map of hazardous precarious rooms or 'zones' to survive.

Attributes:
    entry_room: The name of the room players begin in when they enter the game
    rooms: A name-indexed map of rooms in this dungeon
    
    player: The list of players in this dungeon
"""


class Dungeon:
    def __init__(self):
        # Create the rooms
        self.rooms = {
            "The Foyer": Room(
                "The Foyer",
                "Welcome to the bustling foyer!<br><br>* The bathroom is west.<br>* The library is north.",
                {"west": "The bathroom", "north": "The library"}
            ),

            "The bathroom": Room(
                "The bathroom",
                "You enter the bathroom with a solemn heart. It smells like toilet, and looks like toilets.<br>" +
                "The only pleasant sight here is the mirror on the wall; rather, the face within it.<br><br>" +
                "You look beautiful today.<br><br>" +
                "* The foyer is east.<br>",
                {"east": "The Foyer"},
            ),

            "The library": Room(
                "The library",
                "This room appears to be some sort of ancient, physical website. It's filled with reliable sources.<br><br>" +
                "* The foyer is south.<br>",
                {"south": "The Foyer"},
                [Item("Book", "There is an open <+item>book<-item> sitting in the corner.")]
            )
        }

        # This is where it all begins
        self.entry_room = "The Foyer"

        self.players = []

        # Assign this dungeon to all of the rooms
        for coordinates, room in self.rooms.items():
            room.dungeon = self

        # todo: Assign room names to all of the rooms?

    """
    Updates all necessary objects, players, etc in the dungeon
    """
    def update(self):
        # Update room events
        for index, room in self.rooms.items():
            room.update()

        # Update players
        for player in self.players:
            player.update()

        # Remove disconnected players
        for player_id in range(0, len(self.players)):
            if not self.players[player_id].is_connected:
                self.broadcast("<+info>%s has left the game.<-info>" % self.players[player_id].name)
                self.players.remove(self.players[player_id])
                player_id -= 1

    """Adds a player to the dungeon
    
    Attributes:
        player_socket: Socket of the player joining the dungeon"""
    def add_player(self, player_socket: socket):
        self.players.append(Player(self.rooms[self.entry_room], player_socket))

    """Broadcasts a text to all players in the dungeon
    
    Attributes
        text_to_broadcast: The text to broadcast to the room
        exclude_players: A list of player references to exclude. These players do not receive the broadcast.
    """
    def broadcast(self, text_to_broadcast: str, exclude_players: list = None):
        for player in self.players:
            if exclude_players is None or player not in exclude_players:
                player.output(text_to_broadcast)
