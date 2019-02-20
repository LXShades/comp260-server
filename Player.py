import Room
from Command import Command
import threading
import socket
import random
import time
import queue

"""A player in the game!

Attributes:
    room: current Room that the player is in
"""


class Player:
    """Creates the player in the given room

    Parameters:
        room: The room to spawn in
        player_socket: The connection to this player
    """
    def __init__(self, room: Room, player_socket: socket):
        # Initialise player IO
        self.socket = player_socket
        self.is_connected = True

        self.input_stack = queue.Queue()
        self.output_stack = queue.Queue()

        # Initialise player commands
        self.commands = {
            "help": Command("help", Player.help, "Get a list of all usable commands", "help", 0),
            "look": Command("look", Player.look, "Assess your surroundings", "look", 0),
            "name": Command("name", Player.name, "Change your name", "name Doodyhead", 1),
            "say": Command("say", Player.say, "Say something to the current room", "say Hello, I'm a doofhead.", -1),
            "go": Command("go", Player.go, "<north, east, south, west> Go to another room", "go west", 1)
        }

        # Give player a name
        self.name = Player.generate_name()
        room.dungeon.broadcast("<i><font color='green'><+player>%s<-player> has entered the game!</font></i>" % self.name)

        # Output an initial message to the player
        self.output("<i>You awaken into this world as <+player>%s.<-player></i>" % self.name)

        # Spawn in the given room
        self.room = room
        self.room.on_enter(self)

        self.output("<i>Type help to view your list of commands.</i>")

        # Run the networking threads
        self.running_input_thread = threading.Thread(daemon=True, target=lambda: self.input_thread())
        self.running_output_thread = threading.Thread(daemon=True, target=lambda: self.output_thread())
        self.running_input_thread.start()
        self.running_output_thread.start()

    """Updates the player, flushing all inputs and outputs
    Returns nothing
    """
    def update(self):
        # Flush inputs
        while not self.input_stack.empty():
            self.process_input(self.input_stack.get(False))

    """Outputs a string to the player

    string: the string to output to the player
    Returns: nothing
    """
    def output(self, string: str):
        # Send the string to the output stack for the next update
        self.output_stack.put(string, False)

    """Processes an input from this player
    
    string: the string being input
    Returns: nothing
    """
    def input(self, user_input: str):
        # Send the input to the input stack for the next update
        self.input_stack.put(user_input, False)

    def process_input(self, user_input):
        # Check the command
        parameters: list = user_input.split(" ")
        command_name: str = parameters[0]

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

    """
    Adds a new command to the player's command list
    """
    def add_command(self, command: Command):
        # If it doesn't exist, add it to the command dictionary
        if command.name not in self.commands:
            self.commands.append(command)

    """Displays the room entry message, updated with regard to items, players, etc"""
    def look(self, parameters: list):
        self.room.on_player_look(self)

    """Say something to the entire dungeon"""
    def say(self, parameters: list):
        if len(parameters) > 0:
            # Reconstruct the speech text from the parameters
            speech = " ".join(parameters)

            self.room.dungeon.broadcast("<+player>%s<-player> says: <+speech>%s<-speech>" % (self.name, speech))
        else:
            # Teach the user how to talk
            self.output("Usage: say I am beautiful, you are beautiful, we're all beautiful")

    """
    Go to another room in the given direction
    """
    def go(self, parameters: list):
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
    def name(self, parameters: list):
        # Pick a random message to show after changing the name
        name_message = ""
        randomizer = random.randint(0, 3)

        if randomizer == 0:
            name_message = "Actually, " + self.name + "'s real name was " + parameters[0] + " this whole time."
        elif randomizer == 1:
            name_message = "Scratch that. " + self.name + "'s name is " + parameters[0] + " now."
        elif randomizer == 2:
            name_message = self.name + " had us fooled all along, and has revealed their true name, " + parameters[0] + "!"
        elif randomizer == 3:
            name_message = "Wait, " + self.name + " changed their mind. Call them " + parameters[0] + " from now on."

        self.name = parameters[0]
        self.room.dungeon.broadcast("<font color='blue'><b>" + name_message + "</b></font>")

    """
    Show the list of available commands
    """
    def help(self, parameters: list):
        self.output("You can perform the following commands:")

        for command_name, command in self.commands.items():
            self.output("<b><+item>%s:<-item></b> <i>%s</i><br>" % (command_name, command.usage))

    """Generates a player name"""
    @staticmethod
    def generate_name():
        first = ["Engle", "Beef", "Spork", "Glommuck", "Bligg", "Memni", "Qrech", "Zleeph"]
        second = ["bork", "stoph", "strom", "rak", "bibble", "ziggy", "worth", "boid"]
        third = ["Apostra", "Goven", "Rattler", "Yorky", "Pasta", "Hein", "Yerrel", "Peef"]
        fourth = ["glubber", "slipper", "ribbster", "zonky", "drizzle", "blimey"]
        return random.choice(first) + random.choice(second) + " " + random.choice(third) + random.choice(fourth)

    """
    Runs the loop used to receive input from this player
    """
    def input_thread(self):
        while self.is_connected:
            # Get the next message from the player
            try:
                data = self.socket.recv(1024)

                if len(data) > 0:
                    self.input(data.decode("utf-8"))
                else:
                    self.is_connected = False
            except socket.error as error:
                print("Client error, removing client")
                self.is_connected = False

    """Runs the thread used for networked output to this player"""
    def output_thread(self):
        while self.is_connected:
            # Output the current messages to the player, if possible
            try:
                # Send any existing player outputs
                while not self.output_stack.empty():
                    self.socket.send(self.output_stack.get(False).encode())
            except socket.error as error:
                print("Client error, removing client")
                self.is_connected = False

            # Wait a sec
            time.sleep(0.1)
