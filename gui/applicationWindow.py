import numpy
from PyQt6.uic import loadUi
from settings import settings
from capturers import Capture
from PyQt6.QtCore import QTimer
from typing_extensions import Self
from frameSources import FrameSource
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QMainWindow, QPushButton, QSlider



class Window(QMainWindow):


    def __init__(self, capture: Capture, videoSource: FrameSource) -> None:
        super(Window, self).__init__()
        loadUi(settings.guiFilePath, self)
        css = open(settings.styleFilePath, "r")
        self.setStyleSheet(css.read())

        self.timer = None
        self.capture = capture
        self.videoSource = videoSource

        self.startButton: QPushButton
        self.stopButton: QPushButton
        self.leftEyeThreshold: QSlider
        self.rightEyeThreshold: QSlider

        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)

    def start(self: Self) -> None:
        self.videoSource.start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(settings.refreshTime)

    def stop(self: Self):
        self.timer.stop()
        self.videoSource.stop()

    def updateFrame(self: Self):
        frame = self.videoSource.nextFrame()
        face, leftEye, rightEye = self.capture.process(frame, self.leftEyeThreshold.value(), self.rightEyeThreshold.value())
        if face is not None:
            self.displayImage(self.opencvToQt(frame))
        if leftEye is not None:
            self.displayImage(self.opencvToQt(leftEye), window = "leftEyeBox")
        if rightEye is not None:
            self.displayImage(self.opencvToQt(rightEye), window = "rightEyeBox")

    @staticmethod
    def opencvToQt(image) -> QImage:
        qFormat = QImage.Format.Format_Indexed8
        if len(image.shape) == 3:
            if image.shape[2] == 4:
                qFormat = QImage.Format.Format_RGBA8888
            else:
                qFormat = QImage.Format.Format_RGB888
        image = numpy.require(image, numpy.uint8, "C")
        outImage = QImage(image, image.shape[1], image.shape[0], image.strides[0], qFormat)  # BGR to RGB
        outImage = outImage.rgbSwapped()
        return outImage

    def displayImage(self, image: QImage, window = "baseImage"):
        displayLabel: QLabel = getattr(self, window, None)
        if displayLabel is None:
            raise ValueError(f"Invalid display window: {window}")
        displayLabel.setPixmap(QPixmap.fromImage(image))
        displayLabel.setScaledContents(True)