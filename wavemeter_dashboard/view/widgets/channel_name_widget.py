from PyQt5.QtGui import QPainter, QColor, QPixmap, QPainterPath, QPolygonF
from PyQt5.QtCore import Qt, QPointF, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QPushButton, QSizePolicy
from ..ui.ui_channel_name_widget import Ui_ChannelNameWidget


class ChannelNameWidget(QWidget):
    on_mon_toggled = pyqtSignal(bool)
    on_set_clicked = pyqtSignal()

    def __init__(self, parent, channel_name, channel_num, color):
        super().__init__(parent)

        self.ui = Ui_ChannelNameWidget()
        self.ui.setupUi(self)

        sp = self.ui.indicatorLabel.sizePolicy()
        sp.setRetainSizeWhenHidden(True)
        self.ui.indicatorLabel.setSizePolicy(sp)
        self.ui.indicatorLabel.setVisible(False)

        self.ui.indicatorLabel.setMinimumWidth(25)
        self.ui.indicatorLabel.setMinimumHeight(50)
        self._draw_indicator()

        self.set_name_color(channel_name, channel_num, color)

        self.ui.monBtn.clicked.connect(
            lambda e: self.on_mon_toggled.emit(self.ui.monBtn.isChecked()))
        self.ui.setBtn.clicked.connect(lambda e: self.on_set_clicked.emit())

    def _draw_indicator(self):
        color = QColor(0, 204, 255)

        pix = QPixmap(20, 50)
        pix.fill(Qt.transparent)
        p = QPainter(pix)

        p.setRenderHint(QPainter.Antialiasing)

        polygon = QPolygonF()
        polygon << QPointF(0, 0) << QPointF(0, 50) << QPointF(20, 25)

        path = QPainterPath()
        path.addPolygon(polygon)

        p.setCompositionMode(QPainter.CompositionMode_Source)
        p.setBrush(color)
        p.drawPath(path)
        p.setCompositionMode(QPainter.CompositionMode_DestinationIn)

        p.end()

        self.ui.indicatorLabel.setPixmap(pix)

    def set_name_color(self, channel_name, channel_num, color):
        self.ui.channNameLabel.change_name(channel_name, channel_num)
        self.ui.channNameLabel.change_background_color(color)

    def btn_set_enable(self, enabled):
        self.ui.setBtn.setEnabled(enabled)

    def btn_mon_enable(self, enabled):
        self.ui.monBtn.setEnabled(enabled)

    def btn_mon_checked(self, checked):
        self.ui.monBtn.setChecked(checked)

    def is_btn_mon_checked(self):
        return self.ui.monBtn.isChecked()

    def set_active(self):
        self.ui.indicatorLabel.setVisible(True)

    def set_inactive(self):
        self.ui.indicatorLabel.setVisible(False)
