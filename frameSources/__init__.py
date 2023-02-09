from typing import Protocol
from .camera import FrameSource as CameraFrameSource


class FrameSource(Protocol):

    def nextFrame(self):
        ...

    def start(self):
        ...

    def stop(self):
        ...