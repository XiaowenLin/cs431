"""
This function implements the worker routines that are used for the obstacle
avoider.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

import threading
from median_filter import MedianFilter
import numpy as np
from scipy.spatial import Delaunay
from scipy.spatial.qhull import QhullError
import time

class FrameWorker:
    """
    Class with worker routines that are used for the obstacle avoider.
    """
    def __init__(self, the_thread, frame_gray, old_ttc_update_time, good_old, \
        good_new):
        """
        Constructor for FrameWorker, where frame_gray is the grayscale image
        frame, old_ttc_update_time is the most recent TTC update time (in
        UNIX seconds), good_old is the filtered set of good feature points
        from the previous iteration, and good_new is the filtered set of good
        feature points from the current iteration.
        """
        self.the_thread = the_thread
        self.frame_gray = frame_gray
        self.old_ttc_update_time = old_ttc_update_time
        self.new_ttc_update_time = self.old_ttc_update_time
        self.good_old = good_old
        self.good_new = good_new
        self.updated_mask = None
        self.min_ttc = None
        self.left_ttc = None
        self.right_ttc = None
        self.t1 = None
        self.t2 = None

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

    def start(self):
        """
        Starts the TTC computation and rendering threads.
        """
        # Start TTC computation function as a thread
        self.t1 = threading.Thread(target=self.ttc_computation_function)
        self.t1.daemon = True
        self.t1.start()
        # Start image/optical flow rendering function as a thread
        self.t2 = threading.Thread(target=self.rendering_function)
        self.t2.daemon = True
        self.t2.start()

    def wait_on_ttc_computation(self):
        """
        Waits for the TTC computation thread to finish.
        """
        self.t1.join()

    def wait_on_render(self):
        """
        Waits for the rendering thread to finish.
        """
        self.t2.join()

    def ttc_computation_function(self):
        """
        TTC computation thread function that computes the overall TTC, left
        TTC, and right TTC.
        """
        the_thread = self.the_thread
        frame_gray = self.frame_gray
        good_old = self.good_old
        good_new = self.good_new

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
                neighborhoods = FrameWorker.find_neighborhoods( \
                    old_triangles)
                for (k, v) in list(neighborhoods.items()):
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

                        if (2*new_point[0]) < np.shape(frame_gray)[0]:
                            the_thread.left_scales[num_left_scales] = \
                                local_scale
                            num_left_scales += 1
                        else:
                            the_thread.right_scales[num_right_scales] = \
                                local_scale
                            num_right_scales += 1

                        the_thread.local_scales[num_localscales] = local_scale
                        num_localscales += 1
            except (QhullError, ValueError):
                pass

        # Find max local scale on whole screen
        threshold, max_scale, thresh_scales = \
            FrameWorker.filter_local_scales( \
                the_thread.local_scales, num_localscales)

        if len(thresh_scales) == 0:
            # We lost sufficient information at this point; reinitialize
            # the obstacle avoider
            the_thread.old_gray = None
        else:
            # Find max local scale on left half of screen
            _, left_max_scale, _ = \
                FrameWorker.filter_local_scales( \
                    the_thread.left_scales, num_left_scales, \
                    threshold=threshold)

            # Find max local scale on right half of screen
            _, right_max_scale, _ = \
                FrameWorker.filter_local_scales( \
                    the_thread.right_scales, num_right_scales, \
                    threshold=threshold)

            # Find maximum in each set of thresholded local scales
            the_thread.scale_filter.set_filter_values( \
                (max_scale, left_max_scale, right_max_scale))
            medians = the_thread.scale_filter.update_filter()

            if medians is not None:
                # Find median of each maximum local scale
                median_max_scale, left_median_max_scale, \
                                  right_median_max_scale = medians

                # Find change in time, keeping in mind that we must
                # compensate for median filtering.
                self.new_ttc_update_time = time.time()
                delta = (self.new_ttc_update_time - self.old_ttc_update_time) \
                    / the_thread.scale_filter.filter_size

                self.min_ttc = float('inf') if median_max_scale == 0 \
                                else delta / median_max_scale
                self.left_ttc = float('inf') if left_median_max_scale == 0 \
                           else delta / left_median_max_scale
                self.right_ttc = float('inf') if right_median_max_scale == 0 \
                            else delta / right_median_max_scale

    def rendering_function(self):
        """
        Rendering function that draws optical flow tracks on top of the image.
        """
        # Draw the tracks
        self.the_thread.drawer.draw_tracks(self.good_old, self.good_new)
        self.updated_mask = self.the_thread.drawer.get_current_mask()
        self.the_thread.drawer.update_frame_state()

    def get_updated_mask(self):
        """
        Getter for retrieving the most recently updated mask.
        """
        return self.updated_mask

    def get_latest_ttc_update_time(self):
        """
        Getter for retrieving the most recent TTC update time.
        """
        return self.new_ttc_update_time

    def get_ttc_values(self):
        """
        Getter that returns a triplet containing the minimum TTC, left TTC, and
        right TTC.  If the median filter is not finished processing, all three
        values will be None.
        """
        return self.min_ttc, self.left_ttc, self.right_ttc
