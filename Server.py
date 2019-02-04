import socket
import threading

"""
Server handles network communications between players and the server

Attributes:
    game_port: the TCP port that the game will run on
"""

import time

class Server:
    game_port = 6282

    accept_socket = None

    def __init__(self):
        # Start the player-accepting thread
        self.accept_thread = threading.Thread(name="accept_thread", daemon=True, target=Server.accept_players)
        self.accept_thread.start()

    def receive_packets(self):
        pass

    @staticmethod
    def accept_players():
        # Setup server socket
        Server.accept_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            Server.accept_socket.bind(("localhost", Server.game_port))
        except socket.error as err:
            print("socket error:")
            print(err)

        # Listen for connections
        Server.accept_socket.listen()

        # Connect any new players to the dungeon
        while True:
            client_socket, address = Server.accept_socket.accept()
            data = client_socket.recv(1024)
            print("Got connection!")
            print(data.decode("utf-8"))