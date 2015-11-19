"""
This module contains functions implementing a median filter. The scheme
accepts more than one input for multiple streams of data, which allows median
filtering to be performed on each component in one go.
"""

__author__ = "Ron Wright"
__copyright__ = "Copyright 2015 Ronald Joseph Wright"
__maintainer__ = "Ron Wright"

import numpy as np

class MedianFilter:
    """
    Class for median filtering.
    """
    def __init__(self, num_inputs, filter_size=5):
        """
        Constructor for MedianFilter, where num_inputs is the number of inputs
        that the filter expects, and the optional parameter filter_size (with
        default value 5) is the size of the median filter.
        """
        self.num_inputs = num_inputs
        self.filter_size = filter_size
        self.reset_filter()

    def reset_filter(self):
        """
        Resets the entire state of the filter.
        """
        self.filter_state = 0
        self.filters = [[] for _ in range(self.num_inputs)]

    def set_filter_value(self, input_index, new_value):
        """
        Sets a filter value for a particular input in a particular state, where
        input_index is the index representing a particular input, and new_value
        is the value for the input.
        """
        self.filters[input_index].append(new_value)

    def set_filter_values(self, new_values):
        """
        Sets all filter values for a particular state, where new_values is an
        array of values for all the corresponding inputs.
        """
        input_index = 0
        for new_value in new_values:
            self.set_filter_value(input_index, new_value)
            input_index += 1

    def update_filter(self):
        """
        Updates the state of the filter. If all data have been retrieved, the
        median value for each input is computed, the state of the filter is
        reset for next time, and an array corresponding to the median values
        is returned. Otherwise, None is returned.
        """
        result = None
        self.filter_state += 1
        if self.filter_state >= self.filter_size:
            result = np.median(self.filters, axis=1)
            self.reset_filter()
        return result
