from PyQt5.QtWidgets import QMainWindow, QScrollArea

from wavemeter_dashboard.config import config
from wavemeter_dashboard.controller.alert_tracker import AlertTracker
from wavemeter_dashboard.controller.monitor import Monitor
from wavemeter_dashboard.model.channel_model import ChannelModel
from wavemeter_dashboard.view.dashboard import Dashboard
from wavemeter_dashboard.view.single_channel_display import SingleChannelDisplay


class MainWindow(QMainWindow):
    def __init__(self, monitor: Monitor, alert_tracker: AlertTracker):
        QMainWindow.__init__(self)

        self.monitor = monitor
        self.alert_tracker = alert_tracker

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.setCentralWidget(self.scroll)

        self.dashboard = None
        self.single_channel_display = None

        self.channels = []
        channel_configs = config.get("channels", [])
        for chan in channel_configs:
            self.channels.append(ChannelModel.from_settings_dict(chan))

    def switch_to_dashboard(self):
        self.dashboard = Dashboard(self, self.monitor, self.alert_tracker, self.channels)
        self.dashboard.on_switch_to_single_channel_display_clicked.connect(
            self.switch_to_single_channel_display)
        self.dashboard.on_channel_list_update.connect(self.update_channels_from_dashboard)

        self.scroll.setWidget(self.dashboard)

        if self.single_channel_display:
            self.single_channel_display = None

    def update_channels_from_dashboard(self):
        if self.dashboard:
            self.channels = [channel_view.channel_model for channel_view in self.dashboard.channels]

    def switch_to_single_channel_display(self, channel, default_graph):
        self.single_channel_display = SingleChannelDisplay(
            self, self.monitor, self.alert_tracker, channel)
        self.single_channel_display.on_switch_to_dashboard_clicked.connect(
            self.switch_to_dashboard)
        self.single_channel_display.add_graph(default_graph)
        self.scroll.setWidget(self.single_channel_display)

        if self.dashboard:
            self.dashboard = None

    def show(self):
        if config.get("full_screen", False):
            super().showFullScreen()
        else:
            super().show()
            self.resize(1400, 700)
