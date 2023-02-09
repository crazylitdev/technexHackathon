import sys
import argparse
from frameSources import (
    FileFrameSource,
    VideoFrameSource,
    FolderFrameSource,
    CameraFrameSource
)
from PyQt6.QtWidgets import QApplication
from gui.applicationWindow import Window
from capturers.haarBlob import HaarCascadeBlobCapture


frameSources = {
    "file": FileFrameSource,
    "video": VideoFrameSource,
    "folder": FolderFrameSource,
    "camera": CameraFrameSource
}


def getArgs():
    parser = argparse.ArgumentParser()
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = getArgs()
    frameSource = frameSources[args.frameSource]
    frameSourceKwargs = {}
    if args.cameraId and args.frameSource == "camera":
        frameSourceKwargs["cameraId"] = args.cameraId
    capture = HaarCascadeBlobCapture()
    app = QApplication(sys.argv)
    window = Window(frameSource(**frameSourceKwargs), capture)
    window.setWindowTitle("Eye Ball Tracking")
    window.show()
    sys.exit(app.exec())
