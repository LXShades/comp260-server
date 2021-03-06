import socket
import threading
import sys

"""
Server handles network communications between players and the server

Attributes:
    game: reference to the game; used to add players
    game_port: the TCP port that the game will run on
    listening_socket: the socket listening for TCP connections
"""


class Server:
    game = None

    def __init__(self, game):
        # Initialise vars
        self.game = game
        self.game_port = 9123
        self.listening_socket = None

        # Start the player-accepting thread
        threading.Thread(name="accept_thread", target=lambda: self.accept_thread(), daemon=True).start()

    """Thread that accepts incoming player connections"""
    def accept_thread(self):
        # Setup server socket
        self.listening_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the server socket
        try:
            # Find the primary IP to bind to
            bind_ip = "localhost"
            ip_finder = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

            try:
                ip_finder.connect(('10.255.255.255', 1))
                bind_ip = ip_finder.getsockname()[0]
            finally:
                ip_finder.close()

            # Bind to it
            self.listening_socket.bind((bind_ip, self.game_port))
        except socket.error as err:
            print("Could not create server socket. The server could be running already. Shutting down.")
            return

        # Inform the user of successful creation
        print("Server creation successful! Waiting for players.")

        # Listen for connections
        self.listening_socket.listen()

        # Connect any new players to the dungeon
        while True:
            # Accept incoming players
            client_socket, address = self.listening_socket.accept()

            print("Got new connection! Adding client.")

            # Create the client
            self.game.add_client(client_socket)
