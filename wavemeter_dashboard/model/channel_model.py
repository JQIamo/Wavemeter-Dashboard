import random

from PyQt5.QtCore import pyqtSignal, QObject
from PyQt5.QtGui import QColor

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
    # signal to notify the frontend
    on_name_changed = pyqtSignal()
    on_freq_changed = pyqtSignal()
    on_pattern_changed = pyqtSignal()
    on_wide_pattern_changed = pyqtSignal()
    on_pid_changed = pyqtSignal()
    on_reload = pyqtSignal()

    # signal to notify the backend
    on_expo_settings_changed = pyqtSignal()
    on_pid_settings_changed = pyqtSignal()

    def __init__(self, channel_num, channel_name=None, channel_color=None,
                 dac_channel_num=None):
        super().__init__()
        assert 1 <= channel_num <= 16
        self.channel_num = channel_num
        self.dac_channel_num = dac_channel_num
        self.monitor_enabled = False

        self.channel_name = channel_name if channel_name else str(channel_num)
        self.channel_color = channel_color if channel_color else \
            colors[random.randint(0, len(colors) - 1)]

        self.pattern_enabled = True
        self.wide_pattern_enabled = False

        self.frequency = None
        self.pattern_data = None
        self.wide_pattern_data = None
        self.freq_longterm_data = LongtermData()

        self.expo_time = None
        self.expo2_time = None

        self.pid_enabled = False
        self.freq_setpoint = None
        self.freq_max_error = None
        self.pid_p_prop_val = None
        self.pid_i_prop_val = None
        self.pid_i = 0
        self.error = 0
        self.dac_output = 0
        self.dac_longterm_data = LongtermData()
        self.dac_railed = False

        # error tracker fields
        self.total_errors = []
        self.active_errors = []
        self.current_error_action = None

    def dump_settings_dict(self):
        return {
            'channel_num': self.channel_num,
            'channel_name': self.channel_name,
            'monitor_enabled': self.monitor_enabled,
            'dac_channel_num': self.dac_channel_num,
            'channel_color': [self.channel_color.red(),
                              self.channel_color.green(),
                              self.channel_color.blue()],
            'pattern_enabled': self.pattern_enabled,
            'wide_pattern_enabled': self.wide_pattern_enabled,
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
        channel.pattern_enabled = _dict['pattern_enabled']
        channel.wide_pattern_enabled = _dict['wide_pattern_enabled']
        channel.expo_time = _dict['expo_time']
        channel.expo2_time = _dict['expo2_time']
        channel.pid_enabled = _dict['pid_enabled']
        channel.freq_setpoint = _dict['freq_setpoint']
        channel.freq_max_error = _dict['freq_max_error']
        channel.pid_i_prop_val = _dict['pid_i_prop_val']
        channel.pid_p_prop_val = _dict['pid_p_prop_val']

        return channel
