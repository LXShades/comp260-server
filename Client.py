import socket
import errno

from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import sys
import threading
import time

'''
The client app. Shows client interface and manages interfacing with the server

Attributes:
    socket: The socket that connects to the server
'''


class Client:
    def __init__(self):
        temp = 200

        print(temp)
        # Create the UI
        self.gui = GUIThread()

        # Create the socket
        self.server_socket = socket.socket()
        self.has_connected = False

        # Begin connection loop
        while self.has_connected == False:
            try:
                # Connect to the server
                self.server_socket.connect(("127.0.0.1", 6282))

                print("Connection successful!")
                self.has_connected = True
            except socket.error as error:
                # Print error (todo: convert to string somehow)
                print("Connection error occured, retrying in 5s")
                time.sleep(5)

        # Begin interface or loop or whatevs


class GUIThread:
    def __init__(self):
        # Startup the app
        self.qt_app = QApplication(sys.argv)

        # Create main window
        self.window = MainWindow()

        # Run GUI thread
        threading.Thread(target=GUIThread.run, args=self)

        # Begin the main loop
        sys.exit(self.qt_app.exec_())

    def run(self):
        while True:
            time.sleep(1)


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

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

    def on_input_enter(self):
        # Echo the player's input
        self.output_box.append("> " + self.input_box.text())

        self.input_box.setText("")
        pass

    def append_output(self, text):
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
        print("Resizing!")



# Run the client! (TEMP)
client = Client()