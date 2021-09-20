import time
from threading import Thread, Lock, Condition
from functools import partial
from PyQt5.QtCore import pyqtSignal, QObject

from wavemeter_dashboard.controller.wavemeter_ws7 import WavemeterWS7, WavemeterWS7Exception
from wavemeter_dashboard.controller.fiber_switch import FiberSwitch
from wavemeter_dashboard.controller.arduino_dac import DAC, DACOutOfBoundException
from wavemeter_dashboard.config import config
from wavemeter_dashboard.model.channel_model import ChannelModel


class Monitor(QObject):
    on_monitor_started = pyqtSignal()
    on_monitor_stop_req = pyqtSignal()
    on_monitor_stopped = pyqtSignal()
    on_monitoring_channel = pyqtSignal(int)
    on_channel_error = pyqtSignal(str)

    def __init__(self, wavemeter: WavemeterWS7, fiberswitch: FiberSwitch, dac: DAC):
        super().__init__()
        self.wavemeter = wavemeter
        self.fiberswitch = fiberswitch
        self.dac = dac

        self.monitor_thread = None
        self.channels = {}

        self.stop_monitoring_flag = False
        self.monitoring_lock = Lock()
        self.monitor_stop_cv = Condition()

        self.last_monitored_channel = None

        self.after_switch_wait_time = config.get('after_switch_wait_time', 0.2)

    def start_monitoring(self):
        self.monitor_thread = Thread(name="monitor", target=self._monitor)
        self.monitor_thread.start()

    def _monitor(self):
        with self.monitoring_lock:
            self.wavemeter.set_auto_exposure(False)
            while not self.stop_monitoring_flag:
                for channel in self.channels.values():
                    if not channel.monitor_enabled:
                        continue

                    if self.stop_monitoring_flag:
                        break

                    self.on_monitoring_channel.emit(channel.channel_num)
                    self._update_one_channel(channel.channel_num)

        self.stop_monitoring_flag = False
        self.last_monitored_channel = None

        with self.monitor_stop_cv:
            self.monitor_stop_cv.notify_all()

    def _update_one_channel(self, channel_num):
        ch: ChannelModel = self.channels[channel_num]

        if not self.last_monitored_channel or self.last_monitored_channel != ch:
            self.fiberswitch.switch_channel(channel_num)
            time.sleep(0.2)

            self.wavemeter.set_exposure(ch.expo_time, ch.expo2_time)
            time.sleep(0.2)

            self.last_monitored_channel = ch
        else:
            time.sleep(0.2)  # stop the PC from burning

        try:
            ch.frequency = self.wavemeter.get_frequency()
        except WavemeterWS7Exception as e:
            self.on_channel_error.emit(f"Channel {channel_num} error: {e}")
            return

        ch.append_longterm_data(ch.freq_longterm_data, ch.frequency)

        if ch.freq_setpoint:
            ch.error = ch.frequency - ch.freq_setpoint

        ch.on_freq_changed.emit()

        if ch.pattern_enabled:
            ch.pattern_data = self.wavemeter.get_next_pattern()
            ch.on_pattern_changed.emit()

        if ch.wide_pattern_enabled:
            ch.wide_pattern_date = self.wavemeter.get_next_pattern(True)
            ch.on_wide_pattern_changed.emit()

        if ch.pid_enabled and ch.freq_setpoint:
            ch.pid_i += ch.error  # TODO: * delta
            prev_dac_output = self.dac.get_dac_value(ch.dac_channel_num)
            output = prev_dac_output + ch.pid_p_prop_val * ch.error + ch.pid_i_prop_val * ch.pid_i

            if self.dac.DAC_MIN <= output <= self.dac.DAC_MAX:
                self.dac.set_dac_value(ch.dac_channel_num, output)
                ch.dac_railed = False
            else:
                ch.dac_railed = True

            ch.dac_output = output
            ch.append_longterm_data(ch.dac_longterm_data, output)

            ch.on_pid_changed.emit()

    def get_auto_expo_params(self, channel_num):
        assert not self.monitoring_lock.locked()
        self.fiberswitch.switch_channel(channel_num)
        time.sleep(0.2)
        self.wavemeter.set_auto_exposure(True)
        time.sleep(1)
        exposure, exposure2 = self.wavemeter.get_exposure()
        return exposure, exposure2

    def stop_monitoring(self):
        if not self.monitoring_lock.locked():
            return

        self.stop_monitoring_flag = True
        with self.monitor_stop_cv:
            self.monitor_stop_cv.wait()  # TODO: timeout?

    def add_channel(self, channel):
        # should be called by the frontend
        self.channels[channel.channel_num] = channel

        return channel

    def remove_channel(self, channel_num):
        # should be called by the frontend
        assert channel_num in self.channels

        if self.channels[channel_num].monitor_enabled:
            self.stop_monitoring()

        del self.channels[channel_num]
