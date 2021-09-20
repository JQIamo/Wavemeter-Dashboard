from typing import Dict
from itertools import chain
from functools import partial
from PyQt5.QtCore import pyqtSignal, QObject

from wavemeter_dashboard.model.channel_alert import (ChannelAlert,
                                                     ChannelAlertCode,
                                                     CHANNEL_ALERTS, ChannelAlertAction)
from wavemeter_dashboard.model.channel_model import ChannelModel


class AlertTracker(QObject):
    def __init__(self):
        super().__init__()

        self.channels: Dict[ChannelModel] = {}

    def add_channel(self, channel: ChannelModel):
        self.channels[channel.channel_num] = channel
        channel.on_new_alert.connect(partial(self.add_alert, channel.channel_num))
        channel.on_alert_dismissed.connect(partial(self.dismiss_alert, channel.channel_num))
        channel.on_alert_cleared.connect(partial(self.clear_alert, channel.channel_num))

    def add_alert(self, channel_num, alert_code: ChannelAlertCode):
        need_update = False
        channel = self.channels[channel_num]
        alert = CHANNEL_ALERTS[alert_code]

        if alert_code not in channel.total_alerts:
            # the new alert is not in total_alerts, so it must haven't been
            # dismissed, but it could be superseded by existed alerts
            channel.total_alerts.append(alert_code)

            # check if any existed alerts should be superseded
            to_be_superseded = []

            for _alert_code in channel.total_alerts:
                if _alert_code in alert.supersede:
                    to_be_superseded.append(_alert_code)

            if to_be_superseded:
                channel.superseded_alerts[alert_code] = to_be_superseded

                for to_remove in to_be_superseded:
                    if to_remove in channel.active_alerts:
                        channel.active_alerts.remove(to_remove)
                    elif to_remove in channel.dismissed_alerts:
                        channel.dismissed_alerts.remove(to_remove)

            # check if it is superseded by existed alerts:
            is_superseded = False
            for existed_alert_code in channel.total_alerts:
                supersede_list = CHANNEL_ALERTS[existed_alert_code].supersede
                if alert_code in supersede_list:
                    is_superseded = True
                    if existed_alert_code not in channel.superseded_alerts:
                        channel.superseded_alerts[existed_alert_code] = []
                    channel.superseded_alerts[existed_alert_code].append(alert_code)

            # isn't superseded:
            if not is_superseded:
                self._insert_into_active_alerts(channel, alert_code)
                need_update = True
            else:
                return

        elif alert_code not in channel.active_alerts:
            # in total_alerts but not in active_alerts,
            # it might have been dismissed, or superseded
            if alert_code in channel.dismissed_alerts:
                # if it has been dismissed, reactivate it
                self._insert_into_active_alerts(channel, alert_code)
                need_update = True
            else:
                # then it must have been superseded by something, in this case,
                # simply do nothing
                return
        else:
            # in total_alerts and in active_alerts
            # then rearrange order
            need_update = self._insert_into_active_alerts(channel, alert_code)

        if need_update:
            channel.on_refresh_alert_display_requested.emit()
            self.refresh_channel_action(channel)

    def clear_alert(self, channel_num, code: ChannelAlertCode):
        need_refresh = False
        channel = self.channels[channel_num]
        if code in channel.total_alerts:
            channel.total_alerts.remove(code)

        # if the alert is in the active list
        if code in channel.active_alerts:
            need_refresh = True
            channel.active_alerts.remove(code)
        elif code in channel.dismissed_alerts:
            # if not, then it might have been dismissed
            channel.dismissed_alerts.remove(code)

        # restore alerts superseded by it
        if code in channel.superseded_alerts:
            superseded = channel.superseded_alerts[code]
            del channel.superseded_alerts[code]

            for code in superseded:
                # ensure not superseded by other alerts
                if code not in chain(*channel.superseded_alerts.values()):
                    need_refresh = True
                    self._insert_into_active_alerts(channel, code)

        if need_refresh:
            channel.on_refresh_alert_display_requested.emit()
            self.refresh_channel_action(channel)

    def dismiss_alert(self, channel_num, code: ChannelAlertCode):
        channel = self.channels[channel_num]
        if code not in channel.active_alerts:
            return

        channel.active_alerts.remove(code)
        channel.dismissed_alerts.append(code)

        channel.on_refresh_alert_display_requested.emit()
        self.refresh_channel_action(channel)

    @staticmethod
    def refresh_channel_action(channel):
        if not channel.active_alerts:
            new_action = ChannelAlertAction.NOTHING
        else:
            new_action = CHANNEL_ALERTS[channel.active_alerts[0]].action

        if new_action != channel.channel_alert_action:
            channel.channel_alert_action = new_action
            channel.on_channel_alert_action_changed.emit(new_action)

    @staticmethod
    def _insert_into_active_alerts(channel, alert_code):
        alert = CHANNEL_ALERTS[alert_code]
        current_index = -1
        if alert_code in channel.active_alerts:
            current_index = channel.active_alerts.index(alert_code)

        idx_to_insert = len(channel.active_alerts)
        for idx, _alert_code in enumerate(channel.active_alerts):
            if CHANNEL_ALERTS[_alert_code].priority <= alert.priority:
                idx_to_insert = idx
                break
        if idx_to_insert != current_index:
            if current_index != -1:
                # insert position should always be smaller than current position
                assert idx_to_insert < current_index
                del channel.active_alerts[current_index]
            channel.active_alerts.insert(idx_to_insert, alert_code)
            return True  # active_alerts changed

        return False  # active_alerts unchanged
