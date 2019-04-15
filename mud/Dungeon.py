import socket
from Room import Room
from Item import Item
from Player import Player
from Client import Client
from Database import Database

import queue
import json
import sqlite3

"""A dungeon containing players, and a map of hazardous precarious rooms or 'zones' to survive.

Attributes:
    entry_room: The name of the room players begin in when they enter the game
    rooms: A name-indexed map of rooms in this dungeon
    
    player: The list of players in this dungeon
"""


class Dungeon:
    def __init__(self):
        # Load the rooms from the database
        cursor = Database.room_db.execute("SELECT * FROM rooms")
        room_list = cursor.fetchall()

        self.rooms = {}

        for index, room in enumerate(room_list):
            try:
                # Add the new room
                self.rooms[room[0]] = Room(room[0], room[1], Database.read_json(room[2]))

                # Load the items
                if room[3] is not None:
                    items = Database.read_json(room[3])
                    for item in items:
                        if Database.item_definitions[item] is not None:
                            self.rooms[room[0]].items.append(Database.item_definitions[item])

            except Exception as err:
                print("Warning: Exception occurred while processing room at index %s. Please verify the data." % str(index))
                if len(room) > 0 and type(room[0]) == str:
                    print("Room name: " + room[0])
                print("Exception: " + err.args[0])

        # Use the first room in the database as the entry room
        if len(room_list) > 0:
            self.entry_room = room_list[0][0]
        else:
            self.entry_room = ""
            print("Uh, server manager sir/ma'am... there aren't any rooms in this dungeon... I'm gonna continue anyway but this isn't cool OK?")

        # Create player and client list
        self.players = []
        self.clients = []
        self.incoming_clients = queue.Queue()

        # Assign this dungeon to all of the rooms
        for coordinates, room in self.rooms.items():
            room.dungeon = self

        # todo: Assign room names to all of the rooms?

    """
    Updates all necessary objects, players, etc in the dungeon
    """
    def update(self):
        # Add new queued clients
        while not self.incoming_clients.empty():
            self.clients.append(self.incoming_clients.get(False))

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
        client_id = 0
        while client_id < len(self.clients):
            if not self.clients[client_id].is_connected:
                if self.clients[client_id].player is not None:
                    # Inform the world that the player is leaving
                    self.broadcast("<+info>%s has left the game.<-info>" % self.clients[client_id].player.name)

                    # Remove the player from the player list
                    self.clients[client_id].player.destroy()
                    self.players.remove(self.clients[client_id].player)

                # Remove the client
                self.clients.remove(self.clients[client_id])
            else:
                client_id += 1

    """Destroys the dungeon and saves all players"""
    def destroy(self):
        for client in self.clients:
            if client.player is not None:
                client.player.destroy()

    """Adds a player to the dungeon
    
    Attributes:
        client: The client to be attached to the player
    Returns: The new player"""
    def add_player(self, client):
        # Create and add the player to the player list
        new_player = Player(self, client)

        self.players.append(new_player)

        return new_player

    """Adds a new client to the dungeon. Thread-safe
    
    Attributes:
        client_socket: The socket of the player joining the dungeon"""
    def add_client(self, client_socket):
        self.incoming_clients.put(Client(self, client_socket))

    """Broadcasts a text to all players in the dungeon
    
    Attributes
        text_to_broadcast: The text to broadcast to the room
        exclude_players: A list of player references to exclude. These players do not receive the broadcast.
    """
    def broadcast(self, text_to_broadcast, exclude_players = None):
        for player in self.players:
            if exclude_players is None or player not in exclude_players:
                player.output(text_to_broadcast)
