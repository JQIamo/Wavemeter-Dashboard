import random
import numpy as np

from PyQt5.QtCore import pyqtSignal, QObject, QMetaMethod 
from PyQt5.QtGui import QColor

from wavemeter_dashboard.model.channel_alert import ChannelAlertCode, ChannelAlertAction
from wavemeter_dashboard.model.longterm_data import LongtermData

colors = [QColor(204, 0, 0),
          QColor(204, 102, 0),
          QColor(204, 204, 0),
          QColor(102, 204, 0),
          QColor(0, 204, 0),
          QColor(0, 204, 102),
          QColor(0, 204, 204),
          QColor(0, 102, 204),
          QColor(0, 0, 204),
          QColor(102, 0, 204),
          QColor(204, 0, 204),
          QColor(204, 0, 51)]


class ChannelModel(QObject):
    # signal for Monitor to notify the ChannelView
    on_name_changed = pyqtSignal()
    on_freq_changed = pyqtSignal()
    on_pattern_changed = pyqtSignal()
    on_wide_pattern_changed = pyqtSignal()
    on_pid_changed = pyqtSignal()
    on_reload = pyqtSignal()

    # signal for ChannelView to notify Monitor
    on_channel_monitor_enabled = pyqtSignal(bool)  # args: is_enabled
    on_channel_dac_reset = pyqtSignal()

    # signal from AlertTracker to ChannelView
    on_refresh_alert_display_requested = pyqtSignal()
    on_channel_alert_action_changed = pyqtSignal(ChannelAlertAction)

    # signal from Monitor to AlertTracker
    on_new_alert = pyqtSignal(ChannelAlertCode)
    on_alert_cleared = pyqtSignal(ChannelAlertCode)
    on_alert_clear_dismissed = pyqtSignal()

    # signal from ChannelView to AlertTracker
    on_alert_dismissed = pyqtSignal(ChannelAlertCode)

    def __init__(self, channel_num, channel_name=None, channel_color=None,
                 dac_channel_num=None):
        super().__init__()
        assert 1 <= channel_num <= 16
        self.channel_name = channel_name if channel_name else str(channel_num)
        self.channel_color = channel_color if channel_color else \
            colors[random.randint(0, len(colors) - 1)]

        # maintained by ChannelSetup
        self.channel_num = channel_num
        self.dac_channel_num = dac_channel_num
        self.expo_time = None
        self.expo2_time = None
        self.pid_enabled = False
        self.freq_setpoint = None
        self.pid_p_prop_val = None
        self.pid_i_prop_val = None

        self.error_alert_enabled = False
        self.dac_railed_alert_enabled = False
        self.wmt_alert_enabled = False

        # maintained by ChannelView
        self.monitor_enabled = False

        # maintained by Monitor
        self.frequency = None
        self.pattern_data = np.array([])
        self.wide_pattern_data = np.array([])
        self.freq_longterm_data = LongtermData()

        self.freq_max_error = None
        self.pid_i = 0
        self.pid_i_last_time = 0
        self.error = 0
        self.dac_longterm_data = LongtermData()
        self.dac_railed = False
        self.deviate_since = 0
        self.stable_since = 0

        # maintained by AlertTracker
        self.total_alerts = []
        self.dismissed_alerts = []
        self.active_alerts = []
        self.superseded_alerts = {}
        self.channel_alert_action = None
        
        self.on_pattern_changed_meta = self.get_meta_method_from_signal("on_pattern_changed")
        self.on_wide_pattern_changed_meta = self.get_meta_method_from_signal("on_wide_pattern_changed")

    def dump_settings_dict(self):
        return {
            'channel_num': self.channel_num,
            'channel_name': self.channel_name,
            'monitor_enabled': self.monitor_enabled,
            'dac_channel_num': self.dac_channel_num,
            'channel_color': [self.channel_color.red(),
                              self.channel_color.green(),
                              self.channel_color.blue()],
            'expo_time': self.expo_time,
            'expo2_time': self.expo2_time,
            'pid_enabled': self.pid_enabled,
            'freq_setpoint': self.freq_setpoint,
            'freq_max_error': self.freq_max_error,
            'pid_i_prop_val': self.pid_i_prop_val,
            'pid_p_prop_val': self.pid_p_prop_val
        }

    @staticmethod
    def from_settings_dict(_dict):
        color = QColor(_dict['channel_color'][0], _dict['channel_color'][1],
                       _dict['channel_color'][2])
        channel = ChannelModel(_dict['channel_num'], _dict['channel_name'],
                               color, _dict['dac_channel_num'])
        channel.monitor_enabled = _dict['monitor_enabled']
        channel.expo_time = _dict['expo_time']
        channel.expo2_time = _dict['expo2_time']
        channel.pid_enabled = _dict['pid_enabled']
        channel.freq_setpoint = _dict['freq_setpoint']
        channel.freq_max_error = _dict['freq_max_error']
        channel.pid_i_prop_val = _dict['pid_i_prop_val']
        channel.pid_p_prop_val = _dict['pid_p_prop_val']

        return channel
    
    def get_meta_method_from_signal(self, name):
        metaobj = self.metaObject()

        for i in range(metaobj.methodCount()):
            meta_method = metaobj.method(i)
            if meta_method.methodType() == QMetaMethod.Signal:
                _name = meta_method.name().data().decode('ascii')
                if _name == name:
                    return meta_method
        
        raise Exception("Unknown signal!")

