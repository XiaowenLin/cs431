import sys
import socket
from frame_client import FrameClient
import cv2
import numpy as np

def main(argv):
    if len(argv) <= 1:
        return 1

    cli = FrameClient(argv[1])
    while True:
        try:
            img = cli.get_frame()
        except socket.error:
            break
        if img is not None:
            cv2.imshow('Remote Image Viewer', img)
        # We MUST call waitKey() for an image window to appear
        k = cv2.waitKey(1) & 0xff
        if k == 27: # Was escape pressed?
            break
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
