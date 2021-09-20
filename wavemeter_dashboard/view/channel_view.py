from typing import Type, TYPE_CHECKING
import time
import random
import numpy as np

from PyQt5.QtGui import QColor

from .widgets.channel_alert_label import ChannelAlertLabel
from .widgets.freq_wavelength_label import FreqWavelengthLabel
from .widgets.thumbnail_line_chart import ThumbnailLineChart
from .widgets.channel_name_widget import ChannelNameWidget
from .widgets.color_strip import ColorStrip
from ..model.channel_alert import ChannelAlertAction
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
        self.alert_label = ChannelAlertLabel(self.dashboard, channel_model)

        self.channel_name_widget.hide()
        self.freq_label.hide()
        self.freq_longterm.hide()
        self.dac_longterm.hide()
        self.alert_label.hide()

        self.bind_model(channel_model)

        self.channel_name_widget.on_set_clicked.connect(self.show_channel_setup)
        self.channel_name_widget.on_mon_toggled.connect(self.toggle_monitor_state)

        self.channel_name_widget.btn_mon_checked(channel_model.monitor_enabled)

        self.channel_model.on_channel_alert_action_changed.connect(self.change_alert_status)
        self.channel_model.on_refresh_alert_display_requested.connect(self.alert_label.update)

        if channel_model.freq_setpoint:
            self.freq_longterm.add_vertical_line(
                "freq_setpoint",
                channel_model.freq_setpoint,
                QColor("white"), True)
        else:
            self.freq_longterm.remove_vertical_line("freq_setpoint")

        if channel_model.freq_max_error:
            self.freq_longterm.add_vertical_line(
                "freq_max_error_high",
                channel_model.freq_setpoint + channel_model.freq_max_error,
                QColor("white"))
            self.freq_longterm.add_vertical_line(
                "freq_max_error_low",
                channel_model.freq_setpoint - channel_model.freq_max_error,
                QColor("white"))
        else:
            self.freq_longterm.remove_vertical_line("freq_max_error_high")
            self.freq_longterm.remove_vertical_line("freq_max_error_low")

    def bind_model(self, model):
        self.channel_model = model
        self.channel_name_widget.set_name_color(model.channel_name,
                                                model.channel_num,
                                                model.channel_color)
        model.on_freq_changed.connect(self.on_freq_changed)
        model.on_pattern_changed.connect(self.on_pattern_changed)
        model.on_pid_changed.connect(self.on_pid_changed)

    def on_freq_changed(self):
        self.freq_label.frequency = self.channel_model.frequency
        now = time.time()
        self.freq_longterm.set_x_display_range(
            now - self.long_term_time_window, now)
        x, y = self.channel_model.freq_longterm_data.get_newest_point()
        limit = self.channel_model.freq_longterm_data.points_limit
        self.freq_longterm.append_newest_point(x, y, limit)
        # self.freq_longterm.update_longterm_data(
        #     self.channel_model.freq_longterm_data)

    def on_pattern_changed(self):
        max_amp = np.max(self.channel_model.pattern_data)
        if max_amp > self.dashboard.pattern_max_amp:
            self.dashboard.pattern_max_amp = max_amp

        self.pattern.update_data(range(len(self.channel_model.pattern_data)),
                                 self.channel_model.pattern_data)

    def on_pid_changed(self):
        now = time.time()
        self.dac_longterm.set_x_display_range(
            now - self.long_term_time_window, now)
        x, y = self.channel_model.dac_longterm_data.get_newest_point()
        limit = self.channel_model.dac_longterm_data.points_limit
        self.dac_longterm.append_newest_point(x, y, limit)
        # self.dac_longterm.update_longterm_data(
        #     self.channel_model.dac_longterm_data)

    def show_channel_setup(self):
        self.dashboard.on_set_channel_clicked(self.channel_model.channel_num)

    def toggle_monitor_state(self, on):
        self.channel_model.monitor_enabled = on

    def change_alert_status(self, alert_status: ChannelAlertAction):
        self.color_strip.hide()
        if alert_status == ChannelAlertAction.NOTHING:
            self.color_strip.hide()
        elif alert_status == ChannelAlertAction.STATIC_WARNING:
            self.color_strip.show_warning()
        elif alert_status == ChannelAlertAction.STATIC_ERROR:
            self.color_strip.show_error()
        elif alert_status == ChannelAlertAction.FLASH_WARNING:
            self.color_strip.flash_warning()
        elif alert_status == ChannelAlertAction.FLASH_ERROR:
            self.color_strip.flash_error()
