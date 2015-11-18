import sys
from obstacle_avoider import ObstacleAvoider

def main(argv):
    avoider = ObstacleAvoider()
    avoider.join()
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv))