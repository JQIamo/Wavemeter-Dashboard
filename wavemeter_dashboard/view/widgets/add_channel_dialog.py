from PyQt5.QtCore import pyqtSignal

from wavemeter_dashboard.view.widgets.dialog import Dialog, DialogStatus
from wavemeter_dashboard.view.widgets.channel_setup import ChannelSetup
from wavemeter_dashboard.model.channel_model import ChannelModel


class AddChannelDialog(Dialog):
    title = "ADD CHANNEL"
    channel_range = (1, 16)

    on_apply = pyqtSignal(ChannelModel)

    def __init__(self, parent):
        super().__init__(parent)

    def init_widget(self):
        self.widget = ChannelSetup(self)
        self.ui.applyBtn.clicked.connect(self.on_apply_clicked)
        self.widget.ui.autoExpoBtn.isClicked.connect(self.on_auto_clicked)
        return self.widget

    def on_auto_clicked(self):
        pass

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
            model.expo_time = float(self.widget.ui.expo2Edit.text())
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
