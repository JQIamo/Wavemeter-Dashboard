from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QColor, QPen, QPainter
from PyQt5.QtCore import QRectF, Qt, QPointF

from wavemeter_dashboard.model.longterm_data import LongtermData


class ThumbnailLineChart(QChartView):
    def __init__(self, parent):
        super().__init__(parent)

        self.setRenderHint(QPainter.Antialiasing)
        self.series = QLineSeries()
        self._chart = QChart()
        self.lines = {}
        self._chart.addSeries(self.series)

        self._chart.legend().hide()
        self._chart.layout().setContentsMargins(0, 0, 0, 0)
        self._chart.setBackgroundRoundness(0)
        self._chart.setBackgroundVisible(False)

        self.x_min = 0
        self.x_max = 0

        self.x_axis = QValueAxis()
        self.y_axis = QValueAxis()
        self.x_axis.setLabelsVisible(False)
        self.x_axis.setGridLineVisible(False)
        self.x_axis.setLineVisible(False)
        self.y_axis.setLabelsVisible(False)
        self.y_axis.setGridLineVisible(False)
        self.y_axis.setLineVisible(False)
        self._chart.setAxisX(self.x_axis)
        self._chart.setAxisY(self.y_axis)

        pen = self.series.pen()
        pen.setWidth(1)
        pen.setColor(QColor("white"))
        self.series.setPen(pen)

        self.series.attachAxis(self.x_axis)
        self.series.attachAxis(self.y_axis)

        self.setChart(self._chart)

    def append_newest_point(self, x, y, points_limit=0):
        self._chart.removeSeries(self.series)

        if self.x_min == 0:
            self.x_min = x

        self.x_max = x

        if points_limit and self.series.count() >= points_limit:
            # remove first point
            self.series.remove(0)

        self.series.append(x, y)

        self._chart.addSeries(self.series)

    def update_data(self, xs, ys):
        self.clear_series()

        self.x_min = min(xs)
        self.x_max = max(xs)

        for x, y in zip(xs, ys):
            self.series.append(x, y)

        self._chart.addSeries(self.series)

    def update_longterm_data(self, longterm: LongtermData):
        self.clear_series()

        longterm.transfer_to(self.series.append)
        self.x_min, self.x_max = longterm.get_time_range()

        self._chart.addSeries(self.series)

    def add_vertical_line(self, name, pos, color, dash=False):
        if name in self.lines:
            self.remove_vertical_line(name)

        pen = QPen()
        pen.setWidth(1)
        pen.setColor(color)
        if dash:
            pen.setStyle(Qt.DashLine)

        self.lines[name] = (pos, pen)

    def remove_vertical_line(self, name):
        if name not in self.lines:
            return
        del self.lines[name]

    def clear_series(self):
        self._chart.removeSeries(self.series)
        self.series.clear()

    def set_x_display_range(self, x_min, x_max):
        self.x_min = x_min
        self.x_max = x_max
        self.x_axis.setRange(x_min, x_max)

    def set_y_display_range(self, y_min, y_max):
        self.y_axis(y_min, y_max)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._chart.setPlotArea(QRectF(0, 0,
                                       self.width(), self.height()))

    def drawForeground(self, painter, rect):
        # https://stackoverflow.com/questions/67591067/how-to-draw-a-vertical-line-at-specified-x-value-on-qhorizontalbarseries-qchart
        painter.save()

        for name, (pos, pen) in self.lines.items():
            pen.setWidth(1)
            painter.setPen(pen)
            p = self.chart().mapToPosition(QPointF(0, pos))
            r = self.chart().plotArea()
            p1 = QPointF(r.left(), p.y())
            p2 = QPointF(r.right(), p.y())
            painter.drawLine(p1, p2)

        painter.restore()

