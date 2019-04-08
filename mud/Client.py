import queue
import threading
import socket
import time
import json
import base64
from Crypto.Random import get_random_bytes
from Packet import Packet
import Dungeon

class Client:
    # Global number of sessions (incremental, ensuring unique session for each player)
    total_num_sessions = 0

    # Player states
    STATE_INIT = 0
    STATE_LOGIN = 1
    STATE_INGAME = 2

    def __init__(self, game, my_socket):
        # Startup!
        self.game = game
        self.is_connected = True
        self.last_login_attempt_time = 0

        # Keep the socket
        self.socket = my_socket

        # Begin in the initialisation state
        self.state = Client.STATE_INIT

        # Init networking variables
        self.session_id = Client.total_num_sessions
        self.encryption_key = get_random_bytes(16)
        self.packet_id = 0
        Client.total_num_sessions += 1

        # Start without a connected player. Client will gain a player once they log in
        self.player = None

        # Create the IO queues
        self.output_queue = queue.Queue()

        # Run the networking threads
        self.running_input_thread = threading.Thread(daemon=True, target=lambda: self.recv_thread())
        self.running_output_thread = threading.Thread(daemon=True, target=lambda: self.send_thread())
        self.running_input_thread.start()
        self.running_output_thread.start()

    """Flushes client inputs, sending them to the connected player if applicable. Called during a game tick"""
    def update(self):
        if self.state == Client.STATE_INIT:
            self.output_text("Welcome to the MUD!" +
                                  "<br>* Type 'login' to log in to an existing account." +
                                  "<br>* Type 'register' to begin creating an account.<br><br>")

            # Begin login state
            self.state = Client.STATE_INGAME

            # Temp: Create our player!
            self.player = self.game.add_player(self)
        elif self.state == Client.STATE_LOGIN:
            # Process the user's input
            login_confirmation = {
                "type": "login_confirmed"
            }

    """User login attempt??"""
    def try_login(self, username, password):
        self.last_login_attempt_time = time.time()

    """Outputs a string to the client"""
    def output_text(self, string):
        # Send this as an encrypted packet
        self.output_queue.put(string.encode(), False)

    """Runs the thread used to receive input from this player's client"""
    def recv_thread(self):
        while self.is_connected:
            # Get the next message from the player
            try:
                # Get next message
                data_header = int.from_bytes(self.socket.recv(2), "little")
                packet = self.socket.recv(data_header, socket.MSG_WAITALL)

                if len(packet) == data_header:
                    # Decrypt packet
                    data = Packet.unpack(packet, self.encryption_key)

                    if self.state == Client.STATE_INIT:
                        # Check that the player has sent a valid join request
                        pass

                    if self.state == Client.STATE_INGAME:
                        # Receive a player command
                        self.player.input(data.decode("utf-8"))
                else:
                    print("Partial message received, removing client?")
                    self.is_connected = False
            except socket.error as error:
                print("Client error, removing client")
                self.is_connected = False

    """Runs the thread used for networked output to this player's client"""
    def send_thread(self):
        # Send the encryption info and session/packet ID to the player client
        client_info = {
            "session_id": self.session_id,
            "packet_id": self.packet_id,
            "encryption_key": base64.b64encode(self.encryption_key).decode("utf-8"),
            "bacon_key": base64.b64encode(get_random_bytes(16)).decode("utf-8")
            # this is bacon. it actually does nothing, it just runs on the theory that a hacker
            # would, under his assumption that he is being fooled, prefer to grab the bacon instead of the key
            # it also gives the appearance of some voodoo extra-strong encryption power
            # overall, a hacker needs food too and I respect that
        }
        initial_packet_packaged = json.dumps(client_info).encode()

        self.socket.send(len(initial_packet_packaged).to_bytes(2, 'little') + initial_packet_packaged)

        # Begin the main message send loop
        while self.is_connected:
            # Output the current messages to the player, if possible
            try:
                # Send any existing player outputs
                while not self.output_queue.empty():
                    # Find next message to send
                    output = self.output_queue.get(False)

                    # Package this message
                    packet_packaged = Packet.pack(output, self.encryption_key)

                    # Send the message
                    self.socket.send(len(packet_packaged).to_bytes(2, 'little') + packet_packaged)
            except socket.error as error:
                # Disconnect
                print("Client error, removing client")
                self.is_connected = False

            # Wait a bit
            time.sleep(0.1)