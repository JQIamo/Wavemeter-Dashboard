from typing import Type, TYPE_CHECKING
from datetime import datetime
import random
import numpy as np

from PyQt5.QtCore import pyqtSignal

from .widgets.misc import ChannelNameLabel, BigContentLabel
from .widgets.freq_wavelength_label import FreqWavelengthLabel
from .widgets.thumbnail_line_chart import ThumbnailLineChart
from ..model.channel_model import ChannelModel

if TYPE_CHECKING:
    from .dashboard import Dashboard


class ChannelView:
    def __init__(self, dashboard: 'Dashboard', channel_model: ChannelModel):
        self.channel_model = channel_model
        self.dashboard = dashboard
        self.channel_name_label = ChannelNameLabel(
            self.dashboard,
            channel_model.channel_name, f"#{channel_model.channel_num}",
            channel_model.channel_color)
        self.freq_label = FreqWavelengthLabel(self.dashboard)
        self.freq_label.frequency = 0
        self.pattern = ThumbnailLineChart(self.dashboard)

        self.freq_longterm = ThumbnailLineChart(self.dashboard)

        channel_model.on_freq_changed.connect(self.on_freq_changed)
        channel_model.on_pattern_changed.connect(self.on_pattern_changed)

    def on_freq_changed(self):
        self.freq_label.frequency = self.channel_model.frequency
        now = datetime.now().timestamp()
        self.freq_longterm.set_x_display_range(
            now - 300, now)
        self.freq_longterm.update_longterm_data(
            self.channel_model.freq_longterm_data)

    def on_pattern_changed(self):
        max_amp = np.max(self.channel_model.pattern_data)
        if max_amp > self.dashboard.pattern_max_amp:
            self.dashboard.pattern_max_amp = max_amp

        self.pattern.update_data(range(len(self.channel_model.pattern_data)),
                                 self.channel_model.pattern_data)

