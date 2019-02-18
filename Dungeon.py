import socket
from Room import Room
from Item import Item
from Player import Player


class Dungeon:
    def __init__(self):
        # Create the rooms
        self.rooms = {
            "The Foyer": Room(
                "The Foyer",
                "Welcome to the bustling foyer!<br><br>* The bathroom is west.<br>* The exit is north.",
                {"west": "The bathroom", "north": "The library"}
            ),

            "The bathroom": Room(
                "The bathroom",
                "You enter the bathroom with a solemn heart. It smells like bathroom.<br>" +
                "The only pleasant sight is the mirror on the wall; rather, the face within it.<br>" +
                "You look beautiful today.",
                {"east": "The Foyer"},
            ),

            "The library": Room(
                "The library",
                "This room appears to be some sort of ancient, physical website. It's filled with reliable sources.",
                {"south": "The Foyer"},
                [Item("Book", "There is an open book sitting in the corner.")]
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
                self.broadcast("<i>%s has left the game.</i>" % self.players[player_id].name)
                self.players.remove(self.players[player_id])
                player_id -= 1

    """Adds a player to the dungeon
    
    Attributes:
        player_socket: Socket of the player joining the dungeon"""
    def add_player(self, player_socket: socket):
        self.players.append(Player(self.rooms[self.entry_room], player_socket))

    """Broadcasts a text to all players in the dungeon"""
    def broadcast(self, text_to_broadcast: str):
        for player in self.players:
            player.output(text_to_broadcast)
