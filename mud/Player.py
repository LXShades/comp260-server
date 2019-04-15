import queue
import random
import cgi  # for html-escape
from Item import Item
from Command import Command
from Database import Database

# TEMP
import sqlite3

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
    def __init__(self, dungeon, client):
        # Initialise player IO
        self.client = client
        self.dungeon = dungeon

        self.input_queue = queue.Queue()

        # Initialise player commands
        self.commands = {
            "help": Command("help", Player.cmd_help, "Get a list of all usable commands", "help", 0),
            "look": Command("look", Player.cmd_look, "Re-assess your surroundings", "look", 0),
            "name": Command("name", Player.cmd_rename, "Change your name", "name Doodyhead", 1),
            "say": Command("say", Player.cmd_say, "Say something to the current room", "say Hello, I'm a doofhead.", -1),
            "go": Command("go", Player.cmd_go, "<north, east, south, west> Go to another room", "go west", 1),
            "sql": Command("sql", Player.cmd_sql_test, "Do an SQL test", "sql drop tables; etc", -1),
            "inventory": Command("inventory", Player.cmd_inventory, "Displays your inventory", "inventory", 0)
        }

        # Load player state from the database
        cursor = Database.player_db.execute("SELECT last_room, character_name FROM players WHERE account_name IS (?)", (client.account_name,))
        values = cursor.fetchall()
        starting_room = dungeon.entry_room

        if len(values) > 0:
            starting_room = values[0][0]
            self.name = values[0][1]
        else:
            # Give the player a name
            self.name = Player.generate_name()

            # Add the new player to the database
            Database.player_db.execute("INSERT INTO players (account_name, character_name, last_room) VALUES (?, ?, ?)",
                                       (self.client.account_name, self.name, dungeon.entry_room))

            # Give them an inventory with a useful item
            self.inventory = [Item("Rubberduck", "It's a rubber duck. If you squeak it, it will tell you your fortune.", {"squeak": ""})]

        # Broadcast entry message
        self.dungeon.broadcast("<i><font color='green'><+player>%s<-player> has entered the game!</font></i>" % self.name)

        # Output an initial message to the player
        self.output("<+event>You awaken into this world as <+player>%s.<-player><-event><br>" % self.name)

        # Spawn in the given room
        self.room = dungeon.rooms[starting_room]

        self.output("<+action>You enter <+room>%s<-room><-action>" % self.room.title)
        self.room.on_enter(self)

        self.output("<+info><i>Type <+command>help<-command> to view your list of commands.</i><-info>")
        self.output("<+info><i>Type <+command>look<-command> to re-assess your surroundings.</i><-info><br>")

    """Destroys the player, saving progress"""
    def destroy(self):
        # Save your data
        Database.player_db.execute("""
            UPDATE players
            SET last_room = (?),
                character_name = (?)
                
            WHERE account_name IS (?)""",
            (self.room.title, self.name, self.client.account_name))

    """Updates the player, flushing all inputs and outputs"""
    def update(self):
        # Flush inputs
        while not self.input_queue.empty():
            self.process_input(self.input_queue.get(False))

    """Outputs a string to the player

    Attributes:
        string: the string to output to the player
    """
    def output(self, string):
        # Send the string to the output stack for the next update
        self.client.output_text(string)

    """Sends an input to this player. This will be processed during the next update.
    
    Attributes:
        user_input: the string being input
    """
    def input(self, user_input):
        # Send the input to the input stack for the next update
        self.input_queue.put(user_input, False)

    """Processes an input in this player. This should not be called except in update(). Call input() instead
    
    Attributes:
        user_input: the input string to process
    """
    def process_input(self, user_input):
        # Sanitise the input
        user_input = cgi.escape(user_input)

        # Check the command
        parameters = user_input.split(" ")
        command_name = parameters[0].lower()

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

        # That didn't work. Try item commands
        if len(parameters) > 1:
            target_object_name = parameters[1].lower()
            target_object = [x for x in self.room.items if x.name.lower() == target_object_name]

            if target_object is not None and len(target_object) > 0:
                if command_name in target_object[0].commands:
                    self.output(target_object[0].commands[command_name])
                    target_object[0].do_command(command_name, self)
                    return
                else:
                    self.output("%s does not have the command '%s'" % (target_object[0].name, command_name))
                    return

        # Or the command didn't exist
        self.output("Unknown command: %s" % command_name)

    """Displays the room entry message, updated with regard to items, players, etc"""
    def cmd_look(self, parameters):
        self.output("Refreshing room information...<br>")
        self.room.on_player_look(self)
        self.output("Done!<br>")

    """Say something to the entire dungeon"""
    def cmd_say(self, parameters):
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
    def cmd_go(self, parameters):
        # Which direction are we going in?
        direction = parameters[0].lower()

        # Try and enter the new room
        new_room = self.room.try_go(direction)

        if new_room is not None:
            # Leave the current room
            self.room.on_exit(self, direction)

            # Into the new room!
            self.room = new_room
            self.output("<i>You enter <+room>%s<-room></i>" % self.room.title)

            # Enter the new room
            new_room.on_enter(self)
        else:
            self.output("<i>You are unable to go this way.</i>")

    """
    Changes your name
    """
    def cmd_rename(self, parameters):
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
    def cmd_help(self, parameters):
        # Display general commands
        self.output("<+info>General commands:<-info><br>")

        for command_name, command in self.commands.items():
            self.output("<+command>%s:<-command> <i>%s</i>" % (command_name, command.usage))

        # Display item-specific commands and their usages
        self.output("<br><+info>Item commands:<-info><br>")

        item_commands = {}
        for item in self.room.items:
            for command in item.commands.keys():
                if command not in item_commands:
                    item_commands[command] = []
                item_commands[command].append(item.name)

        for command in item_commands:
            self.output("<+command>%s:<-command> %s" % (command, "<-item>, <+item>".join(item_commands[command])))

    """
    Displays the inventory
    """
    def cmd_inventory(self, parameters):
        self.output("You currently possess:<br><br>")

        for item in self.inventory:
            self.output("* <+item>%s<-item> (<+command>%s<-command>)" % (item.name, "<-command>, <+command>".join(item.commands)))

    def cmd_sql_test(self, parameters):
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
                    self.output("> " + item.decode("utf-8"))

        except sqlite3.Error as err:
            self.output("SQL error:<br>" + err.args[0])

        # Done!
        connection.commit()

        # Close the database
        connection.close()

    """Adds an item to the player's inventory and removes it from the room if applicable"""
    def add_to_inventory(self, item):
        self.inventory.append(item)

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
