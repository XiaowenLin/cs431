import sys
import socket
from frame_client import FrameClient
from ttc_client import TTCClient
import threading
import cv2

def frame_loop():
    frame_cli = FrameClient(argv[1])
    while True:
        try:
            img = frame_cli.get_frame()
        except socket.error:
            sys.exit(0)
        if img is not None:
            cv2.imshow('Remote Image Viewer', img)
        # We MUST call waitKey() for an image window to appear
        k = cv2.waitKey(1) & 0xff
        if k == 27: # Was escape pressed?
            sys.exit(0)

def ttc_loop():
    ttc_cli = TTCClient(argv[1])
    while True:
        try:
            min_ttc, left_ttc, right_ttc = ttc_cli.get_ttc_values()
        except (socket.error, TypeError):
            sys.exit(0)
        print("\033[A\033[KMin TTC: %g"%(min_ttc))
        print("Left TTC: %g, Right TTC: %g"%(left_ttc, right_ttc))

def main(argv):
    if len(argv) <= 1:
        return 1

    print("\n")

    t1 = threading.Thread(target=frame_loop)
    t2 = threading.Thread(target=ttc_loop)

    t1.daemon = t2.daemon = True
    t1.start()
    t2.start()

    while threading.active_count() > 1:
        time.sleep(0.1)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
