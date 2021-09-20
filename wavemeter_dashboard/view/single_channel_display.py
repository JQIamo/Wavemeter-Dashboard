from PyQt5.QtWidgets import QWidget, QLabel

from wavemeter_dashboard.controller.alert_tracker import AlertTracker
from wavemeter_dashboard.controller.monitor import Monitor


class SingleChannelDisplay(QWidget):
    def __init__(self, parent, monitor: Monitor, alert_tracker: AlertTracker):
        super().__init__(parent)

        self.monitor = monitor
        self.alert_tracker = alert_tracker

