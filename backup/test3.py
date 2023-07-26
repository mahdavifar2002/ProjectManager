import os
from pathlib import Path

from PySide6.QtCore import QDir, QUrl
from PySide6.QtMultimedia import (
    QMediaCaptureSession,
    QAudioInput,
    QMediaRecorder,
    QMediaFormat,
)
from PySide6.QtWidgets import QApplication, QPushButton


def main():
    app = QApplication([])

    session = QMediaCaptureSession()
    audioInput = QAudioInput()
    session.setAudioInput(audioInput)
    recorder = QMediaRecorder()
    session.setRecorder(recorder)
    recorder.setMediaFormat(QMediaFormat.MP3)
    recorder.setQuality(QMediaRecorder.HighQuality)
    filename = Path(QDir.toNativeSeparators("//khakbaz/E/ProjectManager/Files/Voices")) / "test.mp3"
    print(filename)
    url = QUrl.fromLocalFile(os.fspath(filename))
    recorder.setOutputLocation(url)
    recorder.record()

    button = QPushButton("Stop")
    button.show()
    button.clicked.connect(recorder.stop)

    app.exec()


if __name__ == "__main__":
    main()
