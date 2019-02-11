import socket
import errno

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import threading
import time
import queue

'''
The client app. Shows client interface and manages interfacing with the server

Attributes:
    socket: The socket that connects to the server
'''


class Client:
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
                # Startup the send thread!
                threading.Thread(target=Client.send_thread, args=(self,), daemon=True).start()

                while self.has_connected is True and self.is_closing is False:
                    time.sleep(0.1)

    def send_thread(self):
        while True:
            while not self.input_queue.empty():
                input_as_bytes: bytes = self.input_queue.get(False).encode()

                try:
                    # Send all unsent inputs to the server
                    self.server_socket.send(input_as_bytes)
                    self.push_output("sent, yay")
                except socket.error as error:
                    self.push_output("You have been disconnected from the server due to reasons.")
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


class MainWindow(QWidget):
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

        # Setup controls
        # Game text output
        self.output_box = QTextEdit(self)

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
        self.output_box.append("> " + self.input_box.text())

        # Send the input to the client class
        self.client.push_input(self.input_box.text())

        # Empty the text box
        self.input_box.setText("")

    def output(self, text):
        self.output_box.append(text)

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

# Run the client! (TEMP)
client = Client()