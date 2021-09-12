from PyQt5.QtChart import QChart, QChartView, QLineSeries, QValueAxis
from PyQt5.QtGui import QColor, QPen, QPainter
from PyQt5.QtCore import QRectF


class ThumbnailLineChart(QChartView):
    def __init__(self, parent):
        super().__init__(parent)

        self.setRenderHint(QPainter.Antialiasing)
        self.series = QLineSeries()
        self.chart = QChart()

        self.chart.legend().hide()
        self.chart.layout().setContentsMargins(0, 0, 0, 0)
        self.chart.setBackgroundRoundness(0)
        self.chart.setBackgroundVisible(False)

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

    def update_data(self, xs, ys):
        self.clear_series()

        for x, y in zip(xs, ys):
            self.series.append(x, y)

        self.chart.addSeries(self.series)

    def update_longterm_data(self, longterm_dict):
        self.clear_series()

        self._transfer_longterm_data(self.series.append, longterm_dict)

        self.chart.addSeries(self.series)

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

    @staticmethod
    def _transfer_longterm_data(append_method, var):
        assert 'index' in var and 'values' in var and 'time' in var

        count = len(var['values'])
        idx = var['index']

        for i in range(count):
            if idx == count:
                idx = 0

            append_method(var['time'][idx], var['values'][idx])
            idx += 1
