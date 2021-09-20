import threading
from PyQt5.QtWidgets import QWidget
from PyQt5.QtCore import pyqtSignal

from ..ui.ui_channel_setup import Ui_channelSetup
from ...controller.monitor import Monitor
from ...model.channel_model import ChannelModel
from wavemeter_dashboard.util import convert_freq_for_forms, convert_freq_to_number


class ChannelSetupInvalidInputException(Exception):
    pass


class ChannelSetup(QWidget):
    channel_range = (1, 16)
    _on_exposure_params_ready = pyqtSignal(int, int)

    def __init__(self, parent, monitor: Monitor, channel: ChannelModel=None):
        super().__init__(parent)
        self.ui = Ui_channelSetup()
        self.ui.setupUi(self)
        self.monitor = monitor
        self.channel_model = channel
        self.ui.autoExpoBtn.clicked.connect(self.on_auto_clicked)
        self._on_exposure_params_ready.connect(self.on_exposure_params_ready)

        self.ui.removeChannelBtn.hide()

        if self.channel_model:
            ui = self.ui
            model = self.channel_model
            ui.chanNumEdit.setText(f"{model.channel_num:d}")
            ui.chanNameEdit.setText(model.channel_name)
            ui.expoEdit.setText(f"{model.expo_time:d}")
            ui.expo2Edit.setText(f"{model.expo2_time:d}")
            ui.pidBtn.setChecked(model.pid_enabled)

            if model.freq_setpoint:
                ui.setpointEdit.setText(convert_freq_for_forms(model.freq_setpoint))
            if model.freq_max_error:
                ui.errBoundEdit.setText(convert_freq_for_forms(model.freq_max_error))

            self.set_text_if_not_empty(ui.dacChanEdit, model.dac_channel_num)
            self.set_text_if_not_empty(ui.pParamEdit, model.pid_p_prop_val)
            self.set_text_if_not_empty(ui.iParamEdit, model.pid_i_prop_val)

    def on_auto_clicked(self):
        ui = self.ui

        chan_num = 0
        try:
            chan_num = int(ui.chanNumEdit.text())
            assert self.channel_range[0] <= chan_num <= self.channel_range[1]
        except (ValueError, AssertionError):
            raise ChannelSetupInvalidInputException("INVALID CHANNEL NUMBER")

        ui.autoExpoBtn.setText("WAIT...")
        ui.autoExpoBtn.setEnabled(False)
        ui.expoEdit.setEnabled(False)
        ui.expo2Edit.setEnabled(False)

        def run():
            expo, expo2 = self.monitor.get_auto_expo_params(chan_num)
            self._on_exposure_params_ready.emit(expo, expo2)

        threading.Thread(target=run).start()

    def on_exposure_params_ready(self, expo, expo2):
        ui = self.ui
        ui.expoEdit.setText(f"{expo:d}")
        ui.expo2Edit.setText(f"{expo2:d}")

        ui.autoExpoBtn.setText("RUN")
        ui.autoExpoBtn.setEnabled(True)
        ui.expoEdit.setEnabled(True)
        ui.expo2Edit.setEnabled(True)

    def verify_and_make_model(self):
        ui = self.ui

        chan_num = 0
        try:
            chan_num = int(ui.chanNumEdit.text())
            assert self.channel_range[0] <= chan_num <= self.channel_range[1]
        except (ValueError, AssertionError):
            raise ChannelSetupInvalidInputException("INVALID CHANNEL NUMBER")

        chan_name = ui.chanNameEdit.text()
        if not chan_name:
            chan_name = f"#{chan_num}"

        model = self.channel_model
        if not self.channel_model:
            model = ChannelModel(chan_num, chan_name)

        if self.channel_model:
            model.channel_color = self.channel_model.channel_color

        try:
            model.expo_time = int(self.ui.expoEdit.text())
        except ValueError:
            raise ChannelSetupInvalidInputException("INVALID EXPO")

        try:
            model.expo2_time = int(self.ui.expo2Edit.text())
        except ValueError:
            raise ChannelSetupInvalidInputException("INVALID EXPO2")

        model.pid_enabled = self.ui.pidBtn.isChecked()

        try:
            if model.pid_enabled or self.ui.setpointEdit.text():
                model.freq_setpoint = convert_freq_to_number(self.ui.setpointEdit.text())
        except ValueError:
            raise ChannelSetupInvalidInputException("INVALID FREQUENCY SETPOINT")

        try:
            if model.pid_enabled or self.ui.dacChanEdit.text():
                model.dac_channel_num = int(self.ui.dacChanEdit.text())
        except ValueError:
            raise ChannelSetupInvalidInputException("INVALID DAC CHANNEL")

        try:
            if model.pid_enabled or self.ui.pParamEdit.text():
                model.pid_p_prop_val = float(self.ui.pParamEdit.text())
        except ValueError:
            raise ChannelSetupInvalidInputException("INVALID PID P PARAM")

        try:
            if model.pid_enabled or self.ui.iParamEdit.text():
                model.pid_i_prop_val = float(self.ui.iParamEdit.text())
        except ValueError:
            raise ChannelSetupInvalidInputException("INVALID PID I PARAM")

        # alert section

        model.error_alert_enabled = self.ui.errAlertBtn.isChecked()
        model.dac_railed_alert_enabled = self.ui.dacRailedBtn.isChecked()
        model.wmt_alert_enabled = self.ui.wmtErrBtn.isChecked()

        try:
            if model.error_alert_enabled or self.ui.errBoundEdit.text():
                model.freq_max_error = convert_freq_to_number(
                    self.ui.errBoundEdit.text())
        except ValueError:
            raise ChannelSetupInvalidInputException("INVALID ERROR BOUND")

        return model

    @staticmethod
    def set_text_if_not_empty(edit, value):
        if value is not None:
            edit.setText(f"{value}")
