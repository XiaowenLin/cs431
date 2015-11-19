import numpy as np

class MedianFilter:
    def __init__(self, num_inputs, filter_size=5):
        self.num_inputs = num_inputs
        self.filter_size = filter_size
        self.reset_filter()

    def reset_filter(self):
        self.filter_state = 0
        self.filters = [[] for _ in range(self.num_inputs)]

    def set_filter_value(self, input_index, new_value):
        self.filters[input_index].append(new_value)

    def set_filter_values(self, new_values):
        input_index = 0
        for new_value in new_values:
            self.set_filter_value(input_index, new_value)
            input_index += 1

    def update_filter(self):
        result = None
        self.filter_state += 1
        if self.filter_state >= self.filter_size:
            result = np.median(self.filters, axis=1)
            self.reset_filter()
        return result
