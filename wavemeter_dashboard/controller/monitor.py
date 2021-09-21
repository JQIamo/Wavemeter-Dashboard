from typing import Dict
import time
import numpy as np
from threading import Thread, Lock, Condition
from functools import partial
from PyQt5.QtCore import pyqtSignal, QObject

from wavemeter_dashboard.controller.wavemeter_ws7 import (
    WavemeterWS7, WavemeterWS7Exception,
    WavemeterWS7BadSignalException, WavemeterWS7LowSignalException,
    WavemeterWS7NoSignalException, WavemeterWS7HighSignalException)
from wavemeter_dashboard.controller.fiber_switch import FiberSwitch
from wavemeter_dashboard.controller.arduino_dac import DAC, DACOutOfBoundException
from wavemeter_dashboard.config import config
from wavemeter_dashboard.model.channel_alert import ChannelAlertCode
from wavemeter_dashboard.model.channel_model import ChannelModel


class Monitor(QObject):
    on_monitor_started = pyqtSignal()
    on_monitor_stop_req = pyqtSignal()
    on_monitor_stopped = pyqtSignal()
    on_monitoring_channel = pyqtSignal(int)
    on_channel_error = pyqtSignal(int, str)

    def __init__(self, wavemeter: WavemeterWS7, fiberswitch: FiberSwitch, dac: DAC):
        super().__init__()
        self.wavemeter = wavemeter
        self.fiberswitch = fiberswitch
        self.dac = dac

        self.monitor_thread = None
        self.channels: Dict[ChannelModel] = {}

        self.stop_monitoring_flag = False
        self.monitoring_lock = Lock()
        self.monitor_stop_cv = Condition()

        self.last_monitored_channel = None

        self.after_switch_wait_time = config.get('wait_time_after_switch', 0.2)
        self.deviate_warning_wait_time = config.get('wait_time_before_deviate_warning', 5)
        self.out_of_lock_error_wait_time = config.get('wait_time_before_out_of_lock_error', 10)
        self.locked_wait_time = config.get('wait_time_before_locked', 10)

    def start_monitoring(self):
        self.monitor_thread = Thread(name="Monitor", target=self._monitor, daemon=True)
        self.monitor_thread.start()
        self.on_monitor_started.emit()

    @staticmethod
    def before_monitoring_channel_setup(channel: ChannelModel):
        channel.on_new_alert.emit(ChannelAlertCode.QUEUED_FOR_MONITORING)

        if channel.pid_enabled:
            channel.on_new_alert.emit(ChannelAlertCode.PID_ENGAGED)

        channel.on_alert_cleared.emit(ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_TEMPORAL)
        channel.on_alert_cleared.emit(ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_LASTING)

        channel.pid_i = 0
        channel.deviate_since = 0
        channel.stable_since = 0

    def _monitor(self):
        with self.monitoring_lock:
            for channel in self.channels.values():
                if not channel.monitor_enabled:
                    continue

                self.before_monitoring_channel_setup(channel)

            self.wavemeter.set_auto_exposure(False)
            while not self.stop_monitoring_flag:
                for channel in self.channels.values():
                    if not channel.monitor_enabled:
                        continue

                    if self.stop_monitoring_flag:
                        break

                    # t = time.time()
                    self.on_monitoring_channel.emit(channel.channel_num)
                    channel.on_new_alert.emit(ChannelAlertCode.MONTIROING)
                    self._update_one_channel(channel.channel_num)
                    channel.on_alert_cleared.emit(ChannelAlertCode.MONTIROING)
                    # print(f"fps {1/(time.time() - t)}")

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
            self.last_monitored_channel = ch
        else:
            time.sleep(0.05)  # stop the PC from burning

        success = False
        max_attempts = 6
        for attempt in range(max_attempts - 1):
            # we don't know how long it needs for the wavemeter to settle down
            # let's try for 300ms
            try:
                ch.frequency = self.wavemeter.get_frequency() * 1e12
                success = True
                break
            except WavemeterWS7Exception as e:
                pass
            time.sleep(0.05)
        if not success:
            # last chance before throwing out errors
            try:
                ch.frequency = self.wavemeter.get_frequency() * 1e12
                success = True
            except WavemeterWS7NoSignalException:
                ch.on_new_alert.emit(ChannelAlertCode.WAVEMETER_NO_SIGNAL)
            except WavemeterWS7BadSignalException:
                ch.on_new_alert.emit(ChannelAlertCode.WAVEMETER_BAD_SIGNAL)
            except WavemeterWS7HighSignalException:
                ch.on_new_alert.emit(ChannelAlertCode.WAVEMETER_OVER_EXPOSED)
            except WavemeterWS7LowSignalException:
                ch.on_new_alert.emit(ChannelAlertCode.WAVEMETER_UNDER_EXPOSED)
            except WavemeterWS7Exception:
                ch.on_new_alert.emit(ChannelAlertCode.WAVEMETER_UNKNOWN_ERROR)
        
        if not success:
            return

        if ch.freq_setpoint:
            ch.error = ch.frequency - ch.freq_setpoint
            if ch.freq_max_error:
                if abs(ch.error) > ch.freq_max_error:
                    ch.stable_since = 0
                    if ch.deviate_since == 0:
                        ch.deviate_since = time.time()

                    time_elapsed = time.time() - ch.deviate_since
                    if time_elapsed > self.out_of_lock_error_wait_time:
                        if ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_LASTING \
                                not in ch.total_alerts:
                            ch.on_new_alert.emit(
                                ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_LASTING)
                    elif time_elapsed > self.deviate_warning_wait_time:
                        if ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_TEMPORAL\
                                not in ch.total_alerts:
                            ch.on_alert_cleared.emit(ChannelAlertCode.PID_LOCKED)
                            ch.on_new_alert.emit(
                                ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_TEMPORAL)
                else:
                    ch.deviate_since = 0
                    if ch.stable_since == 0:
                        ch.stable_since = time.time()
                        if ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_LASTING in ch.total_alerts or \
                                ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_TEMPORAL in ch.total_alerts:
                            ch.on_alert_cleared.emit(
                                ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_TEMPORAL)
                            ch.on_alert_cleared.emit(
                                ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_LASTING)

                    if time.time() - ch.stable_since > self.locked_wait_time:
                        if ChannelAlertCode.PID_LOCKED not in ch.total_alerts:
                            ch.on_new_alert.emit(ChannelAlertCode.PID_LOCKED)

        ch.freq_longterm_data.append(ch.frequency)
        ch.on_freq_changed.emit()

        if ch.isSignalConnected(ch.on_pattern_changed_meta):
            ch.pattern_data = self.wavemeter.get_next_pattern()
            ch.on_pattern_changed.emit()

        if ch.isSignalConnected(ch.on_wide_pattern_changed_meta):
            ch.wide_pattern_data = self.wavemeter.get_next_pattern(True)
            ch.on_wide_pattern_changed.emit()

        if ch.pid_enabled and ch.freq_setpoint:
            if ch.pid_i_last_time != 0:
                ch.pid_i += ch.error / 1e12 * time.time() - ch.pid_i_last_time
            prev_dac_output = self.dac.get_dac_value(ch.dac_channel_num)
            output = prev_dac_output + ch.pid_p_prop_val * ch.error / 1e12 + ch.pid_i_prop_val * ch.pid_i
            ch.pid_i_last_time = time.time()

            try:
                self.dac.set_dac_value(ch.dac_channel_num, output)
                if ChannelAlertCode.PID_DAC_RAILED in ch.total_alerts:
                    ch.on_alert_cleared.emit(ChannelAlertCode.PID_DAC_RAILED)
                ch.dac_railed = False
            except DACOutOfBoundException:
                ch.dac_railed = True
                if ChannelAlertCode.PID_DAC_RAILED not in ch.total_alerts:
                    ch.on_new_alert.emit(ChannelAlertCode.PID_DAC_RAILED)

            ch.dac_output = output
            ch.dac_longterm_data.append(output)

            ch.on_pid_changed.emit()

    def get_auto_expo_params(self, channel_num):
        with self.monitoring_lock:
            self.fiberswitch.switch_channel(channel_num)
            time.sleep(0.2)
            self.wavemeter.set_auto_exposure(True)
            time.sleep(1)
            exposure, exposure2 = self.wavemeter.get_exposure()
            return exposure, exposure2

    def stop_monitoring(self):
        if not self.monitoring_lock.locked():
            return
        self.on_monitor_stop_req.emit()

        self.stop_monitoring_flag = True
        with self.monitor_stop_cv:
            self.monitor_stop_cv.wait()

            for channel in self.channels.values():
                if channel.monitor_enabled:
                    channel.on_alert_cleared.emit(ChannelAlertCode.QUEUED_FOR_MONITORING)
                    channel.on_alert_cleared.emit(ChannelAlertCode.PID_ENGAGED)
                    channel.on_alert_cleared.emit(ChannelAlertCode.PID_LOCKED)
                    channel.on_alert_clear_dismissed.emit()

                    channel.on_new_alert.emit(ChannelAlertCode.IDLE)

            self.on_monitor_stopped.emit()

    def is_monitoring(self):
        return self.monitoring_lock.locked()

    def add_channel(self, channel: ChannelModel):
        # should be called by the frontend
        if channel.channel_num not in self.channels:
            self.channels[channel.channel_num] = channel
            channel.on_channel_monitor_enabled.connect(
                partial(self.on_channel_monitor_enabled, channel.channel_num)
            )
            channel.on_channel_dac_reset.connect(
                partial(self.reset_channel_dac, channel.channel_num)
            )

        return channel

    def on_channel_monitor_enabled(self, channel_num, enabled):
        if self.monitoring_lock.locked():
            channel = self.channels[channel_num]

            if enabled:
                channel.on_new_alert.emit(ChannelAlertCode.QUEUED_FOR_MONITORING)
                if channel.pid_enabled:
                    channel.on_new_alert.emit(ChannelAlertCode.PID_ENGAGED)
            else:
                channel.on_new_alert.emit(ChannelAlertCode.IDLE)

    def reset_channel_dac(self, channel_num):
        ch = self.channels[channel_num]
        self.dac.reset_dac(ch.dac_channel_num)

    def remove_channel(self, channel_num):
        # should be called by the frontend
        assert channel_num in self.channels

        if self.channels[channel_num].monitor_enabled:
            self.stop_monitoring()

        del self.channels[channel_num]
