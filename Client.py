import socket
import sys
import threading
import time
import queue

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *

from Global import Global

'''
The client app. Shows client interface and manages interfacing with the server

Attributes:
    socket: The socket that connects to the server
'''


class Client:
    # This is set to false if the client is spawned as a thread by the server
    is_independent = True

    """Initialises the client app thread and all sub-threads"""
    def __init__(self):
        # Create the UI
        self.gui = GUIThread(self)

        # Init vars
        self.server_socket = None
        self.has_connected = False
        self.is_closing = False

        # Setup queues
        self.input_queue = queue.Queue()
        self.output_queue = queue.Queue()

        # Begin connection loop
        while self.has_connected is False and self.is_closing is False:
            try:
                # Connect to the server
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.connect(("127.0.0.1", 6282))

                self.push_output("Connection successful!")
                self.has_connected = True
            except socket.error as error:
                # Print error (todo: convert to string somehow)
                self.push_output("Connection error occurred, retrying in 5s (" + str(error) + ")")
                time.sleep(5)

            if self.has_connected:
                # Startup the send and receive threads
                threading.Thread(target=Client.send_thread, args=(self,), daemon=True).start()
                threading.Thread(target=Client.recv_thread, args=(self,), daemon=True).start()

                while self.has_connected is True and self.is_closing is False:
                    time.sleep(0.1)

    def send_thread(self):
        while self.has_connected:
            while not self.input_queue.empty():
                input: str = self.input_queue.get(False)
                input_as_bytes: bytes = input.encode()

                try:
                    # Send all unsent inputs to the server
                    self.server_socket.send(input_as_bytes)
                except socket.error as error:
                    self.push_output("You have been disconnected from the server due to <i>active reasons</i>.")
                    self.push_output(str(error))
                    self.has_connected = False

            time.sleep(0.1)

    def recv_thread(self):
        # Show all messages received from the server
        while self.has_connected:
            try:
                data = self.server_socket.recv(1024)

                if len(data) > 0:
                    self.push_output(data.decode("utf-8"))
                else:
                    self.has_connected = False
            except socket.error as error:
                self.push_output("You have been disconnected from the server due to <i>passive reasons</i>.")
                self.push_output(str(error))
                self.has_connected = False

            time.sleep(0.1)

    """Pushes a player input to the queue, to be sent to the server"""
    def push_input(self, text):
        self.input_queue.put(text, False)

    def push_output(self, text):
        self.output_queue.put(text, False)

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
        self.window = MainWindow(self.client)

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
class MainWindow(QWidget):
    custom_formatting_spec = [
        "player", "<font color='orange'>", "</font>",
        "item", "<font color='lightblue'>", "</font>",
        "room", "<font color='yellow'>", "</font>",
        "command", "<font color='yellow'>", "</font>",
        "input", "<font color='#508050'>", "</font>"
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

        # Input enter button
        self.enter_button = QPushButton("Enter", self)
        self.enter_button_width = 80
        self.enter_button.clicked.connect(self.on_input_enter)

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
        self.main_loop.start(100)

    def on_tick(self):
        # Grab outputs from client and paste onto output box
        while not self.client.output_queue.empty():
            self.output(self.client.output_queue.get(False))

    def on_input_enter(self):
        # Echo the player's input
        self.output("<+input>> " + self.input_box.text() + "<-input><br>")

        # Send the input to the client class
        self.client.push_input(self.input_box.text())

        # Empty the text box
        self.input_box.setText("")

    def output(self, text: str):
        # Format the custom HTML tags
        for f in range(0, len(MainWindow.custom_formatting_spec), 3):
            # Replace the opening tag
            text = text.replace("<+" + MainWindow.custom_formatting_spec[f] + ">", MainWindow.custom_formatting_spec[f + 1])

            # Replace the closing tag
            text = text.replace("<-" + MainWindow.custom_formatting_spec[f] + ">", MainWindow.custom_formatting_spec[f + 2])

        # Append HTML to the text. This is a hack because text is only randomly interpreted as HMTL otherwise
        self.output_box.append("<a></a>" + text + "<br>")

    def keyPressEvent(self, event):
        # Handle the Enter key as equivalent to clicking Enter button
        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            self.on_input_enter()

    def resizeEvent(self, event: QResizeEvent):
        super().resizeEvent(event)

        # Resize child controls to fit the window
        width = self.geometry().width()
        height = self.geometry().height()

        # Resize all controls
        self.output_box.move(5, 5)
        self.output_box.resize(width - 10, height - self.input_height - 15)
        self.enter_button.move(width - self.enter_button_width - 5, height - self.input_height - 5)
        self.input_box.move(5, height - self.input_height - 5)
        self.input_box.resize(width - self.enter_button_width - 10, self.input_height)


# Start the client if it's not being created by the server
if Global.is_server is False:
    Client()
