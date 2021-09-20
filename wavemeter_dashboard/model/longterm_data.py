import time

from wavemeter_dashboard.config import config


class LongtermData:
    def __init__(self):
        self.index = 0
        self.time = []
        self.values = []
        self.points_limit = 0

        if config.has('longterm_length_limit'):
            self.points_limit = config.get('longterm_length_limit')

    def append(self, data):
        if self.points_limit and len(self.values) == self.points_limit:
            if self.index == len(self.values):
                self.index = 0

            self.time[self.index] = time.time()
            self.values[self.index] = data
        else:
            self.time.append(time.time())
            self.values.append(data)

        self.index += 1

    def get_time_range(self):
        if self.index == len(self.time):
            t_min = self.time[0]
        else:
            t_min = self.time[self.index]

        if self.index - 1 < 0:
            t_max = self.time[-1]
        else:
            t_max = self.time[self.index - 1]

        return t_min, t_max

    def transfer_to(self, append_method):
        idx = self.index
        count = len(self.time)

        for i in range(count):
            if idx == count:
                idx = 0

            append_method(self.time[idx], self.values[idx])
            idx += 1

    def get_newest_point(self):
        idx = self.index - 1
        if self.index == -1:
            idx = len(self.time) - 1

        return self.time[idx], self.values[idx]

