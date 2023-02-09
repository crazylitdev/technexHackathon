import numpy
from typing import Protocol


class Capture(Protocol):
    def detectEyes(self):
        ...

    def detectFace(self):
        ...

    def process(self, frame: numpy.ndarray, threshold: int):
        ...
