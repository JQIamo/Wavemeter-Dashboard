import time
from threading import Thread, Lock, Condition
from functools import partial
from PyQt5.QtCore import pyqtSignal

from wavemeter_dashboard.controller.wavemeter_ws7 import WavemeterWS7, WavemeterWS7Exception
from wavemeter_dashboard.controller.fiber_switch import FiberSwitch
from wavemeter_dashboard.controller.arduino_dac import DAC
from wavemeter_dashboard.config import config


class Monitor:
    on_monitor_started = pyqtSignal()
    on_monitor_stop_req = pyqtSignal()
    on_monitor_stopped = pyqtSignal()
    on_channel_error = pyqtSignal(str)

    def __init__(self, wavemeter: WavemeterWS7, fiberswitch: FiberSwitch, dac: DAC):
        self.wavemeter = wavemeter
        self.fiberswitch = fiberswitch
        self.dac = dac

        self.monitor_thread = None
        self.channels = {}

        self.stop_monitoring_flag = False
        self.monitoring_lock = Lock()
        self.monitor_stop_cv = Condition()

        self.monitored_channels = []

        self.after_switch_wait_time = config.get('after_switch_wait_time', 0.2)

    def start_monitoring(self):
        self.monitor_thread = Thread(name="monitor", target=self._monitor)
        self.monitor_thread.start()

    def _monitor(self):
        with self.monitoring_lock:
            while not self.stop_monitoring_flag:
                for channel in self.channels.values():
                    if channel.channel_num not in self.monitored_channels:
                        continue

                    if self.stop_monitoring_flag:
                        break

                    self._update_one_channel(channel.channel_num)

        self.stop_monitoring_flag = False

        with self.monitor_stop_cv:
            self.monitor_stop_cv.notify_all()

    def _update_one_channel(self, channel_num):
        ch = self.channels[channel_num]

        self.fiberswitch.switch_channel(channel_num)

        time.sleep(0.2)

        try:
            ch.frequency = self.wavemeter.get_frequency()
        except WavemeterWS7Exception as e:
            self.on_channel_error.emit(f"Channel {channel_num} error: {e}")
            return

        ch.append_longterm_data(ch.freq_longterm_data, ch.frequency)

        if ch.freq_setpoint:
            ch.error = ch.frequency - ch.freq_setpoint
            ch.append_longterm_data(ch.error_longterm_data,
                                    ch.error)

        ch.on_freq_changed.emit()

        if ch.pattern_enabled:
            ch.pattern_data = self.wavemeter.get_next_pattern()
            ch.on_pattern_changed.emit()

        if ch.wide_pattern_enabled:
            ch.wide_pattern_date = self.wavemeter.get_next_pattern(True)
            ch.on_wide_pattern_changed.emit()

        if ch.pid_enabled and ch.freq_setpoint:
            ch.pid_i += ch.error  # TODO: * delta
            prev_dac_output = ch.dac_output
            output = ch.pid_p_prop_val * ch.error + ch.pid_i_prop_val * ch.pid_i
            delta = ch.dac_output - prev_dac_output

            # try:
            self.dac.set_dac_inc(ch.dac_channel_num, delta)

            ch.dac_output = self.dac.get_dac_value(ch.dac_channel_num)
            ch.append_longterm_data(ch.dac_longterm_data, output)

            ch.on_pid_changed.emit()

    def get_auto_expo_params(self, channel):
        pass

    def stop_monitoring(self):
        if not self.monitoring_lock.locked():
            return

        self.stop_monitoring_flag = True
        with self.monitor_stop_cv:
            self.monitor_stop_cv.wait()  # TODO: timeout?

    def toggle_channel_monitoring_status(self, channel_num):
        assert channel_num in self.channels
        channel = self.channels[channel_num]

        if channel.monitor_enabled:
            assert channel_num in self.monitored_channels
            channel.monitor_enabled = False
            self.monitored_channels.remove(channel_num)
        else:
            assert channel_num not in self.monitored_channels
            channel.monitor_enabled = True
            self.monitored_channels.append(channel_num)

    def add_channel(self, channel):
        # should be called by the frontend
        self.channels[channel.channel_num] = channel

        channel.on_monitor_state_changed.connect(
            partial(self.toggle_channel_monitoring_status, channel.channel_num))
        self.monitored_channels.append(channel.channel_num)

        return channel

    def remove_channel(self, channel_num):
        # should be called by the frontend
        if channel_num in self.monitored_channels:
            self.stop_monitoring()
            self.monitored_channels.remove(channel_num)

        assert channel_num in self.channels

        del self.channels[channel_num]


