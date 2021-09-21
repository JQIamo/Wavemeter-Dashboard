from enum import Enum
from typing import List, Dict

from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QVBoxLayout
from PyQt5.QtCore import pyqtSignal, QObject
from pyqtgraph import PlotItem

from .ui.ui_single_channel_display import Ui_singleChannelView
from wavemeter_dashboard.controller.alert_tracker import AlertTracker
from wavemeter_dashboard.controller.monitor import Monitor
from .widgets.select_graph_dialog import SelectGraphDialog
from ..model.channel_model import ChannelModel
from ..model.graphable_data_provider import GraphableDataKind, \
    GraphableDataProvider, GRAPHABLE_DATA


class Graph(QObject):
    def __init__(self, parent: 'SingleChannelDisplay',
                 data_provider: GraphableDataProvider):
        super().__init__(parent)
        self.parent = parent
        self.data_provider = data_provider
        self.plot_item = PlotItem()
        self.plot_item.setLabels(left=(data_provider.y_axis_label,
                                       data_provider.y_axis_unit),
                                 bottom=(data_provider.x_axis_label,
                                         data_provider.x_axis_unit))
        self.plot = self.plot_item.plot()

        if data_provider.y_axis_scale != 1:
            self.plot.setScale(data_provider.y_axis_scale)

        self.parent.add_plot_item(self.plot_item)
        self.data_provider.new_data_signal.connect(self.update)

    def update(self):
        xs, ys = self.data_provider.get_data()
        self.plot.setData(xs, ys)

    def remove(self):
        self.parent.remove_plot_item(self.plot_item)


class SingleChannelDisplay(QWidget):
    on_switch_to_dashboard_clicked = pyqtSignal()

    def __init__(self, parent, monitor: Monitor, alert_tracker: AlertTracker, channel: ChannelModel):
        super().__init__(parent)

        self.monitor = monitor
        self.alert_tracker = alert_tracker
        self.channel = channel
        self.graphs: List[Graph] = []
        self.data_providers: Dict[GraphableDataKind, GraphableDataProvider] = {}

        self.ui = Ui_singleChannelView()
        self.ui.setupUi(self)

        self.ui.alertLabel.channel = channel
        self.ui.channelNameLabel.change_name(channel.channel_name, channel.channel_num)
        self.ui.channelNameLabel.change_background_color(channel.channel_color)
        self.ui.channelSetupWidget.setup(self.monitor, channel)

        self.ui.applyBtn.clicked.connect(self.on_channel_setup_applied)
        self.ui.resetBtn.clicked.connect(self.on_channel_setup_reset)
        self.ui.toDashboardBtn.clicked.connect(self.switch_back_to_dashboard)
        self.ui.selectGraphBtn.clicked.connect(self.on_select_graph_clicked)
        self.ui.monBtn.clicked.connect(self.on_monitor_toggled)

        self.channel.on_freq_changed.connect(self.update_frequency)
        self.channel.on_refresh_alert_display_requested.connect(
            self.ui.alertLabel.update)

        self._original_monitor_status = {}

        assert not monitor.is_monitoring()
        self._suppress_other_channel_update()
        monitor.start_monitoring()

    def _suppress_other_channel_update(self):
        for channel in self.monitor.channels.values():
            self._original_monitor_status[channel.channel_num] = channel.monitor_enabled
            channel.monitor_enabled = False
        self.channel.monitor_enabled = True

    def _restore_original_channel_monitoring_status(self):
        for channel in self.monitor.channels.values():
            channel.monitor_enabled = self._original_monitor_status[channel.channel_num]

    def update_frequency(self):
        self.ui.bigFreqLabel.frequency = self.channel.frequency

    def add_graph(self, graph_type: GraphableDataKind):
        if graph_type == GraphableDataKind.NONE:
            return

        assert graph_type not in self.data_providers
        data_provider = GRAPHABLE_DATA[graph_type](self.channel)
        graph = Graph(self, data_provider)

        self.data_providers[graph_type] = data_provider
        self.graphs.append(graph)

    def update_graphs(self, graph_kind_list):
        self.data_providers = {}
        for graph in self.graphs:
            graph.remove()
        self.graphs = []

        for graph_kind in graph_kind_list:
            self.add_graph(graph_kind)

    def add_plot_item(self, item: PlotItem):
        self.ui.graphicsView.nextRow()
        self.ui.graphicsView.addItem(item)

    def remove_plot_item(self, item: PlotItem):
        self.ui.graphicsView.removeItem(item)

    def on_channel_setup_applied(self):
        channel = self.channel = self.ui.channelSetupWidget.verify_and_make_model()
        self.ui.channelNameLabel.change_name(channel.channel_name, channel.channel_num)
        self.ui.channelNameLabel.change_background_color(channel.channel_color)
        # TODO: vertical line

    def on_channel_setup_reset(self):
        self.ui.channelSetupWidget.setup(self.monitor, self.channel)

    def on_select_graph_clicked(self):
        dialog = SelectGraphDialog(
            self,
            [graph.data_provider.kind for graph in self.graphs]
        )
        dialog.on_apply.connect(self.update_graphs)
        dialog.show()

    def switch_back_to_dashboard(self):
        self.monitor.stop_monitoring()
        self._restore_original_channel_monitoring_status()
        self.on_switch_to_dashboard_clicked.emit()

    def on_monitor_toggled(self, state):
        if state:
            self.monitor.start_monitoring()
        else:
            self.monitor.stop_monitoring()
