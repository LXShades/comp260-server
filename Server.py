import socket
import threading
import sys

"""
Server handles network communications between players and the server

Attributes:
    game_port: the TCP port that the game will run on
"""


class Server:
    game = None

    def __init__(self, game):
        # Initialise vars
        self.game = game
        self.game_port = 6282
        self.accept_socket = None

        # Start the player-accepting thread
        self.accept_thread = threading.Thread(name="accept_thread", target=lambda: self.accept_players(), daemon=True)
        self.accept_thread.start()

    def receive_packets(self):
        pass

    def accept_players(self):
        self.game = self.game
        # Setup server socket
        self.accept_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            self.accept_socket.bind(("localhost", self.game_port))
        except socket.error as err:
            print("Could not create server socket. That's kinda important brah. Shutting down.")
            return

        # Listen for connections
        self.accept_socket.listen()

        # Connect any new players to the dungeon
        while True:
            # Accept incoming players
            client_socket, address = self.accept_socket.accept()

            print("Got new connection! Adding player.")

            # Create the player
            self.game.add_player(client_socket)
