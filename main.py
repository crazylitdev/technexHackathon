import sys
from PyQt6.QtWidgets import QApplication
from gui.applicationWindow import Window
from frameSources import CameraFrameSource
from capturers.haarBlob import HaarCascadeBlobCapture


if __name__ == "__main__":
    capture = HaarCascadeBlobCapture()
    app = QApplication(sys.argv)
    window = Window(capture, CameraFrameSource())
    window.setWindowTitle("Eye Ball Tracking")
    window.show()
    sys.exit(app.exec())
