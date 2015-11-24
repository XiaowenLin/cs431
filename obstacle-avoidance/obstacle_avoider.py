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
from median_filter import MedianFilter
from threading import Thread
import numpy as np
from scipy.spatial import Delaunay
from scipy.spatial.qhull import QhullError
import cv2
from generic_camera import GenericCamera
import time

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
        self.camera = GenericCamera()

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
        start = None
        for frame in self.camera.get_iterator():
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
                start = time.time()
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

            # Find local scales consisting of computation of feature points and
            # any other feature points in their Delaunay neighborhoods.  I'm
            # hoping this is the right way to compute the local scales.  The
            # numbers looked reasonable when I ran this.
            num_localscales = 0
            num_left_scales = 0
            num_right_scales = 0
            if len(good_old) >= 4:
                try:
                    old_triangles = Delaunay(good_old).simplices
                    neighborhoods = ObstacleAvoiderThread.find_neighborhoods( \
                        old_triangles)
                    for (k, v) in neighborhoods.items():
                        index_arr = np.array(list(v))

                        # target point
                        new_point = good_new[k]
                        old_point = good_old[k]

                        # neighborhood points
                        new_neighborhood = good_new[index_arr]
                        old_neighborhood = good_old[index_arr]

                        sum2 = np.sum(np.linalg.norm( \
                            new_point - new_neighborhood, axis=1))
                        if sum2 != 0:
                            sum1 = np.sum(np.linalg.norm( \
                                old_point - old_neighborhood, axis=1))
                            local_scale = (sum1 - sum2) / sum2

                            if (2*new_point[1]) >= np.shape(frame_gray)[1]:
                                self.left_scales[num_left_scales] = local_scale
                                num_left_scales += 1
                            else:
                                self.right_scales[num_right_scales] = \
                                    local_scale
                                num_right_scales += 1

                            self.local_scales[num_localscales] = local_scale
                            num_localscales += 1
                except (QhullError, ValueError):
                    pass

            # Draw the tracks
            self.drawer.draw_tracks(good_old, good_new)

            # Find max local scale on whole screen
            threshold, max_scale, thresh_scales = \
                ObstacleAvoiderThread.filter_local_scales( \
                    self.local_scales, num_localscales)

            if len(thresh_scales) == 0:
                # We lost sufficient information at this point; reinitialize
                # the obstacle avoider
                self.old_gray = None
            else:
                # Find max local scale on left half of screen
                _, left_max_scale, _ = \
                    ObstacleAvoiderThread.filter_local_scales( \
                        self.left_scales, num_left_scales, \
                        threshold=threshold)

                # Find max local scale on right half of screen
                _, right_max_scale, _ = \
                    ObstacleAvoiderThread.filter_local_scales( \
                        self.right_scales, num_right_scales, \
                        threshold=threshold)

                # Find maximum in each set of thresholded local scales
                self.scale_filter.set_filter_values( \
                    (max_scale, left_max_scale, right_max_scale))
                medians = self.scale_filter.update_filter()

                if medians is not None:
                    # Find median of each maximum local scale
                    median_max_scale, left_median_max_scale, \
                                      right_median_max_scale = medians

                    # Find change in time, keeping in mind that we must
                    # compensate for median filtering.
                    end = time.time()
                    delta = (end - start) / self.scale_filter.filter_size
                    start = end

                    self.min_ttc_cb(float('inf') if median_max_scale == 0 \
                                    else delta / median_max_scale)
                    left_ttc = float('inf') if left_median_max_scale == 0 \
                               else delta / left_median_max_scale
                    right_ttc = float('inf') if right_median_max_scale == 0 \
                                else delta / right_median_max_scale
                    self.balance_strategy_cb(left_ttc, right_ttc)

            img = cv2.add(the_frame, self.drawer.get_current_mask())
            self.drawer.update_frame_state()
            self.imgdisp_cb(cv2, img)

            k = cv2.waitKey(30) & 0xff
            if k == 27: # Was escape pressed?
                break

            # Now update the previous frame and previous points
            if self.old_gray is not None:
                self.old_gray = frame_gray.copy()
                self.p0 = good_new.reshape(-1,1,2)

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
