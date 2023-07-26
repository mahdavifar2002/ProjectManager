import datetime
import os
import uuid
from pathlib import Path
import jdatetime
from model import conf

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
    recorder.setMediaFormat(QMediaFormat.FileFormat.MP3)
    recorder.setQuality(QMediaRecorder.Quality.HighQuality)
    filename = conf.generate_filename("mahdavifar", "mp3")
    filepath = Path(QDir.toNativeSeparators("//alireza/E/ProjectManager/Files/Voices")) / filename
    url = QUrl.fromLocalFile(os.fspath(filepath))
    recorder.setOutputLocation(url)
    recorder.record()

    button = QPushButton("Stop")
    button.show()
    button.clicked.connect(recorder.stop)

    app.exec()


if __name__ == "__main__":
    main()
