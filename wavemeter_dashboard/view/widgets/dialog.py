from typing import Type, TYPE_CHECKING
from enum import Enum

from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QPoint, pyqtSignal

from wavemeter_dashboard.view.ui.ui_dialog import Ui_dialog
from wavemeter_dashboard.view.widgets.misc import ErrorLabel

if TYPE_CHECKING:
    from wavemeter_dashboard.view.dashboard import Dashboard


class DialogStatus(Enum):
    CANCEL = 0
    OK = 1


class Dialog(QWidget):
    title = "Title"
    on_close = pyqtSignal(DialogStatus)

    def __init__(self, parent: 'Dashboard'):
        super().__init__(parent)

        self.setAttribute(Qt.WA_StyledBackground, True)

        self.error_label = ErrorLabel(self)
        self.error_label.hide()
        self.widget = None
        self.ui = Ui_dialog()
        self.ui.setupUi(self)

        self.ui.cancelBtn.clicked.connect(self.on_cancel_clicked)

        self.setup_widget()
        self.move_to_center()

        parent.center_floating_widget = self

        self.final_status = DialogStatus.CANCEL

    def set_ok_button_text(self, text):
        self.ui.applyBtn.setText(text)

    def show(self):
        super().show()

    def init_widget(self):
        pass

    def setup_widget(self):
        self.ui.titleLabel.setText(self.title)
        enclosing_widget = self.init_widget()

        # remove placeholder
        self.ui.dialogLayout.insertWidget(0, enclosing_widget)

        self.setMinimumHeight(enclosing_widget.height() + 130)
        self.setMinimumWidth(enclosing_widget.width() + 35)

    def move_to_center(self):
        parent = self.parentWidget()
        x = (parent.width() - self.width()) / 2
        y = (parent.height() - self.height()) / 2

        self.move(x, y)

    def close(self):
        parent = self.parentWidget()
        parent.center_floating_widget = None
        self.on_close.emit(self.final_status)
        super().close()
        self.setParent(None)

    def on_cancel_clicked(self):
        self.close()

    def display_error(self, text):
        self.error_label.setText(text)
        self.error_label.setMinimumWidth(self.width())
        self.error_label.move(0, (self.height() - self.error_label.height())/2)
        self.error_label.clicked.connect(lambda: self.error_label.hide())
        self.error_label.raise_()
        self.error_label.show()

