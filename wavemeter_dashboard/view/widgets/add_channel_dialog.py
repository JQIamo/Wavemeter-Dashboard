from PyQt5.QtCore import pyqtSignal

from wavemeter_dashboard.view.widgets.dialog import Dialog, DialogStatus
from wavemeter_dashboard.view.widgets.channel_setup import ChannelSetup
from wavemeter_dashboard.model.channel_model import ChannelModel


class AddChannelDialog(Dialog):
    title = "ADD CHANNEL"

    on_apply = pyqtSignal(ChannelModel)

    def __init__(self, parent):
        super().__init__(parent)

    def init_widget(self):
        self.widget = ChannelSetup(self)
        self.ui.applyBtn.clicked.connect(self.on_apply_clicked)
        return self.widget

    def on_apply_clicked(self):
        ui = self.widget.ui

        chan_num = 0
        try:
            chan_num = int(ui.chanNumEdit.text())
        except ValueError:
            self.display_error("INVALID CHANNEL NUMBER")
            return

        chan_name = ui.chanNameEdit.text()
        if not chan_name:
            chan_name = f"#{chan_num}"

        model = ChannelModel(chan_num, chan_name)
        self.on_apply.emit(model)

        self.final_status = DialogStatus.OK
        self.close()
