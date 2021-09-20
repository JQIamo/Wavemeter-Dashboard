from typing import Type, TYPE_CHECKING
import threading
from PyQt5.QtCore import pyqtSignal

from wavemeter_dashboard.view.widgets.dialog import Dialog, DialogStatus
from wavemeter_dashboard.view.widgets.channel_setup import ChannelSetup
from wavemeter_dashboard.model.channel_model import ChannelModel
from wavemeter_dashboard.controller.monitor import Monitor

if TYPE_CHECKING:
    from wavemeter_dashboard.view.dashboard import Dashboard


class AddChannelDialog(Dialog):
    title = "ADD CHANNEL"
    channel_range = (1, 16)

    on_apply = pyqtSignal(ChannelModel)
    _on_exposure_params_ready = pyqtSignal(int, int)

    def __init__(self, parent: 'Dashboard', monitor: Monitor):
        super().__init__(parent)
        self.monitor = monitor
        self.waitting_expo_param = False
        self._on_exposure_params_ready.connect(self.on_exposure_params_ready)

    def init_widget(self):
        self.widget = ChannelSetup(self)
        self.ui.applyBtn.clicked.connect(self.on_apply_clicked)
        self.widget.ui.autoExpoBtn.clicked.connect(self.on_auto_clicked)
        return self.widget

    def on_auto_clicked(self):
        ui = self.widget.ui

        chan_num = 0
        try:
            chan_num = int(ui.chanNumEdit.text())
            assert self.channel_range[0] <= chan_num <= self.channel_range[1]
        except (ValueError, AssertionError):
            self.display_error("INVALID CHANNEL NUMBER")
            return

        ui.autoExpoBtn.setText("WAIT...")
        ui.autoExpoBtn.setEnabled(False)
        ui.expoEdit.setEnabled(False)
        ui.expo2Edit.setEnabled(False)

        def run():
            expo, expo2 = self.monitor.get_auto_expo_params(chan_num)
            self._on_exposure_params_ready.emit(expo, expo2)
        
        threading.Thread(target=run).start()
        
    def on_exposure_params_ready(self, expo, expo2):
        ui = self.widget.ui
        ui.expoEdit.setText(f"{expo:d}")
        ui.expo2Edit.setText(f"{expo2:d}")

        ui.autoExpoBtn.setText("RUN")
        ui.autoExpoBtn.setEnabled(True)
        ui.expoEdit.setEnabled(True)
        ui.expo2Edit.setEnabled(True)

    def on_apply_clicked(self):
        ui = self.widget.ui

        chan_num = 0
        try:
            chan_num = int(ui.chanNumEdit.text())
            assert self.channel_range[0] <= chan_num <= self.channel_range[1]
        except (ValueError, AssertionError):
            self.display_error("INVALID CHANNEL NUMBER")
            return

        chan_name = ui.chanNameEdit.text()
        if not chan_name:
            chan_name = f"#{chan_num}"

        model = ChannelModel(chan_num, chan_name)

        try:
            model.expo_time = float(self.widget.ui.expoEdit.text())
        except ValueError:
            self.display_error("INVALID EXPO")

        try:
            model.expo2_time = float(self.widget.ui.expo2Edit.text())
        except ValueError:
            self.display_error("INVALID EXPO2")

        if self.widget.ui.pidBtn.isChecked():
            try:
                model.freq_setpoint = float(self.widget.ui.setpointEdit.text())
            except ValueError:
                self.display_error("INVALID FREQUENCY SETPOINT")

            try:
                model.pid_p_prop_val = float(self.widget.ui.pParamEdit.text())
            except ValueError:
                self.display_error("INVALID PID P PARAM")

            try:
                model.pid_i_prop_val = float(self.widget.ui.iParamEdit.text())
            except ValueError:
                self.display_error("INVALID PID I PARAM")

        self.on_apply.emit(model)

        self.final_status = DialogStatus.OK
        self.close()
