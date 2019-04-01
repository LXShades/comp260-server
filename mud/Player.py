import random
import cgi # for html-escape
from Client import Client
import Room
from Command import Command

# TEMP
import sqlite3
import bcrypt

"""A player in the game!

Attributes:
    name: The name of this player
    client: The Client attached to this player. This should not be None
    
    input_queue: Queue for player input. Filled by the recv thread and read by the update thread
    output_queue: Queue for player output. Filled by self.output, and read by the send thread.
    
    commands: List of commands available to this player
    
    room: The room this player is currently in
"""


class Player:
    """Creates the player in the given room

    Parameters:
        room: The room to start in
        client: The client to attach to the player
    """
    def __init__(self, room: Room, client: Client):
        # Initialise player IO
        self.client = client

        # Initialise player commands
        self.commands = {
            "help": Command("help", Player.cmd_help, "Get a list of all usable commands", "help", 0),
            "look": Command("look", Player.cmd_look, "Re-assess your surroundings", "look", 0),
            "name": Command("name", Player.cmd_rename, "Change your name", "name Doodyhead", 1),
            "say": Command("say", Player.cmd_say, "Say something to the current room", "say Hello, I'm a doofhead.", -1),
            "go": Command("go", Player.cmd_go, "<north, east, south, west> Go to another room", "go west", 1),
            "sql": Command("sql", Player.cmd_sql_test, "Do an SQL test", "sql drop tables; etc", -1),
            "login": Command("login", Player.cmd_login, "<user name> <password>", "register InsecureUser, letmein", 2)
        }

        # Give player a name
        self.name = Player.generate_name()
        room.dungeon.broadcast("<i><font color='green'><+player>%s<-player> has entered the game!</font></i>" % self.name)

        # Output an initial message to the player
        self.output("<+event>You awaken into this world as <+player>%s.<-player><-event>" % self.name)

        # Spawn in the given room
        self.room = room
        self.room.on_enter(self)

        self.output("<+info><i>Type <+command>help<-command> to view your list of commands.</i><-info><br>")
        self.output("<+info><i>Type <+command>look<-command> to re-assess your surroundings.</i><-info><br>")

    """Updates the player, flushing all inputs and outputs"""
    def update(self):
        # Flush inputs
        while not self.client.input_queue.empty():
            self.process_input(self.client.input_queue.get(False))

    """Outputs a string to the player

    Attributes:
        string: the string to output to the player
    """
    def output(self, string: str):
        # Send the string to the output stack for the next update
        self.client.output_queue.put(string, False)

    """Sends an input to this player. This will be processed during the next update.
    
    Attributes:
        user_input: the string being input
    """
    def input(self, user_input: str):
        # Send the input to the input stack for the next update
        self.client.input_queue.put(user_input, False)

    """Processes an input in this player. This should not be called except in update(). Call input() instead
    
    Attributes:
        user_input: the input string to process
    """
    def process_input(self, user_input: str):
        # Sanitise the input
        user_input = cgi.escape(user_input)

        # Check the command
        parameters: list = user_input.split(" ")
        command_name: str = parameters[0].lower()

        # Find and call the command function
        for command_n, command in self.commands.items():
            if command_n == command_name:
                # Ensure the correct number of parameters is supplied
                if len(parameters) - 1 == command.number_of_parameters or command.number_of_parameters == -1:
                    # Call the command function!
                    command.func(self, parameters[1:])
                    return
                else:
                    # Show example usage because player doesn't know what they're doing
                    self.output("Invalid input. Example usage: '%s'" % command.example_usage)
                    return

        # Or the command didn't exist
        self.output("Unknown command: %s" % command_name)

    """Displays the room entry message, updated with regard to items, players, etc"""
    def cmd_look(self, parameters: list):
        self.output("Refreshing room information...<br>")
        self.room.on_player_look(self)
        self.output("Done!<br>")

    """Say something to the entire dungeon"""
    def cmd_say(self, parameters: list):
        if len(parameters) > 0:
            # Reconstruct the speech text from the parameters
            speech = " ".join(parameters)

            self.room.broadcast("<+player>%s<-player> says: <+speech>%s<-speech>" % (self.name, speech))
        else:
            # Teach the user how to talk
            self.output("Usage: say I am beautiful, you are beautiful, we're all beautiful")

    """
    Go to another room in the given direction
    """
    def cmd_go(self, parameters: list):
        # Which direction are we going in?
        direction: str = parameters[0].lower()

        # Try and enter the new room
        new_room = self.room.try_go(direction)

        if new_room is not None:
            # Leave the current room
            self.room.on_exit(self, direction)

            # Into the new room!
            self.room = new_room
            self.output("<i>You enter <+room>%s</-room></i>" % self.room.title)

            # Enter the new room
            new_room.on_enter(self)
        else:
            self.output("<i>You are unable to go this way.</i>")

    """
    Changes your name
    """
    def cmd_rename(self, parameters: list):
        # Pick a random message to show after changing the name
        name_message = ""
        randomizer = random.randint(0, 3)

        if randomizer == 0:
            name_message = "Actually, <+player>" + self.name + "<-player>'s real name was <+player>" + parameters[0] + "<-player> this whole time."
        elif randomizer == 1:
            name_message = "Scratch that. <+player>" + self.name + "<-player>'s name is <+player>" + parameters[0] + "<-player> now."
        elif randomizer == 2:
            name_message = "<+player>" + self.name + "<-player> had us fooled all along, and has revealed their true name, <+player>" + parameters[0] + "<-player>!"
        elif randomizer == 3:
            name_message = "Wait, <+player>" + self.name + "<-player> changed their mind. Call them <+player>" + parameters[0] + "<-player> from now on."

        self.name = parameters[0]
        self.room.dungeon.broadcast("<+event>" + name_message + "<-event>")

    """
    Outputs the list of available commands
    """
    def cmd_help(self, parameters: list):
        self.output("You can perform the following commands:")

        for command_name, command in self.commands.items():
            self.output("<b><+item>%s:<-item></b> <i>%s</i><br>" % (command_name, command.usage))

    def cmd_sql_test(self, parameters: list):
        string = " ".join(parameters)

        # Execute an SQL database thing
        # Open the database
        connection = sqlite3.connect("players.db")

        # Grab a database cursor
        cursor = connection.cursor()

        # Execute some thing on the cursor
        try:
            for row in cursor.execute(string):
                for item in row:
                    self.output("> " + item + "<br>")

        except sqlite3.Error as err:
            self.output("SQL error:<br>" + err.args[0])

        # Done!
        connection.commit()

        # Close the databse
        connection.close()

    def cmd_login(self, parameters: list):
        # Connect to SQL
        connection = sqlite3.connect("players.db")

        # Create the table if it doesn't exist
        connection.execute("CREATE TABLE IF NOT EXISTS player_accounts(account_name, account_passhash, account_salt)")

        # If the user does not exist, register them
        username = parameters[0]
        local_salt = bcrypt.gensalt(12)
        password_hash = bcrypt.hashpw(parameters[1].encode("utf-8"), local_salt)

        try:
            ret = connection.execute("SELECT (account_passhash, account_salt) FROM player_accounts WHERE account_name IS (?)", (username,))
            row_info = ret.fetchall()

            if len(row_info) < 1:
                self.output("User account is not registered! Registering now...<br>")

                try:
                    # Add the user account to the database
                    # Rehash the password???
                    password_hash = bcrypt.hashpw(password_hash, bcrypt.gensalt(12))

                    connection.execute("INSERT INTO player_accounts VALUES (?,?)", (username, password_hash))
                    connection.commit()

                    self.output("Registration successful! You're now a welcomed victim of my dungeon.")
                except sqlite3.Error as err:
                    self.output("Exception while registering: " + err.args[0])
            else:
                self.output("Logging in...")

                # Check if the password is correct
                if bcrypt.checkpw(password_hash, row_info[0][0]):
                    self.output("Password correct! You're totally not a hacker")
                else:
                    self.output("Wrong password! You're totally not a good hacker")

        except sqlite3.Error as err:
            self.output("Exception: " + err.args[0])

        connection.close()


    """Generates a player name
    
    Returns: The randomly generated player name"""
    @staticmethod
    def generate_name():
        first = ["Engle", "Beef", "Spork", "Glommuck", "Bligg", "Memni", "Qrech", "Zleeph", "Zimple"]
        second = ["bork", "stoph", "strom", "rak", "bibble", "ziggy", "worth", "boid", "gloph"]
        third = ["Apostra", "Goven", "Rattler", "Yorky", "Pasta", "Hein", "Yerrel", "Peef"]
        fourth = ["glubber", "slipper", "ribbster", "zonky", "drizzle", "blimey"]
        return random.choice(first) + random.choice(second) + " " + random.choice(third) + random.choice(fourth)

    """Saves the player's state to the database"""
    def save_state(self):
        # Todo
        pass

    """Loads the player's state from the database"""
    def load_state(self):
        # Todo
        pass
