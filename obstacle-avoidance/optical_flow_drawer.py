"""
This module contains functions implementing the drawing of optical flows. The
trail size for all optical flows is bounded to prevent clutter.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

import cv2
import numpy as np

class OpticalFlowDrawer:
    """
    Class for drawing optical flows.
    """
    def __init__(self, max_corners, trail_size=15):
        """
        Constructor for OpticalFlowDrawer, where max_corners is the maximum
        number of corners that is used to find corner points, and the optional
        parameter trail_size (with default value 15) is the maximum trail size
        (in frames) for any given optical flow.
        """
        self.frame = None

        self.restore_init_state()
        self.masks = None
        self.trail_size = trail_size

        # Create some random colors
        self.color = np.random.randint(0, 255, (max_corners, 3))

    def set_frame(self, frame):
        """
        Sets the frame to be used for a particular drawing task.
        """
        self.frame = frame

    def restore_init_state(self):
        """
        Helper function for the constructor and the reset function that resets
        the mask index and count variables. This function should not be used
        directly outside this class.
        """
        self.curr_mask_index = 0
        self.mask_count = 0

    def reset(self):
        """
        Resets the entire state of the optical flow drawing class.
        """
        # Create mask images for drawing purposes
        self.restore_init_state()
        self.masks = [np.zeros_like(self.frame) \
                      for _ in range(self.trail_size)]

    def draw_line(self, index, a, b, c, d):
        """
        Helper function for draw_tracks that draws a line in the current mask
        as well as the previous masks. This function should not be used
        directly outside this class.
        """
        for mask_index in range(min(self.mask_count + 1, self.trail_size)):
            cv2.line(self.masks[mask_index], (a,b),(c,d), \
                     self.color[index].tolist(), 2, lineType=cv2.CV_AA)

    def get_current_mask(self):
        """
        Returns the currently active mask.
        """
        return self.masks[self.curr_mask_index]

    def update_frame_state(self):
        """
        Updates the frame state for the next iteration. Once we have all masks
        filled out, the current mask is cleared out to facilitate the drawing
        of finite-length optical flow trails.
        """
        if self.mask_count >= self.trail_size:
            self.masks[self.curr_mask_index] = np.zeros_like(self.frame)
            self.curr_mask_index = (self.curr_mask_index + 1) % self.mask_count
        else:
            self.mask_count += 1

    def draw_tracks(self, old_features, new_features):
        """
        Develops a set of optical flow trails by drawing lines between old
        features and their corresponding new features. old_features is the
        set of old good features, and new_features is the set of new good
        features.
        """
        for i,(new, old) in enumerate(zip(new_features, old_features)):
            # draw the optical flow vector
            a,b = new.ravel()
            c,d = old.ravel()

            self.draw_line(i, a, b, c, d)
            cv2.circle(self.frame, (a,b),5,self.color[i].tolist(),-1)
