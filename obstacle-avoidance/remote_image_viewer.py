import sys
import socket
from frame_client import FrameClient
from ttc_client import TTCClient
import threading
import time
import cv2

def check_returned_value(value):
    return float('inf') if value == 'Infinity' else value

def frame_loop(host):
    global frame_cli
    frame_cli = FrameClient(host)
    while True:
        try:
            img = frame_cli.get_frame()
        except socket.error:
            break
        if img is not None:
            cv2.imshow('Remote Image Viewer', img)
        # We MUST call waitKey() for an image window to appear
        k = cv2.waitKey(1) & 0xff
        if k == 27: # Was escape pressed?
            break

    try:
        frame_cli.shutdown()
    except socket.error:
        pass

    try:
        ttc_cli.shutdown()
    except socket.error:
        pass

    sys.exit(0)

def ttc_loop(host):
    global ttc_cli
    ttc_cli = TTCClient(host)
    while True:
        try:
            ttc_dict = ttc_cli.get_ttc_values()
        except (socket.error, TypeError):
            break
        if ttc_dict is not None:
            print("\033[A\033[K\033[A\033[KMin TTC: %g"%( \
                check_returned_value(ttc_dict['min-ttc'])))
            print("Left TTC: %g, Right TTC: %g"%( \
                check_returned_value(ttc_dict['left-ttc']), \
                check_returned_value(ttc_dict['right-ttc'])))

    try:
        frame_cli.shutdown()
    except socket.error:
        pass

    try:
        ttc_cli.shutdown()
    except socket.error:
        pass

    sys.exit(0)

def main(argv):
    if len(argv) <= 1:
        return 1

    print("\n")

    t1 = threading.Thread(target=frame_loop, args=(argv[1],))
    t2 = threading.Thread(target=ttc_loop, args=(argv[1],))

    t1.daemon = t2.daemon = True
    t1.start()
    t2.start()

    while threading.active_count() > 1:
        time.sleep(0.1)

    return 0

if __name__ == '__main__':
    sys.exit(main(sys.argv))
