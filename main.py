# This Python file uses the following encoding: utf-8
import sys
import os
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5.QtCore import Qt, QCoreApplication

from wavemeter_dashboard.view.dashboard import Dashboard
from wavemeter_dashboard.controller.monitor import Monitor
from wavemeter_dashboard.controller.wavemeter_ws7 import WavemeterWS7
from wavemeter_dashboard.controller.fiber_switch import FiberSwitch
from wavemeter_dashboard.controller.arduino_dac import DAC
from wavemeter_dashboard.util import solve_filepath
from wavemeter_dashboard import config


class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)


if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)
    app = QApplication([])
    window = MainWindow()

    config_path = solve_filepath("config.json")

    if os.path.exists(config_path):
        config.config.load_config(solve_filepath("config.json"))
    else:
        QMessageBox.critical(window, "Error",
                             f"Failed to load configuration file from "
                             f"{config_path}.")
        exit(1)

    style = solve_filepath("wavemeter_dashboard/view/ui/style.qss")
    with open(style) as f:
        window.setStyleSheet(f.read())

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
    dashboard = Dashboard(window, monitor)

    window.setCentralWidget(dashboard)

    window.show()
    sys.exit(app.exec_())
