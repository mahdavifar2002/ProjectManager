from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *
import sys

#############Define MyWindow Class Here ############
class MyWindow(QMainWindow):
##-----------------------------------------
  def __init__(self):
    QMainWindow.__init__(self)
    self.label = QLabel("No data")
    self.label.setGeometry(100, 200, 100, 100)
    self.setCentralWidget(self.label)
    self.setWindowTitle("QMainWindow WheelEvent")
    self.x = 0
##-----------------------------------------
  def wheelEvent(self,event):
    self.x =self.x + event.delta()/120
    print(self.x)
    self.label.setText("Total Steps: "+QString.number(self.x))
##-----------------------------------------
##########End of Class Definition ##################


def main():
  app = QApplication(sys.argv)
  window = MyWindow()
  window.show()
  return app.exec_()

if __name__ == '__main__':
 main()