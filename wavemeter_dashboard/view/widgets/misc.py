from PyQt5.QtWidgets import QLabel, QSizePolicy, QAbstractButton, QPushButton
from PyQt5.QtGui import QPalette
from PyQt5.QtCore import pyqtSignal

from .flip_label import FlipLabel

# Most of the classes defined in this file are just the aliases of native Qt
# widgets. They are used solely to match the class selector in the stylesheet.
# I have tried my best to keep the layout definition inside the stylesheet, but
# sometimes it take more than the stylesheet to layout the widget, in this
# case, I will put the format code here to avoid polluting elsewhere.


class BigContentLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class TableHeaderLabel(QLabel):
    def __init__(self, parent):
        super(TableHeaderLabel, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class ChannelNameLabel(FlipLabel):
    def __init__(self, parent, channel_name="", channel_num=0, color=None):
        super().__init__(parent, channel_name, f"#{channel_num}")

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.color = color

        if self.color:
            self.change_background_color(color)

    def change_name(self, channel_name, channel_num):
        self.front = channel_name
        self.back = f"#{channel_num}"

    def change_background_color(self, color):
        self.setStyleSheet(f"background: rgb({color.red()}, {color.green()}, {color.blue()})")


class DialogTitleLabel(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)


class ErrorLabel(QLabel):
    clicked = pyqtSignal()

    def mousePressEvent(self, event):
        self.clicked.emit()


class ChannelLayoutPlaceholderLabel(QLabel):
    pass


class ChannelPlaceholderPromptLabel(QLabel):
    pass


class ToggleButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)

        self.setCheckable(True)


class MonitorEnableButton(ToggleButton):
    pass


class RedButton(QPushButton):
    pass


