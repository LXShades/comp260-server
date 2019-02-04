import Room
import threading
import time

"""A player in the game!

Attributes:
    room: current Room that the player is in
"""


class Player:
    """Creates the player in the given room

    Parameters:
        room: the room to spawn in
    """
    def __init__(self, room: Room, is_local: bool = False):
        # Initialise variables
        self.is_local = is_local

        # Initialise player IO
        self.input_stack = []
        self.output_stack = []
        self.io_stack_lock = threading.Lock()

        # Spawn in the given room
        self.room = room
        self.room.on_enter(self)

        # Start IO threads (todo perhaps: move to PlayerController class)
        self.running_input_thread = threading.Thread(daemon=True,
                                                  target=lambda: self.input_thread())
        self.running_output_thread = threading.Thread(daemon=True,
                                                  target=lambda: self.output_thread())
        self.running_input_thread.start()
        self.running_output_thread.start()

        # Output an initial message to the player
        self.output("""
        You have entered the dungeon...
        Type 'help' at any time to see your list of commands. Consider using the 'walk into' command to 'walk into the door'.
        """)
        # very good. now try opening the door and going around it

    """Updates the player, flushing all inputs and outputs
    Returns nothing
    """
    def update(self):
        # Flush inputs
        for input_string in self.input_stack:
            self.process_input(input_string)

        self.input_stack = []

    """Outputs a string to the player

    string: the string to output to the player
    Returns: nothing
    """
    def output(self, string: str):
        # Lock the IO stack
        self.io_stack_lock.acquire()

        try:
            # Send the string to the output stack for the next update
            self.output_stack.append(string)
        finally:
            self.io_stack_lock.release()

    """Processes an input from this player
    
    string: the string being input
    Returns: nothing
    """
    def input(self, user_input: str):
        # Lock the IO stack
        self.io_stack_lock.acquire()

        try:
            # Send the input to the input stack for the next update
            self.input_stack.append(user_input)
        finally:
            self.io_stack_lock.release()

    def process_input(self, user_input):
        # Check the command
        parameters: list = user_input.lower().split(" ")
        command: str = parameters[0]

        # Act based on the command
        # Go to another room
        if command == "go":
            self.go(parameters[1])

    def go(self, direction: str):
        # Try and enter the new room
        new_room = self.room.try_go(direction)

        if new_room is not None:
            # In we go!
            self.room = new_room
            self.output("Entered %d,%d" % (self.room.x, self.room.y))

            new_room.on_enter(self)
        else:
            self.output("You cannot go there!")

    """
    Runs the loop used to supply input/output on this player
    """
    def input_thread(self):
        while True:
            # Get local input from the player
            user_input: str = input("Enter a command\n")

            self.input(user_input)

            # Wait a little for stuff to process
            time.sleep(0.5)

    def output_thread(self):
        while True:
            # Output the current messages to the player, if possible
            self.io_stack_lock.acquire()

            try:
                # Print any existing player outputs
                for output_string in self.output_stack:
                    print(output_string)

                self.output_stack = []
            finally:
                self.io_stack_lock.release()
