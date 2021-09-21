from typing import Type, TYPE_CHECKING
from PyQt5.QtCore import pyqtSignal

from wavemeter_dashboard.view.widgets.dialog import Dialog, DialogStatus
from wavemeter_dashboard.view.widgets.channel_setup_widget import ChannelSetupWidget, \
    ChannelSetupInvalidInputException
from wavemeter_dashboard.model.channel_model import ChannelModel
from wavemeter_dashboard.controller.monitor import Monitor

if TYPE_CHECKING:
    from wavemeter_dashboard.view.dashboard import Dashboard


class AddChannelDialog(Dialog):
    title = "ADD CHANNEL"

    on_apply = pyqtSignal(ChannelModel)
    on_remove_channel = pyqtSignal(int)  # args: channel_num

    def __init__(self, parent: 'Dashboard', monitor: Monitor, channel: ChannelModel = None):
        self.monitor = monitor
        self.channel_model = channel
        super().__init__(parent)

    def init_widget(self):
        self.widget = ChannelSetupWidget(self, self.monitor, self.channel_model)
        self.ui.applyBtn.clicked.connect(self.on_apply_clicked)

        return self.widget

    def show_remove_channel_button(self):
        assert self.channel_model
        self.widget.ui.removeChannelBtn.setVisible(True)
        self.widget.ui.removeChannelBtn.clicked.connect(
            lambda: self.on_remove_channel.emit(self.channel_model.channel_num))

    def on_apply_clicked(self):
        try:
            model = self.widget.verify_and_make_model()
            self.on_apply.emit(model)
            self.final_status = DialogStatus.OK
            self.close()
        except ChannelSetupInvalidInputException as e:
            self.display_error(e)
