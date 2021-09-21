from enum import Enum
from PyQt5.QtCore import pyqtSignal

from wavemeter_dashboard.model.channel_model import ChannelModel


class GraphableDataKind(Enum):
    PATTERN = 0
    FREQ_LONGTERM = 1
    DAC_LONGTERM = 2
    ERR_LONGTERM = 3


class DataType(Enum):
    INT = 0
    FLOAT = 1
    DATETIME = 2


class GraphableDataProvider:
    name = ""
    kind = None

    def __init__(self, channel: ChannelModel):
        self.channel = channel
        self.x_axis_label = ""
        self.x_axis_unit = ""
        self.x_axis_type = DataType.FLOAT
        self.y_axis_label = ""
        self.y_axis_unit = ""
        self.y_axis_type = DataType.FLOAT
        self.y_axis_scale = 1
        self.append_only = False  # if new (x, y) pair is only append to the bottom at a time

        self.new_data_signal: pyqtSignal = None

    def get_data(self):
        # return (xs, ys) pair.
        # the pair could possibly be an iterator,
        # xs, ys could also be an iterator
        raise NotImplementedError

    def transfer_data(self, append_method):
        # call append_method(x, y) in a loop until all data are appended
        raise NotImplementedError

    def append_newest_data(self, append_method):
        # if self.append_only is True, then it is more efficient to only
        # append new data point to the existed graph
        # should be implemented by all children with self.append_only == True
        raise NotImplementedError


class PatternDataProvider(GraphableDataProvider):
    name = "INTERFEROMETER PATTERN"
    kind = GraphableDataKind.PATTERN

    def __init__(self, channel: ChannelModel):
        super().__init__(channel)
        self.x_axis_label = "CCD Channel"
        self.x_axis_unit = ""
        self.x_axis_type = DataType.INT
        self.y_axis_label = "Count"
        self.y_axis_unit = "arb."
        self.y_axis_type = DataType.INT
        self.append_only = False

        self.new_data_signal: pyqtSignal = channel.on_pattern_changed

    def get_data(self):
        # not efficient, not recommended
        return zip(*enumerate(self.channel.pattern_data))

    def transfer_data(self, append_method):
        for x, y in enumerate(self.channel.pattern_data):
            append_method(x, y)

    def append_newest_data(self, append_method):
        raise NotImplementedError


class FreqLongtermDataProvider(GraphableDataProvider):
    name = "FREQUENCY LONGTERM"
    kind = GraphableDataKind.FREQ_LONGTERM

    def __init__(self, channel: ChannelModel):
        super().__init__(channel)

        self.x_axis_label = "Time"
        self.x_axis_unit = ""
        self.x_axis_type = DataType.DATETIME
        self.y_axis_label = "Frequency"
        self.y_axis_unit = "THz"
        self.y_axis_type = DataType.INT
        self.y_axis_scale = 10e-12
        self.append_only = True

        self.new_data_signal: pyqtSignal = channel.on_freq_changed

    def get_data(self):
        return self.channel.freq_longterm_data.get_data()

    def transfer_data(self, append_method):
        # not efficient, not recommended
        self.channel.freq_longterm_data.transfer_to(append_method)

    def append_newest_data(self, append_method):
        append_method(self.channel.freq_longterm_data.get_newest_point())


class ErrLongtermDataProvider(GraphableDataProvider):
    name = "ERROR LONGTERM"
    kind = GraphableDataKind.ERR_LONGTERM

    def __init__(self, channel: ChannelModel):
        super().__init__(channel)

        self.x_axis_label = "Time"
        self.x_axis_unit = ""
        self.x_axis_type = DataType.DATETIME
        self.y_axis_label = "Frequency"
        self.y_axis_unit = "MHz"
        self.y_axis_type = DataType.INT
        self.y_axis_scale = 10e-6
        self.append_only = True

        self.new_data_signal: pyqtSignal = channel.on_freq_changed

    def get_data(self):
        if self.channel.freq_setpoint:
            return self.channel.freq_longterm_data.get_data()
        return None

    def transfer_data(self, append_method):
        # not efficient, not recommended
        if self.channel.freq_setpoint:
            setpoint = self.channel.freq_setpoint
            self.channel.freq_longterm_data.transfer_to(
                append_method, lambda pair: (pair[0], pair[1] - setpoint))

    def append_newest_data(self, append_method):
        if self.channel.freq_setpoint:
            x, y = self.channel.freq_longterm_data.get_newest_point()
            append_method(x, y - self.channel.freq_setpoint)


class DACLongtermDataProvider(GraphableDataProvider):
    name = "DAC OUTPUT LONGTERM"
    kind = GraphableDataKind.DAC_LONGTERM

    def __init__(self, channel: ChannelModel):
        super().__init__(channel)

        self.x_axis_label = "Time"
        self.x_axis_unit = ""
        self.x_axis_type = DataType.DATETIME
        self.y_axis_label = "DAC Output"
        self.y_axis_unit = "arb."
        self.y_axis_type = DataType.INT
        self.append_only = True

        self.new_data_signal: pyqtSignal = channel.on_pid_changed

    def get_data(self):
        return self.channel.dac_longterm_data.get_data()

    def transfer_data(self, append_method):
        # not efficient, not recommended
        self.channel.dac_longterm_data.transfer_to(append_method)

    def append_newest_data(self, append_method):
        append_method(self.channel.dac_longterm_data.get_newest_point())


GRAPHABLE_DATA = {
    GraphableDataKind.PATTERN: PatternDataProvider,
    GraphableDataKind.FREQ_LONGTERM: FreqLongtermDataProvider,
    GraphableDataKind.ERR_LONGTERM: ErrLongtermDataProvider,
    GraphableDataKind.DAC_LONGTERM: DACLongtermDataProvider
}