from camera import Camera
import cv2

class GenericCameraIterator:
    def __init__(self, cap):
        self.cap = cap
        
    def __iter__(self):
        return self
    
    # Iterate and grab frames indefinitely
    def next(self):
        _, frame = self.cap.read()
        return frame

class GenericCamera(Camera):
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
    
    def get_iterator(self):
        return GenericCameraIterator(self.cap)
    
    def get_frame(self, raw_frame):
        return raw_frame
    
    def destroy(self):
        self.cap.release()