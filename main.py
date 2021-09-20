# This Python file uses the following encoding: utf-8
import sys
import os
from PyQt5.QtWidgets import (QApplication, QMainWindow, QMessageBox, QScrollArea,
                             QStackedWidget)
from PyQt5.QtCore import Qt, QCoreApplication

from wavemeter_dashboard.controller.alert_tracker import AlertTracker
from wavemeter_dashboard.view.dashboard import Dashboard
from wavemeter_dashboard.controller.monitor import Monitor
from wavemeter_dashboard.controller.wavemeter_ws7 import WavemeterWS7
from wavemeter_dashboard.controller.fiber_switch import FiberSwitch
from wavemeter_dashboard.controller.arduino_dac import DAC
from wavemeter_dashboard.util import solve_filepath
from wavemeter_dashboard import config


class MainWindow(QMainWindow):
    def __init__(self, monitor: Monitor, alert_tracker: AlertTracker):
        QMainWindow.__init__(self)

        self.stack = QStackedWidget(self)

        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.dashboard = Dashboard(self, monitor, alert_tracker)
        self.stack.addWidget(self.dashboard)

        self.scroll.setWidget(self.stack)

        self.setCentralWidget(self.scroll)


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

    # wm = WavemeterWS7()
    # fs = FiberSwitch(fbs_port)
    # dac = DAC(dac_port)

    wm = None
    fs = None
    dac = None

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

    sys.exit(app.exec_())
