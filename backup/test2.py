#!/usr/bin/python

# Fetch More Example
# Ported to PyQt4 by Darryl Wallace, 2009 - wallacdj@gmail.com

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

class FileListModel(QAbstractListModel):
    numberPopulated = Signal(int)

    def __init__(self, parent=None):
        super(FileListModel, self).__init__(parent)

        self.fileCount = 0
        self.fileList = []

    def rowCount(self, parent=QModelIndex()):
        return self.fileCount

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if index.row() >= len(self.fileList) or index.row() < 0:
            return None

        if role == Qt.ItemDataRole.DisplayRole:
            return self.fileList[index.row()]

        if role == Qt.ItemDataRole.BackgroundRole:
            batch = (index.row() // 100) % 2
            if batch == 0:
                return qApp.palette().base()

            return qApp.palette().alternateBase()

        return None

    def canFetchMore(self, index):
        return self.fileCount < len(self.fileList)

    def fetchMore(self, index):
        remainder = len(self.fileList) - self.fileCount
        itemsToFetch = min(100, remainder)

        self.beginInsertRows(QModelIndex(), self.fileCount,
                self.fileCount + itemsToFetch)

        self.fileCount += itemsToFetch

        self.endInsertRows()

        self.numberPopulated.emit(itemsToFetch)

    def setDirPath(self, path):
        dir = QDir(path)

        self.fileList = list(dir.entryList())
        self.fileCount = 0
        # self.reset()


class Window(QWidget):
    def __init__(self, parent=None):
        super(Window, self).__init__(parent)

        model = FileListModel(self)
        model.setDirPath(QLibraryInfo.location(QLibraryInfo.PrefixPath))

        label = QLabel("Directory")
        lineEdit = QLineEdit()
        label.setBuddy(lineEdit)

        view = QListView()
        view.setModel(model)

        self.logViewer = QTextBrowser()
        self.logViewer.setSizePolicy(QSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred))

        lineEdit.textChanged.connect(model.setDirPath)
        lineEdit.textChanged.connect(self.logViewer.clear)
        model.numberPopulated.connect(self.updateLog)

        layout = QGridLayout()
        layout.addWidget(label, 0, 0)
        layout.addWidget(lineEdit, 0, 1)
        layout.addWidget(view, 1, 0, 1, 2)
        layout.addWidget(self.logViewer, 2, 0, 1, 2)

        self.setLayout(layout)
        self.setWindowTitle("Fetch More Example")

    def updateLog(self, number):
        self.logViewer.append("%d items added." % number)


if __name__ == '__main__':

    import sys

    app = QApplication(sys.argv)

    window = Window()
    window.show()

    sys.exit(app.exec_())