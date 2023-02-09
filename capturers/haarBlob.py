import numpy
import logging
from cv2 import cv2
from typing import Optional
from settings import settings
from cv2.data import haarcascades


logger = logging.getLogger(__name__)


class CV2Error(Exception):
    pass


class HaarCascadeBlobCapture:

    def __init__(self):
        self.previousLeftBlobArea = 1
        self.previouRightBlobArea = 1
        self.previousLeftKeypoints = None
        self.previousRightKeypoints = None

        self.faceDetector = cv2.CascadeClassifier(haarcascades + "haarcascade_frontalface_default.xml")
        self.eyeDetector = cv2.CascadeClassifier(haarcascades + "haarcascade_eye.xml")
        self.blobDetector = None

    def initBlobDetector(self):
        detectorParams = cv2.SimpleBlobDetector_Params()
        detectorParams.filterByArea = True
        detectorParams.maxArea = 1500
        self.blobDetector = cv2.SimpleBlobDetector_create(detectorParams)

    def detectFace(self, image: numpy.ndarray) -> Optional[numpy.ndarray]:
        coords = self.faceDetector.detectMultiScale(image, 1.3, 5)
        if len(coords) > 1:
            biggest = (0, 0, 0, 0)
            for i in coords:
                if i[3] > biggest[3]:
                    biggest = i
            biggest = numpy.array([i], numpy.int32)
        elif len(coords) == 1:
            biggest = coords
        else:
            return None
        for (x, y, w, h) in biggest:
            frame = image[y : y + h, x : x + w]
            return frame

    @staticmethod
    def cutEyebrows(image):
        if image is None:
            return image
        height, width = image.shape[:2]
        image = image[15:height, 0:width]
        return image

    def detectEyes(self, faceImg: numpy.ndarray, cutBrows = True) -> None:
        coords = self.eyeDetector.detectMultiScale(faceImg, 1.3, 5)
        leftEye = rightEye = None
        if coords is None or len(coords) == 0:
            return leftEye, rightEye
        for (x, y, w, h) in coords:
            eyeCenter = int(float(x) + (float(w) / float(2)))
            if int(faceImg.shape[0] * 0.1) < eyeCenter < int(faceImg.shape[1] * 0.4):
                leftEye = faceImg[y : y + h, x : x + w]
            elif int(faceImg.shape[0] * 0.5) < eyeCenter < int(faceImg.shape[1] * 0.9):
                rightEye = faceImg[y : y + h, x : x + w]
            else:
                pass
            if cutBrows:
                return self.cutEyebrows(leftEye), self.cutEyebrows(rightEye)
            return leftEye, rightEye

    def blobTrack(self, image, threshold, prevArea):
        _, image = cv2.threshold(image, threshold, 255, cv2.THRESH_BINARY)
        image = cv2.erode(image, None, iterations = 2)
        image = cv2.dilate(image, None, iterations = 4)
        image = cv2.medianBlur(image, 5)
        keypoints = self.blobDetector.detect(image)
        if keypoints and len(keypoints) > 1:
            tmp = 1000
            for keypoint in keypoints:  # filter out odd blobs
                if abs(keypoint.size - prevArea) < tmp:
                    ans = keypoint
                    tmp = abs(keypoint.size - prevArea)

            keypoints = (ans,)
        return keypoints

    def draw(self, source, keypoints, dest = None):
        try:
            if dest is None:
                dest = source
            return cv2.drawKeypoints(
                source,
                keypoints,
                dest,
                (0, 0, 255),
                cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
            )
        except cv2.error as e:
            raise CV2Error(str(e))

    def debugDump(self, frame):
        cv2.imwrite(str(settings.debugDataLocation / f"{id(frame)}.png"), frame)

    def process(self, frame: numpy.ndarray, leftThreshold, rightThreshold):
        if not self.blobDetector:
            self.initBlobDetector()
        try:
            face = self.detectFace(frame)
            if face is None:
                return frame, None, None
            faceGray = cv2.cvtColor(face, cv2.COLOR_RGB2GRAY)
            leftEye, rightEye = self.detectEyes(faceGray)
            if leftEye is not None:
                leftKeyPoints = self.blobTrack(leftEye, leftThreshold, self.previousLeftBlobArea)
                kp = leftKeyPoints or self.previousLeftKeypoints
                leftEye = self.draw(leftEye, kp, frame)
                self.previousLeftKeypoints = kp
            if rightEye is not None:
                rightKeyPoints = self.blobTrack(rightEye, rightThreshold, self.previouRightBlobArea)
                kp = rightKeyPoints or self.previousRightKeypoints
                rightEye = self.draw(rightEye, kp, frame)
                self.previousRightKeypoints = kp
            return frame, leftEye, rightEye
        except (cv2.error, CV2Error) as e:
            logger.error("error occurred: %s", str(e))
            logger.error(f"Thresholds: left: {leftThreshold}, right: {rightThreshold}")
            if settings.debugData:
                self.debugDump(frame)
            raise
