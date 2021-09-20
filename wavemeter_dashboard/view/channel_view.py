from typing import Type, TYPE_CHECKING
from datetime import datetime
import random
import numpy as np

from PyQt5.QtCore import pyqtSignal

from .widgets.freq_wavelength_label import FreqWavelengthLabel
from .widgets.thumbnail_line_chart import ThumbnailLineChart
from .widgets.channel_name_widget import ChannelNameWidget
from ..model.channel_model import ChannelModel

if TYPE_CHECKING:
    from .dashboard import Dashboard


class ChannelView:
    long_term_time_window = 300

    def __init__(self, dashboard: 'Dashboard', channel_model: ChannelModel):
        self.channel_model = channel_model
        self.dashboard = dashboard
        self.channel_name_widget = ChannelNameWidget(
            self.dashboard,
            channel_model.channel_name, channel_model.channel_num,
            channel_model.channel_color)
        self.freq_label = FreqWavelengthLabel(self.dashboard)
        self.freq_label.frequency = 0
        self.pattern = ThumbnailLineChart(self.dashboard)

        self.freq_longterm = ThumbnailLineChart(self.dashboard)
        self.error_longterm = ThumbnailLineChart(self.dashboard)
        self.dac_longterm = ThumbnailLineChart(self.dashboard)

        self.rebind_model(channel_model)

        self.channel_name_widget.on_set_clicked.connect(self.show_channel_setup)
        self.channel_name_widget.on_mon_toggled.connect(self.toggle_monitor_state)

    def rebind_model(self, model):
        self.channel_model = model
        self.channel_name_widget.set_name_color(model.channel_name,
                                                model.channel_num,
                                                model.channel_color)
        model.on_freq_changed.connect(self.on_freq_changed)
        model.on_pattern_changed.connect(self.on_pattern_changed)
        model.on_pid_changed.connect(self.on_pid_changed)

    def on_freq_changed(self):
        self.freq_label.frequency = self.channel_model.frequency
        now = datetime.now().timestamp()
        self.freq_longterm.set_x_display_range(
            now - self.long_term_time_window, now)
        self.freq_longterm.update_longterm_data(
            self.channel_model.freq_longterm_data)

        if self.channel_model.freq_setpoint:
            self.error_longterm.set_x_display_range(
                now - self.long_term_time_window, now)
            self.error_longterm.update_longterm_data(
                self.channel_model.error_longterm_data)

    def on_pattern_changed(self):
        max_amp = np.max(self.channel_model.pattern_data)
        if max_amp > self.dashboard.pattern_max_amp:
            self.dashboard.pattern_max_amp = max_amp

        self.pattern.update_data(range(len(self.channel_model.pattern_data)),
                                 self.channel_model.pattern_data)

    def on_pid_changed(self):
        now = datetime.now().timestamp()
        self.dac_longterm.set_x_display_range(
            now - self.long_term_time_window, now)
        self.dac_longterm.update_longterm_data(
            self.channel_model.dac_longterm_data)

    def show_channel_setup(self):
        self.dashboard.on_set_channel_clicked(self.channel_model.channel_num)

    def toggle_monitor_state(self, on):
        pass
