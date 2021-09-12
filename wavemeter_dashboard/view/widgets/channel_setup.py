from PyQt5.QtWidgets import QWidget

from ..ui.ui_channel_setup import Ui_channelSetup
from wavemeter_dashboard.view.widgets.dialog import Dialog


class ChannelSetup(QWidget):
    def __init__(self, parent: Dialog):
        super().__init__(parent)

        self.ui = Ui_channelSetup()
        self.ui.setupUi(self)
