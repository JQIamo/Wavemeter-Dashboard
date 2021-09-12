from PyQt5.QtWidgets import QPushButton, QHBoxLayout, QLabel
from PyQt5.QtGui import QColor, QIcon, QPixmap
from PyQt5.QtCore import QSize

inactive_color = QColor(51, 51, 51)
active_color = QColor(255, 140, 26)


class CheckButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)

        self.setCheckable(True)

        self.check_indicator = QPixmap(16, 16)
        self.check_indicator.fill(inactive_color)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(10, 0, 10, 0)
        self.setLayout(self.layout)
        self.label = QLabel(super().text())

        self.icon = QLabel()
        self.icon.setPixmap(self.check_indicator)

        self.layout.addWidget(self.icon)
        self.layout.addWidget(self.label)

        self.toggled.connect(self.on_toggled)

    def setText(self, text):
        self.label.setText(text)

    def text(self):
        return self.label.text()

    def on_toggled(self, state):
        if state:
            self.check_indicator.fill(active_color)
        else:
            self.check_indicator.fill(inactive_color)

        self.icon.setPixmap(self.check_indicator)
