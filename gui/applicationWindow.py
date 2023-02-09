import numpy
from PyQt6.uic import loadUi
from settings import settings
from capturers import Capture
from PyQt6.QtCore import QTimer
from frameSources import FrameSource
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtWidgets import QLabel, QMainWindow, QPushButton, QSlider



class Window(QMainWindow):
    startButton: QPushButton
    stopButton: QPushButton
    leftEyeThreshold: QSlider
    rightEyeThreshold: QSlider

    def __init__(self, videoSource: FrameSource, capture: Capture):
        super(Window, self).__init__()
        loadUi(settings.guiFilePath, self)
        css = open(settings.styleFilePath, "r")
        self.setStyleSheet(css.read())

        self.startButton.clicked.connect(self.start)
        self.stopButton.clicked.connect(self.stop)
        self.timer = None
        self.videoSource = videoSource
        self.capture = capture

    def start(self):
        self.videoSource.start()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.updateFrame)
        self.timer.start(settings.refreshTime)

    def stop(self):
        self.timer.stop()
        self.videoSource.stop()

    def updateFrame(self):
        frame = self.videoSource.nextFrame()
        face, leftEye, rightEye = self.capture.process(frame, self.leftEyeThreshold.value(), self.rightEyeThreshold.value())
        if face != None:
            self.displayImage(self.opencvToQt(frame))
        if leftEye != None:
            self.displayImage(self.opencvToQt(leftEye), window = "leftEyeBox")
        if rightEye != None:
            self.displayImage(self.opencvToQt(rightEye), window = "rightEyeBox")

    @staticmethod
    def opencvToQt(img) -> QImage:
        qFormat = QImage.Format.Format_Indexed8
        if len(img.shape) == 3:
            if img.shape[2] == 4:
                qFormat = QImage.Format.Format_RGBA8888
            else:
                qFormat = QImage.Format.Format_RGB888
        img = numpy.require(img, numpy.uint8, "C")
        outImage = QImage(img, img.shape[1], img.shape[0], img.strides[0], qFormat)  # BGR to RGB
        outImage = outImage.rgbSwapped()

        return outImage

    def displayImage(self, img: QImage, window="baseImage"):
        displayLabel: QLabel = getattr(self, window, None)
        if displayLabel == None:
            raise ValueError(f"No such display window in GUI: {window}")
        displayLabel.setPixmap(QPixmap.fromImage(img))
        displayLabel.setScaledContents(True)
