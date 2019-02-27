import socket
import sys
import threading
import time
import queue
import re

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from Global import Global

"""
The client app. Shows client interface and manages interfacing with the server

Attributes:
    is_independent (class attribute): Whether the client is being run independently, or is being spawned as a 
                                      thread for testing on the server
    server_socket: The socket that connects to the server
    is_connected: Whether the server is connected
    is_closing: Whether the client UI is being closed
    input_queue: A queue of inputs from the UI
    output_queue: A queue of outputs to be read by the UI
"""
class Client:
    # This is set to false if the client is spawned as a thread by the server
    is_independent = True

    """Initialises the client app thread and all sub-threads"""
    def __init__(self):
        # Create the UI
        self.gui = GUIThread(self)

        # Init vars
        self.server_socket = None
        self.is_connected = False
        self.is_closing = False

        # Setup queues
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

        # Run the client!
        self.run()

    """Runs the main loop. Handles client connection and disconnection until the app is closed"""
    def run(self):
        # Begin connection loop
        while self.is_connected is False and self.is_closing is False:
            try:
                # Connect to the server
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.connect(("127.0.0.1", 6282))

                self.push_output("Connection successful!")
                self.is_connected = True
            except socket.error as error:
                # Print error (todo: convert to string somehow)
                self.push_output("Connection error occurred, retrying in 5s (" + str(error) + ")")
                time.sleep(5)

            if self.is_connected:
                # Startup the send and receive threads
                threading.Thread(target=Client.send_thread, args=(self,), daemon=True).start()
                threading.Thread(target=Client.recv_thread, args=(self,), daemon=True).start()

                while self.is_connected is True and self.is_closing is False:
                    time.sleep(1.0)

    """Sends outstanding player inputs while connected"""
    def send_thread(self):
        while self.is_connected:
            while not self.input_queue.empty():
                input: str = self.input_queue.get(False)
                input_as_bytes: bytes = input.encode()

                try:
                    # Send all unsent inputs to the server
                    self.server_socket.send(input_as_bytes)
                except socket.error as error:
                    self.push_output("You have been disconnected from the server due to <i>active reasons</i>.")
                    self.push_output(str(error))
                    self.is_connected = False

            time.sleep(0.1)

    """Receives player outputs from the server while connected"""
    def recv_thread(self):
        # Show all messages received from the server
        while self.is_connected:
            try:
                data = self.server_socket.recv(1024)

                if len(data) > 0:
                    self.push_output(data.decode("utf-8"))
                else:
                    self.is_connected = False
            except socket.error as error:
                self.push_output("You have been disconnected from the server due to <i>passive reasons</i>.")
                self.push_output(str(error))
                self.is_connected = False

            time.sleep(0.1)

    """Pushes a player input to the queue, to be sent to the server
    
    Attributes:
        text: the text to send 
    """
    def push_input(self, text: str):
        self.input_queue.put(text, False)

    """Pushes a player output to the queue, to be read by the GUI thread
    
    Attributes:
        text: the text received from the server to be output to the player
    """
    def push_output(self, text: str):
        self.output_queue.put(text, False)

    """Called when the app window is closed"""
    def on_gui_close(self):
        self.is_closing = True


class GUIThread:
    def __init__(self, client: Client):
        self.client = client

        # Run GUI thread
        threading.Thread(target=GUIThread.run, args=(self,), daemon=True).start()

    def run(self):
        # Startup the app
        self.qt_app = QApplication(sys.argv)

        # Create main window
        self.window = ClientWindow(self.client)

        # Begin the main loop
        self.qt_app.exec_()

        # The program has ended
        self.client.on_gui_close()


"""
The main window for the client.

Attributes:
    custom_formatting_spec: A list of custom HTML tags followed by their replacement opening tag and closing tag,
                            respectively.
"""
class ClientWindow(QWidget):
    custom_formatting_spec = [
        "player", "<font color='orange'>", "</font>",
        "item", "<font color='lightblue'>", "</font>",
        "room", "<font color='yellow'>", "</font>",
        "command", "<font color='yellow'>", "</font>",
        "input", "<font color='#508050'>", "</font>",
        "action", "<font color='yellow'><i>", "</i></font>",
        "event", "<font color='white'><i>", "</i></font>",
        "info", "<i>", "</i>",
    ]

    def __init__(self, client: Client):
        super().__init__()

        # Assign the main client reference
        self.client = client

        # Setup the window title and dimensions
        self.title = "MUDdy Beach Cafe"
        self.top = 100
        self.left = 100
        self.width = 640
        self.height = 480

        # Create the fonts
        default_font = QFont("Times", 13, QFont.DemiBold)
        self.setFont(default_font)
        self.setStyleSheet("""
            QWidget {background-color: #111e31; color: #afab9b;}
            """)

        # Setup controls
        # Game text output
        self.output_box = QTextEdit(self)
        self.output_box.setReadOnly(True)

        # Room title box
        self.room_title = QTextEdit(self)
        self.room_title.setText("Room")
        self.room_title.setReadOnly(True)

        # Room info box
        self.room_info = QTextEdit(self)
        self.room_info.setReadOnly(True)

        # Input enter button
        self.enter_button = QPushButton("Enter", self)
        self.enter_button_width = 80
        self.enter_button.clicked.connect(self.on_input_entered)

        # Input box
        self.input_box = QLineEdit(self)
        self.input_height = 20

        # Setup window
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

        # Setup I/O event loop
        self.main_loop = QTimer()
        self.main_loop.timeout.connect(self.on_tick)
        self.main_loop.start(50)

    """Called every timer tick"""
    def on_tick(self):
        # Grab outputs from client and paste onto output box
        while not self.client.output_queue.empty():
            self.output(self.client.output_queue.get(False))

    """Called when the return key is pressed, or the Enter button clicked"""
    def on_input_entered(self):
        # Echo the player's input
        self.output("<+input>&gt; " + self.input_box.text() + "<-input><br>")

        # Send the input to the client class
        self.client.push_input(self.input_box.text())

        # Empty the text box
        self.input_box.setText("")

    """Outputs text to the screen. Should not be called externally. Use client.push_output instead
    
    Attributes:
        text: Text to output"""
    def output(self, text: str):
        # Format the custom HTML tags
        for f in range(0, len(ClientWindow.custom_formatting_spec), 3):
            # Replace the opening tag
            text = text.replace("<+" + ClientWindow.custom_formatting_spec[f] + ">", ClientWindow.custom_formatting_spec[f + 1])

            # Replace the closing tag
            text = text.replace("<-" + ClientWindow.custom_formatting_spec[f] + ">", ClientWindow.custom_formatting_spec[f + 2])

        # Process additional custom HTML tags for targeting other widgets
        custom_ui_targets = ["<+room_title>", "<-room_title>", self.room_title,
                             "<+room_info>", "<-room_info>", self.room_info]

        for f in range(0, len(custom_ui_targets), 3):
            tag_start = text.find(custom_ui_targets[f])
            tag_end = text.find(custom_ui_targets[f + 1])

            if tag_start is not -1 and tag_end is not -1:
                # Place the tagged text into the appropriate widget
                custom_ui_targets[f + 2].setText(text[tag_start + len(custom_ui_targets[f]):tag_end])

                # Strip this tag out of the text output
                text = text[0:tag_start] + text[tag_end + len(custom_ui_targets[f + 1]):]

        # Present the output only if there's some plaintext output available
        if ClientWindow.html_text_is_readable(text):
            # Append HTML to the text. This is a hack, because text is not guaranteed to be interpreted as HTML otherwise...
            self.output_box.append("<a></a>" + text)

    """Returns: Whether an HTML text has non-whitespace, human-readable characters"""
    @staticmethod
    def html_text_is_readable(text: str):
        return len(re.sub('<[^<]+?>', '', text)) > 0

    """Called by Qt when a key is pressed"""
    def keyPressEvent(self, event):
        # Handle the Enter key as equivalent to clicking Enter button
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.on_input_entered()

    """Called by Qt when the window is resized"""
    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)

        # Resize child controls to fit the window
        width = self.geometry().width()
        height = self.geometry().height()

        output_box_width = int(width * 0.7)
        room_title_height = 30

        # Resize all controls
        self.room_title.move(output_box_width + 5, 5)
        self.room_title.resize(width - output_box_width - 10, room_title_height)
        self.output_box.move(5, 5)
        self.output_box.resize(output_box_width - 5, height - self.input_height - 15)
        self.enter_button.move(width - self.enter_button_width - 5, height - self.input_height - 5)
        self.enter_button.resize(self.enter_button_width, self.input_height)
        self.input_box.move(5, height - self.input_height - 5)
        self.input_box.resize(width - self.enter_button_width - 10, self.input_height)
        self.room_info.move(output_box_width + 5, room_title_height + 10)
        self.room_info.resize(width - output_box_width - 10, height - self.input_height - room_title_height - 20)


# Start the client if it's not being created by the server
if Global.is_server is False:
    Client()
