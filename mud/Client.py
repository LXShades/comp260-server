import queue
import threading
import socket
import time
import json
import base64
import random
from Crypto.Random import get_random_bytes
from Packet import Packet
import Dungeon

import sqlite3
import bcrypt

class Client:
    # Global number of sessions (incremental, ensuring unique session for each player)
    total_num_sessions = 0

    # Player states
    STATE_INIT = 0
    STATE_AUTHENTICATION = 1
    STATE_INGAME = 2
    STATE_REGISTERING = 3
    STATE_LOGGING_IN = 4

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
        self.packet_id = random.randint(0, 1000)

        Client.total_num_sessions += 1

        # Init account variables
        self.account_salt = b""
        self.account_name = ""

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
            self.state = Client.STATE_AUTHENTICATION

    """Sets the client state"""
    def set_state(self, new_state):
        # Don't change anything if we're already in the given state
        if self.state == new_state:
            return

        if new_state == Client.STATE_INGAME:
            # Create the player
            self.player = self.game.add_player(self)
        elif self.state == Client.STATE_INGAME:
            # Remove the player, later
            pass

        self.state = new_state

    """Handles user input during gameplay"""
    def process_ingame_input(self, input):
        # Send the command to the player
        self.player.input(input)

    """Handle user input during registering state"""
    def process_authentication_input(self, input):
        # Split the command
        inputs = str.split(input, " ")

        if inputs[0] == "login":
            if len(inputs) == 2:
                # Send the salt
                self.try_login(inputs[1], "")
            else:
                self.output_text("<+info>Usage: login [username]<-info>")
        elif inputs[0] == "register":
            # Inform the user of what to do
            if len(inputs) == 2:
                self.try_register(inputs[1], "")
            else:
                self.output_text("<+info>Usage: register [username]<-info>")
        else:
            self.output_text("<+info>Type <+command>login<-command> or <+command>register<-command>.<-info>")

    def process_registering_input(self, input):
        self.output_text("<+info>Registering your account...<-info>")

        # Try to register with this password
        if self.try_register(self.account_name, input):
            # We're done, enter the game!
            self.output_text("<+info>Registration complete! Welcome to the game!<-info>")
            self.set_state(Client.STATE_INGAME)
        else:
            # Failed, return to authentication
            self.output_text("<+error>Unknown error registering your account. Please try again.<-error>")
            self.set_state(Client.STATE_AUTHENTICATION)

    def process_login_input(self, input):
        self.output_text("<+info>Logging in...<-info>")

        # Try to login with this password
        if self.try_login(self.account_name, input):
            # We're in!
            self.output_text("<+info>Welcome back, %s!<-info>" % self.account_name)
            self.set_state(Client.STATE_INGAME)
        else:
            # Failed, return to authentication
            self.output_text("<+error>Wrong username or password. Please try again.<-error>")
            self.set_state(Client.STATE_AUTHENTICATION)
        # Deja vu? This code looks very familiar...................

    def try_register(self, username, password):
        # Make sure the account doesn't already exist
        # Connect to SQL
        connection = sqlite3.connect("players.db")

        try:
            # Create the table if it doesn't exist (todo: do this on init)
            connection.execute("CREATE TABLE IF NOT EXISTS player_accounts(name, passhash, salt)")

            # Ensure the username doesn't already exist
            cursor = connection.execute("SELECT (1) FROM player_accounts WHERE name IS (?)", (username,))
            values = cursor.fetchall()

            if len(values) > 0:
                self.output_text("<+error>This account already exists.<-error>")
                connection.close()
                return False
            else:
                if self.state == Client.STATE_AUTHENTICATION:
                    # Request a password for this new account
                    self.account_name = username
                    self.account_salt = bcrypt.gensalt(12)
                    self.request_password()

                    self.output_text("<+info>Welcome aboard, %s! Please type a password:<-info>" % username)

                    # Advance to the next state
                    self.set_state(Client.STATE_REGISTERING)

                elif self.state == Client.STATE_REGISTERING:
                    # We should have a password now
                    if password != None and len(password) > 0:
                        # Add the account to the database
                        connection.execute("INSERT INTO player_accounts VALUES (?,?,?)", (username, password, self.account_salt))
                        connection.commit()
                        connection.close()

                        # Registratino successful!
                        return True
                    else:
                        self.output_text("Invalid password. Please type another.")
        except sqlite3.Error as err:
            self.output_text("SQL exception: " + err.args[0])

        connection.close()
        return False

    """Tries to log the user in"""
    def try_login(self, username, password):
        # Connect to SQL
        connection = sqlite3.connect("players.db")

        # Create the table if it doesn't exist (todo: do this on init)
        connection.execute("CREATE TABLE IF NOT EXISTS player_accounts(name, passhash, salt)")

        try:
            if self.state == Client.STATE_AUTHENTICATION:
                # Request the password
                self.account_name = username
                self.account_salt = self.get_user_salt(username)
                self.request_password()

                self.output_text("<+info>Please type your password:<-info>")

                # Advance to logging in state
                self.set_state(Client.STATE_LOGGING_IN)

            elif self.state == Client.STATE_LOGGING_IN:
                # Get the password hash from the account database
                ret = connection.execute("SELECT (passhash) FROM player_accounts WHERE name IS (?)", (username,))
                row_info = ret.fetchall()

                connection.close()

                # Ensure the account exists
                if len(row_info) < 1:
                    return False

                # Check the password
                is_password_correct = row_info[0][0] == password

                # Ensure the account isn't already logged in
                if is_password_correct:
                    if len([player for player in self.game.players if player.client.account_name == self.account_name]) > 0:
                        return False

                # Login was successful!
                return True

        except sqlite3.Error as err:
            self.output_text("Exception: " + err.args[0])

        connection.close()
        return False

    """Outputs a string to the client"""
    def output_text(self, string):
        # Create the packet
        packet_data = {
            "type": "output",
            "text": string
        }

        self.output_queue.put(json.dumps(packet_data).encode(), False)

    # Requests a password from the client
    def request_password(self):
        packet_data = {
            "type": "salt",
            "salt": self.account_salt.decode("utf-8")
        }

        self.output_queue.put(json.dumps(packet_data).encode(), False)

        """Returns the encoded password salt for a user account, or a random salt if the account doesn't exist"""

    def get_user_salt(self, username):
        connection = sqlite3.connect("players.db")

        try:
            # Create the table if it doesn't exist (todo: do this on init)
            connection.execute("CREATE TABLE IF NOT EXISTS player_accounts(name, passhash, salt)")

            # Get the salt for this user
            cursor = connection.execute("SELECT (salt) FROM player_accounts WHERE name IS (?)", (username,))
            values = cursor.fetchall()

            if len(values) == 0:
                # Account doesn't exist, but send a random salt anyway
                return bcrypt.gensalt(12)
            else:
                return values[0][0]

        except sqlite3.Error as err:
            self.output_text("Exception getting salt: " + err.args[0])

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
                    data = Packet.unpack(packet, self.encryption_key, self.session_id, self.packet_id)
                    self.packet_id += 1

                    if data is not None:
                        if self.state == Client.STATE_INIT:
                            pass
                        if self.state == Client.STATE_INGAME:
                            self.process_ingame_input(data.decode("utf-8"))
                        elif self.state == Client.STATE_AUTHENTICATION:
                            self.process_authentication_input(data.decode("utf-8"))
                        elif self.state == Client.STATE_REGISTERING:
                            self.process_registering_input(data.decode("utf-8"))
                        elif self.state == Client.STATE_LOGGING_IN:
                            self.process_login_input(data.decode("utf-8"))
                    else:
                        print("Invalid packet received -- removing client")
                        self.is_connected = False    # I'm just glad
                else:
                    print("Partial message received -- removing client")
                    self.is_connected = False        # we aren't being
            except socket.error as error:
                print("Client error, removing client")
                self.is_connected = False            # marked on maintainability

    """Runs the thread used for networked output to this player's client"""
    def send_thread(self):
        # Send the encryption info and session/packet ID to the player client
        client_info = {
            "type": "security",
            "session_id": self.session_id,
            "packet_id": self.packet_id,
            "encryption_key": base64.b64encode(self.encryption_key).decode("utf-8"),
            "bacon_key": base64.b64encode(get_random_bytes(16)).decode("utf-8")
            # this is bacon. it actually does nothing, it just runs on the theory that a hacker
            # would, under his assumption that he is being fooled, prefer to grab the bacon instead of the key
            # it also gives the appearance of some voodoo extra-strong encryption technique, which I am in fact
            # not smart or magic enough to implement
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
                    packet_packaged = Packet.pack(output, self.encryption_key, self.session_id, self.packet_id)

                    # Send the message
                    self.socket.send(len(packet_packaged).to_bytes(2, 'little') + packet_packaged)
            except socket.error as error:
                # Disconnect
                print("Client error, removing client")
                self.is_connected = False

            # Wait a bit
            time.sleep(0.1)