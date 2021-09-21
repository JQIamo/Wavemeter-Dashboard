import time
from abc import ABC

import numpy as np

from wavemeter_dashboard.config import config


class Array(ABC):
    def __init__(self):
        self.length = 0
        pass

    def append(self, item):
        raise NotImplementedError

    def view(self):
        raise NotImplementedError


class ExtendableArray(Array):
    def __init__(self):
        super().__init__()
        self._list = []

    def append(self, item):
        self._list.append(item)

    def view(self):
        return self._list

    @property
    def length(self):
        return len(self._list)


class RoundRobinArray(Array):
    # Before writing this class, I have thousands of complaints to make.
    # Round-robin array is undoubtedly a very common kind of data structure,
    # nut why there isn't an implementation ready on the shelf?
    # Why QtChart and pyqtgraph use different methods to handle plot data (
    # appending vs. passing array), etc.
    # I'm very unpleasant about these weird things because they cost me extra
    # labor.

    # Yeah, it is short, but it still took me 20min. And now I have to refactor
    # a lot of things...

    def __init__(self, length):
        super().__init__()
        self.length = length
        self.index = 0
        self.array = np.zeros(length * 2)  # trade time with space

        self.full = False

    def append(self, item):
        self.array[self.index] = item
        self.array[self.length + self.index] = item
        self.index += 1

        if self.index == self.length:
            self.index = 0
            self.full = True

    def view(self):
        if not self.full:
            return self.array[:self.index].view()
        else:
            return self.array[self.index:self.index + self.length].view()


class LongtermData:
    def __init__(self):
        self.points_limit = 0
        if config.has('longterm_length_limit'):
            self.points_limit = config.get('longterm_length_limit')

            self.time = RoundRobinArray(self.points_limit)
            self.values = RoundRobinArray(self.points_limit)
        else:
            self.time = ExtendableArray()
            self.values = ExtendableArray()

    def append(self, data):
        self.time.append(time.time())
        self.values.append(data)

    def get_time_range(self):
        view = self.time.view()
        return view[0], view[-1]

    def get_newest_point(self):
        return self.time.view()[-1], self.values.view()[-1]

    def get_data(self):
        return self.time.view(), self.values.view()

    def transfer_to(self, append_method, pre_process_func=None):
        # not efficient, should use get_data or get_newest_point instead
        if not pre_process_func:
            for t, v in zip(self.time.view(), self.values.view()):
                append_method(t, v)
        else:
            for t, v in zip(self.time.view(), self.values.view()):
                append_method(*pre_process_func(t, v))

