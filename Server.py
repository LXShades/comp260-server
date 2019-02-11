import socket
import threading
import time

"""
Server handles network communications between players and the server

Attributes:
    game_port: the TCP port that the game will run on
"""


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
            print("socket error: perhaps you have more than one instance of this game running?")

        # Listen for connections
        Server.accept_socket.listen()

        # Connect any new players to the dungeon
        while True:
            client_socket, address = Server.accept_socket.accept()

            print("Got connection!")

            # Connection received! Try to serve it
            is_connected = True
            while is_connected:
                try:
                    data = client_socket.recv(1024)

                    if(len(data) > 0):
                        print("Server recv:" + data.decode("utf-8"))
                    else:
                        is_connected = False
                except socket.error as err:
                    print("Client error, closing client")
                    is_connected = False

                time.sleep(0.1)
