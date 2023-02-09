from typing import Protocol

from .camera import FrameSource as CameraFrameSource
from .file import FrameSource as FileFrameSource
from .folder import FrameSource as FolderFrameSource
from .video import FrameSource as VideoFrameSource


class FrameSource(Protocol):
    pass
