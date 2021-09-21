from typing import TYPE_CHECKING, List

from wavemeter_dashboard.model.graphable_data_provider import GraphableDataKind
from wavemeter_dashboard.view.widgets.dialog import Dialog, DialogStatus
from PyQt5.QtCore import pyqtSignal

from wavemeter_dashboard.view.widgets.graph_data_select_widget import GraphDataSelectWidget

if TYPE_CHECKING:
    from wavemeter_dashboard.view.single_channel_display import SingleChannelDisplay


class SelectGraphDialog(Dialog):
    title = "SELECT GRAPH"

    on_apply = pyqtSignal(list)

    def __init__(self, parent: 'SingleChannelDisplay', selected_graphs: List[GraphableDataKind]):
        self.selected = selected_graphs if selected_graphs else []
        super().__init__(parent)

    def init_widget(self):
        self.widget = GraphDataSelectWidget(self, self.selected)
        self.ui.applyBtn.clicked.connect(self.on_apply_clicked)

        return self.widget

    def on_apply_clicked(self):
        new_selected = self.widget.get_selected_graph_list()
        self.on_apply.emit(new_selected)
        self.final_status = DialogStatus.OK
        self.close()
