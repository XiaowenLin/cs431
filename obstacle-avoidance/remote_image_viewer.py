import sys
from frame_client import FrameClient
from socket_util import SocketUtil
import cv2
import numpy as np

def main(argv):
    if len(argv) <= 1:
        return 1

    cli = FrameClient(argv[1])
    while True:
        cv2.imshow('Remote Image Viewer', \
            SocketUtil.get_image_from_raw_buffer(cli.get_frame()))
        # We MUST call waitKey() for an image window to appear
        k = cv2.waitKey(1) & 0xff
        if k == 27: # Was escape pressed?
            break
    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
