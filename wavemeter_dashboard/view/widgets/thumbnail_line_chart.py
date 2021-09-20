from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QColor, QPen, QPainter
from PyQt5.QtCore import QRectF, Qt

from wavemeter_dashboard.model.longterm_data import LongtermData


class ThumbnailLineChart(QChartView):
    def __init__(self, parent):
        super().__init__(parent)

        self.setRenderHint(QPainter.Antialiasing)
        self.series = QLineSeries()
        self.chart = QChart()
        self.lines = {}

        self.chart.legend().hide()
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        self.chart.setBackgroundRoundness(0)
        self.chart.setBackgroundVisible(False)

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
        self.chart.setAxisX(self.x_axis)
        self.chart.setAxisY(self.y_axis)

        pen = self.series.pen()
        pen.setWidth(1)
        pen.setColor(QColor("white"))
        self.series.setPen(pen)

        self.chart.addSeries(self.series)

        self.setChart(self.chart)

    def append_newest_point(self, x, y, points_limit=0):
        assert x > self.x_max
        self.chart.removeSeries(self.series)

        if self.x_min == 0:
            self.x_min = x

        self.x_max = x

        if points_limit and self.series.count() >= points_limit:
            # remove first point
            self.series.remove(0)

        self.series.append(x, y)

        self.chart.addSeries(self.series)
        self.update_vertical_lines()

    def update_data(self, xs, ys):
        self.clear_series()

        self.x_min = min(xs)
        self.x_max = max(xs)

        for x, y in zip(xs, ys):
            self.series.append(x, y)

        self.chart.addSeries(self.series)
        self.update_vertical_lines()

    def update_longterm_data(self, longterm: LongtermData):
        self.clear_series()

        longterm.transfer_to(self.series.append)
        self.x_min, self.x_max = longterm.get_time_range()

        self.chart.addSeries(self.series)

    def add_vertical_line(self, name, pos, color, dash=False):
        if name in self.lines:
            self.remove_vertical_line(name)

        series = QLineSeries()
        pen = series.pen()
        pen.setWidth(1)
        pen.setColor(color)
        if dash:
            pen.setStyle(Qt.DashLine)
        series.setPen(pen)
        self.lines[name] = (pos, series)
        series.append(self.x_min, pos)
        series.append(self.x_max, pos)
        self.chart.addSeries(series)

    def update_vertical_lines(self):
        for name, (pos, series) in self.lines:
            self.chart.removeSeries(series)
            series.clear()
            series.append(self.x_min, pos)
            series.append(self.x_max, pos)
            self.chart.addSeries(series)

    def remove_vertical_line(self, name):
        if name not in self.lines:
            return
        self.chart.removeSeries(self.lines[name][1])
        del self.lines[name]

    def clear_series(self):
        self.chart.removeSeries(self.series)
        self.series.clear()

    def set_x_display_range(self, x_min, x_max):
        self.x_axis.setRange(x_min, x_max)

    def set_y_display_range(self, y_min, y_max):
        self.y_axis(y_min, y_max)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.chart.setPlotArea(QRectF(0, 0,
                                      self.width(), self.height()))
