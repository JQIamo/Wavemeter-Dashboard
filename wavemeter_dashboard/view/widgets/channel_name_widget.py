from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton
from PyQt5.QtCore import pyqtSignal
from ..ui.ui_channel_name_widget import Ui_ChannelNameWidget


class ChannelNameWidget(QWidget):
    on_mon_toggled = pyqtSignal(bool)
    on_set_clicked = pyqtSignal()

    def __init__(self, parent, channel_name, channel_num, color):
        super().__init__(parent)

        self.ui = Ui_ChannelNameWidget()
        self.ui.setupUi(self)

        self.set_name_color(channel_name, channel_num, color)

        self.ui.monBtn.clicked.connect(
            lambda e: self.on_mon_toggled.emit(self.ui.monBtn.isChecked()))
        self.ui.setBtn.clicked.connect(lambda e: self.on_set_clicked.emit())

    def set_name_color(self, channel_name, channel_num, color):
        self.ui.channNameLabel.change_name(channel_name, channel_num)
        self.ui.channNameLabel.change_background_color(color)

