from enum import Enum
from typing import List, Dict

from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from PyQt5.QtCore import pyqtSignal
from .ui.ui_dashboard import Ui_dashboard
from .widgets.misc import *
from .widgets.add_channel_dialog import AddChannelDialog
from .widgets.color_strip import ColorStrip
from .channel_view import ChannelView
from wavemeter_dashboard.model.channel_model import ChannelModel
from wavemeter_dashboard.config import config
from ..controller.alert_tracker import AlertTracker
from ..controller.monitor import Monitor
from ..model.channel_alert import ChannelAlertCode
from ..model.graphable_data_provider import GraphableDataKind


class ColumnType(Enum):
    NAME = 1
    FREQ = 2
    PATTERN = 3
    FREQ_LONGTERM = 4
    PID_OUTPUT_LONGTERM = 5
    STATUS = 6


column_name = {
    ColumnType.NAME: 'CHANNEL',
    ColumnType.FREQ: 'FREQ',
    ColumnType.PATTERN: 'INTERFEROMETER',
    ColumnType.FREQ_LONGTERM: 'FREQ LONGTERM',
    ColumnType.PID_OUTPUT_LONGTERM: 'FDBK LONGTERM',
    ColumnType.STATUS: 'STATUS'
}


class Dashboard(QWidget):
    column_num_map = {
        ColumnType.NAME: 0,
        ColumnType.FREQ: 1,
        ColumnType.PATTERN: 2,
        ColumnType.FREQ_LONGTERM: 3,
        ColumnType.PID_OUTPUT_LONGTERM: 4,
        ColumnType.STATUS: 5
    }

    row_height = 75
    vertical_spacing = 20
    horizontal_spacing = 30

    on_switch_to_single_channel_display_clicked = pyqtSignal(ChannelModel, GraphableDataKind)
    on_channel_list_update = pyqtSignal()

    def __init__(self, parent, monitor: Monitor, alert_tracker: AlertTracker,
                 channels: List[ChannelModel]=None):
        super().__init__(parent)

        self.channels: List[ChannelView] = []
        self.color_strips: Dict[ColorStrip] = {}
        self.monitor = monitor
        self.alert_tracker = alert_tracker

        self.pattern_max_amp = 0

        self.setAutoFillBackground(True)
        self.ui = Ui_dashboard()
        self.ui.setupUi(self)

        self.ui.monBtn.setEnabled(False)

        self.ui.channelGridLayout.setVerticalSpacing(self.vertical_spacing)
        self.ui.channelGridLayout.setHorizontalSpacing(self.horizontal_spacing)

        self._init_table_header()

        self.placeholder_prompt_label = None
        self._add_channel_placeholder()

        self.ui.addChannelBtn.clicked.connect(self.on_add_channel_clicked)
        self.ui.monBtn.clicked.connect(self.on_monitor_toggled)
        self.ui.saveSettingsBtn.clicked.connect(self.save_channel_settings)
        self.ui.closeWindowButton.clicked.connect(QApplication.quit)

        self.center_floating_widget = None

        self.monitor.on_monitoring_channel.connect(self.on_monitoring_channel)

        if channels:
            self.load_channels_from_models(channels)

    def _init_table_header(self):
        for col, num in self.column_num_map.items():
            if column_name[col]:
                label = TableHeaderLabel(self)
            else:
                label = QLabel(self)

            label.setText(column_name[col])
            self.ui.channelGridLayout.addWidget(label, 0, num)

    def _add_channel_placeholder(self):
        if len(self.channels) != 0:
            return

        self.placeholder_prompt_label = ChannelPlaceholderPromptLabel(
            "CHANNEL LIST EMPTY", self)
        self.ui.channelGridLayout.addWidget(
            self.placeholder_prompt_label, 1, 0, 1,
            self.ui.channelGridLayout.columnCount())

    def _remove_channel_placeholder(self):
        if self.placeholder_prompt_label:
            self.ui.channelGridLayout.removeWidget(self.placeholder_prompt_label)
            self.placeholder_prompt_label = None

    def load_channels_from_models(self, channels: List[ChannelModel]):
        for model in channels:
            self.add_channel(model)

        if self.channels:
            self.ui.monBtn.setEnabled(True)

    def find_channel_by_num(self, num):
        filtered = list(filter(
            lambda c: c[1].channel_model.channel_num == num,
            enumerate(self.channels)
        ))
        if filtered:
            ch = filtered[0]
            return ch[1]

        return None

    def on_add_channel_dialog_apply(self, channel: ChannelModel):
        self.ui.saveSettingsBtn.setText("SAVE*")

        self.add_channel(channel)

    def on_add_channel_dialog_close(self, status):
        self.ui.addChannelBtn.setEnabled(True)
        if self.channels:
            self.ui.monBtn.setEnabled(True)

    def add_channel(self, channel: ChannelModel):
        if self.channels:
            self.ui.monBtn.setEnabled(True)

        self._remove_channel_placeholder()

        old_ch = self.find_channel_by_num(channel.channel_num)
        if not old_ch:
            color_strip = ColorStrip(self)
            self.color_strips[channel.channel_num] = color_strip
            view = ChannelView(self, channel, color_strip)
            self.monitor.add_channel(channel)
            self.alert_tracker.add_channel(channel)
            self.channels.append(view)

            for col_type, widget, to_show, fix_height in [
                (ColumnType.NAME, view.channel_name_widget, True, True),
                (ColumnType.FREQ, view.freq_label, True, True),
                (ColumnType.PATTERN, view.pattern, True, True),
                (ColumnType.FREQ_LONGTERM, view.freq_longterm, True, True),
                (ColumnType.PID_OUTPUT_LONGTERM, view.dac_longterm, True, True),
                (ColumnType.STATUS, view.alert_label, True, False),
            ]:
                self.ui.channelGridLayout.addWidget(
                    widget,
                    len(self.channels),
                    self.column_num_map[col_type]
                )
                if fix_height:
                    widget.setFixedHeight(self.row_height)

                if to_show:
                    widget.show()

            channel.on_new_alert.emit(ChannelAlertCode.IDLE)
            view.alert_label.update()
            self.resize(self.width(), self.height())

    def remove_channel(self, channel_num):
        if self.monitor.is_monitoring():
            self.monitor.stop_monitoring()

        # find channel in self.channels
        filtered = list(filter(
            lambda c: c[1].channel_model.channel_num == channel_num,
            enumerate(self.channels)
        ))
        if not filtered:
            return
        idx = filtered[0][0]

        del self.channels[idx]
        del self.color_strips[channel_num]

        self.monitor.remove_channel(channel_num)
        self.alert_tracker.remove_channel(channel_num)

    def on_add_channel_clicked(self):
        dialog = AddChannelDialog(self, self.monitor)
        self.ui.addChannelBtn.setEnabled(False)
        self.ui.monBtn.setEnabled(False)

        dialog.on_apply.connect(self.on_add_channel_dialog_apply)
        dialog.on_close.connect(self.on_add_channel_dialog_close)
        dialog.show()

    def on_set_channel_clicked(self, channel_num):
        old_ch = self.find_channel_by_num(channel_num)

        if not old_ch:
            return

        dialog = AddChannelDialog(self, self.monitor, old_ch.channel_model)
        dialog.show_remove_channel_button()
        self.ui.addChannelBtn.setEnabled(False)
        self.ui.monBtn.setEnabled(False)

        dialog.on_apply.connect(self.on_add_channel_dialog_apply)
        dialog.on_close.connect(self.on_add_channel_dialog_close)
        dialog.on_remove_channel.connect(self.remove_channel)
        dialog.show()

    def display_message_box(self, title, message):
        pass

    def resizeEvent(self, event):
        QWidget.resizeEvent(self, event)
        if self.center_floating_widget:
            self.center_floating_widget.move_to_center()

        self.resize_color_strips()

    def resize_color_strips(self):
        for channel in self.channels:
            y = channel.channel_name_widget.y() - 0.5 * self.vertical_spacing
            h = self.row_height + self.vertical_spacing

            self.color_strips[channel.channel_model.channel_num].set_position(
                0, y,
                self.width(), h
            )

    def on_monitor_toggled(self, state):
        if state:
            self.monitor.start_monitoring()
            self.ui.addChannelBtn.setEnabled(False)
        else:
            self.monitor.stop_monitoring()
            self.ui.addChannelBtn.setEnabled(True)

    def save_channel_settings(self):
        channel_list = []
        for chan in self.channels:
            channel_list.append(chan.channel_model.dump_settings_dict())
        config.set('channels', channel_list)
        config.save()
        self.ui.saveSettingsBtn.setText("SAVE")

    def on_monitoring_channel(self, channel_num):
        for chan in self.channels:
            if channel_num == chan.channel_model.channel_num:
                chan.channel_model.on_channel_monitor_enabled.emit(True)
                chan.channel_name_widget.set_active()
            else:
                chan.channel_model.on_channel_monitor_enabled.emit(False)
                chan.channel_name_widget.set_inactive()

    def switch_to_single_channel_display(self, channel_model, default_graph):
        self.monitor.stop_monitoring()
        self.on_switch_to_single_channel_display_clicked.emit(channel_model, default_graph)

