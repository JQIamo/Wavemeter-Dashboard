from enum import Enum

from PyQt5.QtWidgets import QWidget
from .ui.ui_dashboard import Ui_dashboard
from .widgets.misc import *
from .widgets.add_channel_dialog import AddChannelDialog
from .widgets.color_strip import ColorStrips
from .channel_view import ChannelView
from wavemeter_dashboard.model.channel_model import ChannelModel
from wavemeter_dashboard.config import config


class ColumnType(Enum):
    NAME = 0
    FREQ = 1
    PATTERN = 2
    FREQ_LONGTERM = 3
    PID_ERROR_LONGTERM = 4
    PID_OUTPUT_LONGTERM = 5
    REMOVE = 6


column_name = {
    ColumnType.NAME: 'CHANNEL',
    ColumnType.FREQ: 'FREQ',
    ColumnType.PATTERN: 'INTERFEROMETER',
    ColumnType.FREQ_LONGTERM: 'FREQ LONGTERM',
    ColumnType.PID_ERROR_LONGTERM: 'ERR LONGTERM',
    ColumnType.PID_OUTPUT_LONGTERM: 'CTR OUTPUT LONGTERM',
    ColumnType.REMOVE: ' '
}


class Dashboard(QWidget):
    column_num_map = {
        ColumnType.NAME: 0,
        ColumnType.FREQ: 1,
        ColumnType.PATTERN: 2,
        ColumnType.FREQ_LONGTERM: 3,
        ColumnType.PID_ERROR_LONGTERM: 4,
        ColumnType.PID_OUTPUT_LONGTERM: 5,
        ColumnType.REMOVE: 6
    }

    row_height = 105
    vertical_spacing = 20
    horizontal_spacing = 40

    def __init__(self, parent, monitor):
        super().__init__(parent)

        self.channels = []
        self.color_strips = {}
        self.monitor = monitor

        self.pattern_max_amp = 0

        self.setAutoFillBackground(True)
        self.ui = Ui_dashboard()
        self.ui.setupUi(self)

        self.ui.channelGridLayout.setVerticalSpacing(self.vertical_spacing)
        self.ui.channelGridLayout.setHorizontalSpacing(self.horizontal_spacing)

        self._init_table_header()

        self.placeholder_prompt_label = None
        self._add_channel_placeholder()

        self.ui.addChannelBtn.clicked.connect(self.on_add_channel_clicked)
        self.ui.monBtn.clicked.connect(self.on_monitor_toggled)
        self.ui.saveSettingsBtn.clicked.connect(self.save_channel_settings)

        self.ui.monBtn.setEnabled(False)

        self.center_floating_widget = None

        self.monitor.on_monitoring_channel.connect(self.on_monitoring_channel)

        self.load_channels_from_config()

    def _init_table_header(self):
        for col, num in self.column_num_map.items():
            label = TableHeaderLabel(self)
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

    def load_channels_from_config(self):
        channels = config.get("channels")
        if channels:
            for chan in channels:
                model = ChannelModel.from_settings_dict(chan)
                self.add_channel(model)
            self.ui.monBtn.setEnabled(False)

    def add_channel(self, channel: ChannelModel):
        self.ui.addChannelBtn.setEnabled(True)
        self.ui.saveSettingsBtn.setText("SAVE*")
        self.ui.monBtn.setEnabled(True)

        view = ChannelView(self, channel)
        self._remove_channel_placeholder()
        self.channels.append(view)
        self.color_strips[channel.channel_num] = ColorStrips(self)
        self.monitor.add_channel(channel)

        for col_type, widget in [
            (ColumnType.NAME, view.channel_name_label),
            (ColumnType.FREQ, view.freq_label),
            (ColumnType.PATTERN, view.pattern),
            (ColumnType.FREQ_LONGTERM, view.freq_longterm),
            (ColumnType.PID_ERROR_LONGTERM, view.error_longterm),
            (ColumnType.PID_OUTPUT_LONGTERM, view.dac_longterm),
        ]:
            self.ui.channelGridLayout.addWidget(
                widget,
                len(self.channels),
                self.column_num_map[col_type]
            )
            widget.setFixedHeight(self.row_height)

        self.resize_color_strips()

    def on_add_channel_clicked(self):
        dialog = AddChannelDialog(self, self.monitor)
        self.ui.addChannelBtn.setEnabled(False)
        self.ui.monBtn.setEnabled(False)

        dialog.on_apply.connect(self.add_channel)
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
            y = channel.channel_name_label.y() - 0.5 * self.vertical_spacing
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
        for num, strip in self.color_strips.items():
            if num == channel_num:
                strip.show_info()
            else:
                strip.hide_info()
