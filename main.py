# This Python file uses the following encoding: utf-8
import sys
import os
import time
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox, QScrollArea
from PyQt5.QtCore import Qt, QCoreApplication, pyqtSignal

from wavemeter_dashboard.controller.alert_tracker import AlertTracker
from wavemeter_dashboard.model.channel_model import ChannelModel
from wavemeter_dashboard.view.dashboard import Dashboard
from wavemeter_dashboard.controller.monitor import Monitor
from wavemeter_dashboard.controller.wavemeter_ws7 import WavemeterWS7
from wavemeter_dashboard.controller.fiber_switch import FiberSwitch
from wavemeter_dashboard.controller.arduino_dac import DAC
from wavemeter_dashboard.util import solve_filepath
from wavemeter_dashboard import config
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
        channel_configs = config.config.get("channels", [])
        for chan in channel_configs:
            self.channels.append(ChannelModel.from_settings_dict(chan))

    def switch_to_dashboard(self):
        self.dashboard = Dashboard(self, monitor, alert_tracker, self.channels)
        self.dashboard.on_switch_to_single_channel_display_clicked.connect(
            self.switch_to_single_channel_display)

        self.scroll.setWidget(self.dashboard)

        if self.single_channel_display:
            self.single_channel_display = None

    def switch_to_single_channel_display(self, channel):
        self.single_channel_display = SingleChannelDisplay(
            self, monitor, alert_tracker, channel)
        self.single_channel_display.on_switch_to_dashboard_clicked.connect(
            self.switch_to_dashboard)
        self.scroll.setWidget(self.single_channel_display)

        if self.dashboard:
            self.dashboard = None


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication([])

    config_path = solve_filepath("config.json")

    if os.path.exists(config_path):
        config.config.load_config(solve_filepath("config.json"))
    else:
        QMessageBox.critical(QMainWindow(), "Error",
                             f"Failed to load configuration file from "
                             f"{config_path}.")
        exit(1)

    assert config.config.has("fiberswitch_com_port")
    assert config.config.has("dac_com_port")
    fbs_port = config.config.get("fiberswitch_com_port")
    dac_port = config.config.get("dac_com_port")

    wm = WavemeterWS7()
    fs = FiberSwitch(fbs_port)
    dac = DAC(dac_port)

    # wm = None
    # fs = None
    # dac = None

    monitor = Monitor(wm, fs, dac)
    alert_tracker = AlertTracker()

    window = MainWindow(monitor, alert_tracker)
    style = solve_filepath("wavemeter_dashboard/view/ui/style.qss")
    with open(style) as f:
        window.setStyleSheet(f.read())

    if config.config.get("full_screen", False):
        window.showFullScreen()
    else:
        window.show()
        window.resize(1400, 700)

    window.switch_to_dashboard()

    sys.exit(app.exec_())
