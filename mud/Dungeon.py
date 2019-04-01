import socket
from Room import Room
from Item import Item
from Player import Player
from Client import Client

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

        # Create player and client list
        self.players = []
        self.clients = []

        # Assign this dungeon to all of the rooms
        for coordinates, room in self.rooms.items():
            room.dungeon = self

        # todo: Assign room names to all of the rooms?

    """
    Updates all necessary objects, players, etc in the dungeon
    """
    def update(self):
        # Update clients
        for client in self.clients:
            client.update()

        # Update room events
        for index, room in self.rooms.items():
            room.update()

        # Update players
        for player in self.players:
            player.update()

        # Remove disconnected clients
        for client_id in range(0, len(self.clients)):
            if not self.clients[client_id].is_connected:
                if self.clients[client_id].player is not None:
                    # Inform the world that the player is leaving
                    self.broadcast("<+info>%s has left the game.<-info>" % self.clients[client_id].player.name)

                    # Remove the player from the player list
                    self.players.remove(self.clients[client_id].player)

                # Remove the client
                self.clients.remove(self.clients[client_id])
                client_id -= 1

    """Adds a player to the dungeon
    
    Attributes:
        client: The client to be attached to the player
    Returns: The new player"""
    def add_player(self, client):
        # Create and add the player to the player list
        new_player = Player(self.rooms[self.entry_room], client)

        self.players.append(new_player)

        return new_player

    """Adds a client to the dungeon
    
    Attributes:
        client_socket: The socket of the player joining the dungeon"""
    def add_client(self, client_socket):
        self.clients.append(Client(self, client_socket))

    """Broadcasts a text to all players in the dungeon
    
    Attributes
        text_to_broadcast: The text to broadcast to the room
        exclude_players: A list of player references to exclude. These players do not receive the broadcast.
    """
    def broadcast(self, text_to_broadcast, exclude_players = None):
        for player in self.players:
            if exclude_players is None or player not in exclude_players:
                player.output(text_to_broadcast)
