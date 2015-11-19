import sys
from obstacle_avoider import ObstacleAvoider
import threading
import time

def imgdisp(cv2, img):
    cv2.imshow('frame', img)

def min_ttc(the_min_ttc):
    print("\033[A\033[K\033[A\033[KMin TTC: %g"%(the_min_ttc))

def balance_strategy(left_ttc, right_ttc):
    print("Left TTC: %g, Right TTC: %g"%(left_ttc, right_ttc))

def main(argv):
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
