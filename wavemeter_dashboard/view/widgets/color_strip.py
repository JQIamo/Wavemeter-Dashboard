from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import QRect, QTimer


class ErrorBox(QLabel):
    pass


class InfoBox(QLabel):
    pass


class WarningBox(QLabel):
    pass


class ColorStrip:
    flash_timer = QTimer()

    def __init__(self, parent):
        self.info_box = InfoBox(parent)
        self.warning_box = InfoBox(parent)
        self.error_box = InfoBox(parent)

        self.info_box.setVisible(False)
        self.warning_box.setVisible(False)
        self.error_box.setVisible(False)

        self.error_flashing = False
        self.info_flashing = False
        self.warning_flashing = False

        self.flash_timer.timeout.connect(self._on_flashing)
        if not self.flash_timer.isActive():
            self.flash_timer.start(1000)

    def set_position(self, x, y, width, height):
        self.info_box.setGeometry(QRect(x, y, width, height))
        self.warning_box.setGeometry(QRect(x, y, width, height))
        self.error_box.setGeometry(QRect(x, y, width, height))

    def show_error(self):
        self.error_box.setVisible(True)
        self.error_box.lower()
        self.warning_box.lower()
        self.info_box.lower()

    def show_warning(self):
        self.warning_box.setVisible(True)
        self.warning_box.lower()
        self.info_box.lower()

    def show_info(self):
        self.info_box.show()
        self.info_box.lower()

    def hide(self):
        self.info_box.setVisible(False)
        self.warning_box.setVisible(False)
        self.error_box.setVisible(False)
        self.info_flashing = False
        self.warning_flashing = False
        self.error_flashing = False

    def hide_info(self):
        self.info_flashing = False
        self.info_box.setVisible(False)

    def hide_error(self):
        self.error_flashing = False
        self.error_box.setVisible(False)

    def hide_warning(self):
        self.warning_flashing = False
        self.warning_box.setVisible(False)

    def flash_error(self):
        self.error_flashing = True
        self.error_box.lower()
        self.warning_box.lower()
        self.info_box.lower()

    def flash_warning(self):
        self.warning_flashing = True
        self.warning_box.lower()
        self.info_box.lower()

    def flash_info(self):
        self.info_flashing = True
        self.info_box.lower()

    def stop_flashing(self):
        self.info_flashing = False
        self.warning_flashing = False
        self.error_flashing = False

    def _on_flashing(self):
        if self.error_flashing:
            self.error_box.setVisible(not self.error_box.isVisible())
        elif self.warning_flashing:
            self.warning_box.setVisible(not self.warning_box.isVisible())
        elif self.info_flashing:
            self.info_box.setVisible(not self.info_box.isVisible())
