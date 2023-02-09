from cv2 import cv2


class FrameSource:

    def __init__(self, cameraId = None):
        self.cameraIsRunning = False
        self.cameraId = cameraId
        self.capture = None

    def checkCamera(self):
        return self.capture is not None and self.capture.read()[0]

    def start(self):
        if self.cameraIsRunning:
            return
        if self.cameraId is not None:
            self.capture = cv2.VideoCapture(self.cameraId)
            if not self.checkCamera():
                raise SystemError(f"Camera with id = {self.cameraId} is not working.")
            self.cameraIsRunning = True
            return
        for cameraDeviceIndex in range(0, 5000, 100):
                self.capture = cv2.VideoCapture(cameraDeviceIndex)
                if self.checkCamera():
                    self.cameraIsRunning = True
                    return
        raise SystemError("Camera device not found.")

    def stop(self):
        if self.cameraIsRunning:
            self.capture.release()
            self.cameraIsRunning = False

    def nextFrame(self):
        assert self.cameraIsRunning, "First start the camera."
        success, frame = self.capture.read()
        if not success:
            raise SystemError("Frame couldn't be captured.")
        return frame