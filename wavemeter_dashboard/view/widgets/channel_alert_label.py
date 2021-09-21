from typing import List
from collections import namedtuple
from PyQt5.QtWidgets import QLabel, QMenu, QAction, QSizePolicy
from PyQt5.QtCore import Qt, pyqtProperty, pyqtSignal

from wavemeter_dashboard.model.channel_alert import ChannelAlert, ChannelAlertCode, CHANNEL_ALERTS, ChannelAlertAction
from wavemeter_dashboard.model.channel_model import ChannelModel


class ChannelAlertLabel(QLabel):
    def __init__(self, parent, channel_model: ChannelModel = None):
        super().__init__(parent)

        self._state = "normal"
        self.display_index = 0
        self.display_alert_code = None
        self.channel = channel_model

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setContextMenuPolicy(Qt.CustomContextMenu)

        self.customContextMenuRequested.connect(self.open_menu)

    @pyqtProperty(str)
    def state(self):
        return self._state

    @state.setter
    def state(self, val):
        self._state = val

    def update(self):
        self.display_index = 0

        if self.channel.active_alerts:
            self.display_alert_code = self.channel.active_alerts[0]
        else:
            if self.channel.dismissed_alerts:
                self.display_alert_code = self.channel.dismissed_alerts[0]
            else:
                self.display_alert_code = None

        self.display()

    def display(self):
        old_state = self._state

        if self.display_index < len(self.channel.active_alerts):
            alert_code = self.channel.active_alerts[self.display_index]
            alert = CHANNEL_ALERTS[alert_code]
            self.setText(alert.msg)

            if alert.action in [
                ChannelAlertAction.FLASH_ERROR,
                ChannelAlertAction.STATIC_ERROR
            ]:
                self.state = "error"
            elif alert.action in [
                ChannelAlertAction.FLASH_WARNING,
                ChannelAlertAction.STATIC_WARNING
            ]:
                self.state = "warning"
            else:
                self.state = "normal"
        elif self.display_index < len(self.channel.active_alerts) \
                + len(self.channel.dismissed_alerts):
            index = self.display_index - len(self.channel.dismissed_alerts)
            alert_code = self.channel.dismissed_alerts[index]
            alert = CHANNEL_ALERTS[alert_code]
            self.setText(alert.msg)
            self.state = "dismissed"
        else:
            self.setText("")
            self.state = "normal"

        if old_state != self._state:
            self.refresh_bg()

    def next_alert(self):
        print(self.channel.total_alerts, self.channel.active_alerts)
        if len(self.channel.active_alerts) == 0:
            return

        self.display_index += 1
        if self.display_index >= len(self.channel.active_alerts) \
                + len(self.channel.dismissed_alerts):
            self.display_index = 0

        self.display()

    def mousePressEvent(self, event):
        self.next_alert()

    def refresh_bg(self):
        self.style().unpolish(self)
        self.style().polish(self)

    def append_alert(self, alert: ChannelAlert):
        self.alerts.append(alert)
        self.display_index = len(self.alerts) - 1

        self.display()

    def remove_alert(self, alert: ChannelAlert):
        code = alert.code

        for idx, err in filter(lambda pair: pair[1].code == code,
                               enumerate(self.alerts)):
            if len(self.alerts) == 1:
                self.setText("")
                self.display_index = 0
            elif idx == self.display_index:
                self.next_alert()
            elif idx < self.display_index:
                self.display_index -= 1

            del self.alerts[idx]
            break

    def open_menu(self, point):
        if self.display_index < len(self.channel.active_alerts):
            menu = QMenu(self)
            dismiss_action = menu.addAction("DISMISS")
            action = menu.exec_(self.mapToGlobal(point))
            if action == dismiss_action:
                alert_code = self.channel.active_alerts[self.display_index]
                self.channel.on_alert_dismissed.emit(alert_code)
