from typing import Type, TYPE_CHECKING
from datetime import datetime
import random
import numpy as np

from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QColor

from .widgets.freq_wavelength_label import FreqWavelengthLabel
from .widgets.thumbnail_line_chart import ThumbnailLineChart
from .widgets.channel_name_widget import ChannelNameWidget
from .widgets.color_strip import ColorStrip
from .widgets.misc import ErrorLabel
from ..model.channel_model import ChannelModel

if TYPE_CHECKING:
    from .dashboard import Dashboard


class ChannelView:
    long_term_time_window = 300

    def __init__(self, dashboard: 'Dashboard', channel_model: ChannelModel, color_strip: ColorStrip):
        self.channel_model = channel_model
        self.dashboard = dashboard
        self.color_strip = color_strip
        self.channel_name_widget = ChannelNameWidget(
            self.dashboard,
            channel_model.channel_name, channel_model.channel_num,
            channel_model.channel_color)

        self.freq_label = FreqWavelengthLabel(self.dashboard)
        self.freq_label.frequency = 0
        self.pattern = ThumbnailLineChart(self.dashboard)
        self.freq_longterm = ThumbnailLineChart(self.dashboard)
        self.dac_longterm = ThumbnailLineChart(self.dashboard)
        self.error_label = ErrorLabel(self.dashboard)

        self.channel_name_widget.hide()
        self.freq_label.hide()
        self.freq_longterm.hide()
        self.dac_longterm.hide()
        self.error_label.hide()

        self.rebind_model(channel_model)

        self.channel_name_widget.on_set_clicked.connect(self.show_channel_setup)
        self.channel_name_widget.on_mon_toggled.connect(self.toggle_monitor_state)

        self.channel_name_widget.btn_mon_checked(channel_model.monitor_enabled)

    def rebind_model(self, model):
        self.channel_model = model
        self.channel_name_widget.set_name_color(model.channel_name,
                                                model.channel_num,
                                                model.channel_color)
        model.on_freq_changed.connect(self.on_freq_changed)
        model.on_pattern_changed.connect(self.on_pattern_changed)
        model.on_pid_changed.connect(self.on_pid_changed)

        if model.freq_setpoint:
            self.freq_longterm.add_vertical_line(
                "freq_setpoint",
                model.freq_setpoint,
                QColor("white"), True)
        else:
            self.freq_longterm.remove_vertical_line("freq_setpoint")

        if model.freq_max_error:
            self.freq_longterm.add_vertical_line(
                "freq_max_error_high",
                model.freq_setpoint + model.freq_max_error,
                QColor("white"))
            self.freq_longterm.add_vertical_line(
                "freq_max_error_low",
                model.freq_setpoint - model.freq_max_error,
                QColor("white"))
        else:
            self.freq_longterm.remove_vertical_line("freq_max_error_high")
            self.freq_longterm.remove_vertical_line("freq_max_error_low")

    def on_freq_changed(self):
        self.freq_label.frequency = self.channel_model.frequency
        now = datetime.now().timestamp()
        self.freq_longterm.set_x_display_range(
            now - self.long_term_time_window, now)
        self.freq_longterm.update_longterm_data(
            self.channel_model.freq_longterm_data)

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
        
        # if self.channel_model.dac_railed:
        #     self.color_strip.flash_error()
        # else:
        #     self.color_strip.hide_error()  # TODO: keep track of error
            
    def show_channel_setup(self):
        self.dashboard.on_set_channel_clicked(self.channel_model.channel_num)

    def toggle_monitor_state(self, on):
        self.channel_model.monitor_enabled = on
