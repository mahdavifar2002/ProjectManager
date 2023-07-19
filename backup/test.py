import os
from pathlib import Path

from PySide6.QtCore import QDir, QUrl
from PySide6.QtMultimedia import (
    QMediaCaptureSession,
    QAudioInput,
    QMediaRecorder,
    QMediaFormat,
)
from PySide6.QtWidgets import *


def main():
    app = QApplication([])

    session = QMediaCaptureSession()
    audioInput = QAudioInput()
    session.setAudioInput(audioInput)
    recorder = QMediaRecorder()
    session.setRecorder(recorder)
    recorder.setMediaFormat(QMediaFormat.MP3)
    recorder.setQuality(QMediaRecorder.HighQuality)
    filename = Path(QDir.currentPath()) / "test.mp3"
    url = QUrl.fromLocalFile(os.fspath(filename))
    recorder.setOutputLocation(url)

    startButton = QPushButton("start")
    startButton.clicked.connect(recorder.record)
    stopButton = QPushButton("Stop")
    stopButton.clicked.connect(recorder.stop)

    window = QWidget()
    vbox = QVBoxLayout()
    window.setLayout(vbox)
    vbox.addWidget(startButton)
    vbox.addWidget(stopButton)
    window.show()

    app.exec()


if __name__ == "__main__":
    main()