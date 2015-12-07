import sys
from obstacle_avoider import ObstacleAvoider
from frame_server import FrameServer
import threading
import time

def imgdisp(cv2, img):
#    cv2.imshow('frame', img)
    frame_server.set_frame(img)

def min_ttc(the_min_ttc):
    print("\033[A\033[K\033[A\033[KMin TTC: %g"%(the_min_ttc))
    sys.stdout.flush()

def balance_strategy(left_ttc, right_ttc):
    print("Left TTC: %g, Right TTC: %g"%(left_ttc, right_ttc))
    sys.stdout.flush()

def main(argv):
    global frame_server
    frame_server = FrameServer()
    frame_server.run_daemon_thread()
    avoider = ObstacleAvoider()
    avoider.set_imgdisp_cb(imgdisp)
    avoider.set_balance_strategy_cb(balance_strategy)
    avoider.set_min_ttc_cb(min_ttc)
    print("\n")
    avoider.start()
    while threading.active_count() > 1:
        time.sleep(0.1)
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))
