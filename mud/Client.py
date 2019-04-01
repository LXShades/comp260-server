import queue
import threading
import socket
import time
import Dungeon

class Client:
    # Player states
    STATE_INIT = 0
    STATE_LOGIN = 1
    STATE_INGAME = 2

    def __init__(self, game: Dungeon, my_socket: socket):
        # Startup!
        self.game = game
        self.is_connected = True

        # Keep the socket
        self.socket = my_socket

        # Begin in the initialisation state
        self.state = Client.STATE_INGAME

        # Start without a connected player. Client will gain a player once they log in
        self.player = None

        # Create the IO queues
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

        # Run the networking threads
        self.running_input_thread = threading.Thread(daemon=True, target=lambda: self.recv_thread())
        self.running_output_thread = threading.Thread(daemon=True, target=lambda: self.send_thread())
        self.running_input_thread.start()
        self.running_output_thread.start()

    """Flushes client inputs, sending them to the connected player if applicable. Called during a game tick"""
    def update(self):
        if self.player is None:
            # Temp: Create the player
            self.player = self.game.add_player(self)


    """Runs the thread used to receive input from this player's client"""
    def recv_thread(self):
        while self.is_connected:
            # Get the next message from the player
            try:
                # Get message size
                data_header = self.socket.recv(2)

                # Get message contents
                data = self.socket.recv(int.from_bytes(data_header, 'little'))

                # Todo: Check state, etc
                if len(data) > 0:
                    if self.state == Client.STATE_INIT:
                        # Check that the player has sent a valid join request
                        pass

                    if self.state == Client.STATE_INGAME:
                        # Receive a player command
                        self.player.input(data.decode("utf-8"))
                else:
                    self.is_connected = False
            except socket.error as error:
                print("Client error, removing client")
                self.is_connected = False

    """Runs the thread used for networked output to this player's client"""
    def send_thread(self):
        while self.is_connected:
            # Output the current messages to the player, if possible
            try:
                # Send any existing player outputs
                while not self.output_queue.empty():
                    output = self.output_queue.get(False).encode()
                    output_size = len(output)

                    # Send message size and data
                    self.socket.send(output_size.to_bytes(2, 'little') + output)
            except socket.error as error:
                # Disconnect
                print("Client error, removing client")
                self.is_connected = False

            # Wait a bit
            time.sleep(0.1)