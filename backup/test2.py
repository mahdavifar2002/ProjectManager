# Import necessary modules
import sys
from PySide6.QtWidgets import *
from PySide6.QtCore import *

# Define class to create the stop watch
class StopWatchWindow(QMainWindow):

    def __init__(self):
        # Call the parent constructor
        super().__init__()

        # Set the title of the window
        self.setWindowTitle("Stop Watch using QTimer")
        # Set the geometry for the window
        self.setGeometry(100, 100, 300, 200)

        # Set the necessary variables
        self.counter = 0
        self.minute = '00'
        self.second = '00'
        self.count = '00'
        self.startWatch = False

        # Create label to display the watch
        self.label = QLabel(self)
        # Set geometry for the label
        self.label.setGeometry(100, 40, 150, 70)


        # Create start button
        self.start = QPushButton("Start", self)
        # Set geometry to the start button
        self.start.setGeometry(50, 120, 100, 40)
        # Call start() method when the start button is clicked
        self.start.pressed.connect(self.Start)

        # Create reset button
        resetWatch = QPushButton("Reset", self)
        # Set geometry to the stop button
        resetWatch.setGeometry(160, 120, 100, 40)
        # Call reset() method when the reset button is clicked
        resetWatch.pressed.connect(self.Reset)


        # Create timer object
        timer = QTimer(self)
        # Add a method with the timer
        timer.timeout.connect(self.showCounter)
        # Call start() method to modify the timer value
        timer.start(100)

        # Move the position of the window
        self.move(900, 400)
        # Display the window
        self.show()

    # Define a method to modify the values of minutes and seconds based on the timer value
    def showCounter(self):
        # Check the value of startWatch  variable to start or stop the Stop Watch
        if self.startWatch:
            # Increment counter by 1
            self.counter += 1

            # Count and set the time counter value
            cnt = int((self.counter/10 - int(self.counter/10))*10)
            self.count = '0' + str(cnt)

            # Set the second value
            if int(self.counter/10) < 10 :
                self.second = '0' + str(int(self.counter / 10))
            else:
                self.second = str(int(self.counter / 10))
                # Set the minute value
                if self.counter / 10 == 60.0 :
                    self.second == '00'
                    self.counter = 0
                    min = int(self.minute) + 1
                    if min < 10 :
                        self.minute = '0' + str(min)
                    else:
                        self.minute = str(min)


        # Merge the mintue, second and count values
        text = self.minute + ':' + self.second + ':' + self.count
        # Display the stop watch values in the label
        self.label.setText('<h1 style="color:blue">' + text + '</h1>')

    # Define method to handle the start button
    def Start(self):
        # Set the caption of the start button based on previous caption
        if self.start.text() == 'Stop':
            self.start.setText('Resume')
            self.startWatch = False
        else:
            # making startWatch to true
            self.startWatch = True
            self.start.setText('Stop')

    # Define method to handle the reset button
    def Reset(self):
        self.startWatch = False
        # Reset all counter variables
        self.counter = 0
        self.minute = '00'
        self.second = '00'
        self.count = '00'
        # Set the initial values for the stop watch
        self.label.setText(str(self.counter))

# Create app object and run the app
app = QApplication(sys.argv)
stopWt = StopWatchWindow()
app.exec()