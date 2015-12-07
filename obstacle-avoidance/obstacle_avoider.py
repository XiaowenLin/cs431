"""
This module contains functions implementing an obstacle avoider. The code is
based on example Python code for usage of OpenCV's Pyramidal Lucas-Kanade
algorithm found at
http://docs.opencv.org/master/d7/d8b/tutorial_py_lucas_kanade.html#gsc.tab=0.
TTC computation is based on information found at
http://teyvoniathomas.com/index.php/projects/55-opticalflow.html. The obstacle
avoidance strategy used here is the Balance Strategy.

This library requires the following libraries:

1. OpenCV, along with Python wrapper for OpenCV
2. NumPy
3. SciPy (for Delaunay triangulation)

On Debian/Ubuntu, run the following (as root) to install the above packages:

  apt-get install python-numpy python-scipy python-opencv
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

from optical_flow_drawer import OpticalFlowDrawer
from frame_worker import FrameWorker
from median_filter import MedianFilter
from threading import Thread
import numpy as np
import cv2
from cameras.auto_camera import AutoCamera
import time
from math import ceil

class ObstacleAvoiderThread(Thread):
    """
    Class for running the obstacle avoidance algorithm in a Python thread.
    """
    def __init__(self):
        """
        Constructor for ObstacleAvoiderThread. It sets up the parameters for
        camera snapshot retrieval as well as the parameters for optical flow
        feature selection and time-to-collision (TTC) calculations.
        """
        Thread.__init__(self)

        # Initialize camera
        self.camera = AutoCamera()

        # Parameters for Shi-Tomasi corner detection
        self.feature_params = dict( maxCorners = 100,
                                    qualityLevel = 0.3,
                                    minDistance = 7,
                                    blockSize = 7 )

        # Parameters for Lucas-Kanade optical flow
        self.lk_params = dict( winSize = (15,15),
                               maxLevel = 2,
                               criteria = (cv2.TERM_CRITERIA_EPS | \
                                           cv2.TERM_CRITERIA_COUNT, 10, 0.03) )

        # Initialize optical flow drawing class
        self.drawer = OpticalFlowDrawer(100)

        # Create array for line equations
        self.lines = np.zeros((100, 3))
        self.local_scales = np.zeros((100, 1))
        self.left_scales = np.zeros((100, 1))
        self.right_scales = np.zeros((100, 1))

        # Median filtering for smoother TTC computations
        self.scale_filter = MedianFilter(3)

        self.old_gray = None
        self.p0 = None

        # Callbacks
        self.imgdisp_cb = None
        self.min_ttc_cb = None
        self.balance_strategy_cb = None

    def set_imgdisp_cb(self, imgdisp_cb):
        """
        Setter for the image display callback. imgdisp_cb takes on the
        following format:

           imgdisp_cb(cv2, img)

        where cv2 is the OpenCV object, and img is the image data that was
        retrieved (either in original form or in modified form with optical
        flows).
        """
        self.imgdisp_cb = imgdisp_cb

    def set_min_ttc_cb(self, min_ttc_cb):
        """
        Setter for the minimum TTC value callback, which is called when the
        computation of this value has finished for a particular camera
        snapshot. min_ttc_cb takes on the following format:

           min_ttc_cb(the_min_ttc)

        where the_min_ttc is the minimum TTC value in the entire snapshot.
        """
        self.min_ttc_cb = min_ttc_cb

    def set_balance_strategy_cb(self, balance_strategy_cb):
        """
        Setter for the balance strategy callback, which is called when the
        computation of the minimum TTC value for the left and right halves of
        a particular camera snapshot has finished. balance_strategy_cb takes
        on the following format:

           balance_strategy_cb(left_ttc, right_ttc)

        where left_ttc is the minimum TTC value in the left half of the
        snapshot, and right_ttc is the minimum TTC value in the right half of
        the snapshot.
        """
        self.balance_strategy_cb = balance_strategy_cb

    @staticmethod
    def find_neighborhoods(delaunay_triangles):
        """
        Helper function used internally by the TTC computation algorithm for
        finding nearby feature points corresponding to a particular feature
        point. This function should not be used directly outside this class.
        """
        neighbor_dict = {}
        for triangle_point_indices in delaunay_triangles:
            index_set = set(triangle_point_indices)
            for index in index_set:
                index_set_2 = index_set - set([index])
                if len(index_set_2) != 0:
                    if neighbor_dict.get(index):
                        neighbor_dict[index] = neighbor_dict[index] | \
                                               index_set_2
                    else:
                        neighbor_dict[index] = index_set_2
        return neighbor_dict

    @staticmethod
    def filter_local_scales(local_scales, num_localscales, threshold=None):
        """
        Helper function used internally by the TTC computation algorithm for
        filtering local scale changes of each feature point using some specific
        threshold. This function should not be used directly outside this
        class.
        """
        thresh_scales = local_scales[:num_localscales]
        the_threshold = threshold
        max_local_scale = 0
        if len(thresh_scales) != 0:
            if threshold is None:
                the_threshold = 0.1 * thresh_scales.max()
            thresh_scales = thresh_scales[thresh_scales > the_threshold]
        if len(thresh_scales) != 0:
            max_local_scale = np.max(thresh_scales)
        return the_threshold, max_local_scale, thresh_scales

    def run(self):
        """
        A function representing the thread runtime code. This function takes
        care of camera snapshot retrieval, optical flow imaging, optical flow
        feature selection, TTC computations, and optical flow imaging. TTC
        computations are computed for the entire snapshot, which is useful for
        detecting obstacles, as well as for the left and right halves of the
        snapshot, which is useful for deciding whether to make a left or right
        turn. The thread runs until the user decides to terminate it.

        This function should not be used directly outside this class.
        """
        filter_update_time = None
        for frame in self.camera.get_iterator():
            last_iter_time = time.time()
            the_frame = self.camera.get_frame(frame)
            self.drawer.set_frame(the_frame)

            if self.old_gray is None:
                # Take first frame and find corners in it
                self.old_gray = cv2.cvtColor(the_frame, cv2.COLOR_BGR2GRAY)
                self.p0 = cv2.goodFeaturesToTrack(self.old_gray, mask = None, \
                                                  **self.feature_params)

                # Reset the state of the optical flow drawing class
                self.drawer.reset()

                # Move on to next frame capture
                filter_update_time = last_iter_time
                self.scale_filter.reset_filter()
                continue

            frame_gray = cv2.cvtColor(the_frame, cv2.COLOR_BGR2GRAY)

            # Calculate optical flow
            p1, st, _ = cv2.calcOpticalFlowPyrLK(self.old_gray, frame_gray, \
                                                 self.p0, None, \
                                                 **self.lk_params)
            if p1 is None:
                # We lost all tracking at this point; reinitialize the obstacle
                # avoider
                self.old_gray = None
                self.imgdisp_cb(cv2, the_frame)
                k = cv2.waitKey(30) & 0xff
                if k == 27: # Was escape pressed?
                    break
                continue

            # Select good points
            good_new = p1[st == 1]
            good_old = self.p0[st == 1]

            # Start worker up
            worker = FrameWorker(self, frame_gray, last_iter_time, \
                filter_update_time, good_old, good_new)
            worker.start()

            # Once we have results from the TTC computation, use them
            worker.wait_on_ttc_computation()
            filter_update_time = worker.get_latest_ttc_update_time()
            min_ttc, left_ttc, right_ttc = worker.get_ttc_values()
            if min_ttc is not None:
                self.min_ttc_cb(min_ttc)
                self.balance_strategy_cb(left_ttc, right_ttc)

            # Now update the previous frame and previous points
            if self.old_gray is not None:
                self.old_gray = frame_gray.copy()
                self.p0 = good_new.reshape(-1,1,2)

            # Once we have results from the render, use them
            worker.wait_on_render()
            self.imgdisp_cb(cv2, cv2.add(the_frame, worker.get_updated_mask()))

            # Idle for whatever time we have left
            iter_time = time.time()
            if last_iter_time is not None and last_iter_time + 30 > iter_time:
                k = cv2.waitKey(int(ceil(30 - (iter_time - last_iter_time))))
            else:
                k = cv2.waitKey(1) & 0xff
            if k == 27: # Was escape pressed?
                break

        cv2.destroyAllWindows()
        self.camera.destroy()

class ObstacleAvoider:
    """
    Class for retrieving image data from a camera and executing obstacle
    avoidance algorithms and optical flow imaging on those data. The work
    is handled by a separate Python thread, which is useful in multi-threaded
    applications.
    """
    def __init__(self):
        """
        Constructor for ObstacleAvoider. It initializes a thread class. Its
        constructor sets up the parameters for camera snapshot retrieval as
        well as the parameters for optical flow feature selection and
        time-to-collision (TTC) calculations.
        """
        self.thread = ObstacleAvoiderThread()
        self.thread.daemon = True

    def set_imgdisp_cb(self, imgdisp_cb):
        """
        Setter for the image display callback. imgdisp_cb takes on the
        following format:

           imgdisp_cb(cv2, img)

        where cv2 is the OpenCV object, and img is the image data that was
        retrieved (either in original form or in modified form with optical
        flows).
        """
        self.thread.set_imgdisp_cb(imgdisp_cb)

    def set_min_ttc_cb(self, min_ttc_cb):
        """
        Setter for the minimum TTC value callback, which is called when the
        computation of this value has finished for a particular camera
        snapshot. min_ttc_cb takes on the following format:

           min_ttc_cb(the_min_ttc)

        where the_min_ttc is the minimum TTC value in the entire snapshot.
        """
        self.thread.set_min_ttc_cb(min_ttc_cb)

    def set_balance_strategy_cb(self, balance_strategy_cb):
        """
        Setter for the balance strategy callback, which is called when the
        computation of the minimum TTC value for the left and right halves of
        a particular camera snapshot has finished. balance_strategy_cb takes
        on the following format:

           balance_strategy_cb(left_ttc, right_ttc)

        where left_ttc is the minimum TTC value in the left half of the
        snapshot, and right_ttc is the minimum TTC value in the right half of
        the snapshot.
        """
        self.thread.set_balance_strategy_cb(balance_strategy_cb)

    def start(self):
        """
        Starts the thread, which takes care of camera snapshot retrieval,
        optical flow imaging, optical flow feature selection, TTC computations,
        and optical flow imaging. TTC computations are computed for the entire
        snapshot, which is useful for detecting obstacles, as well as for the
        left and right halves of the snapshot, which is useful for deciding
        whether to make a left or right turn. The thread runs until the user
        decides to terminate it.
        """
        self.thread.start()

    def join(self):
        """
        Waits until the thread terminates. In this implementation, the thread
        terminates when the user presses the escape key (only when an OpenCV
        image window is shown and active).
        """
        self.thread.join()
