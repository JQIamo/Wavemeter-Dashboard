from typing import List
from PyQt5.QtWidgets import QWidget, QListWidgetItem
from PyQt5.QtCore import Qt, pyqtSignal

from wavemeter_dashboard.model.graphable_data_provider import GraphableDataKind, \
    GraphableDataProvider, GRAPHABLE_DATA
from wavemeter_dashboard.view.ui.ui_data_select import Ui_dataSelect


class GraphDataSelectWidget(QWidget):
    def __init__(self, parent, selected_graphs: List[GraphableDataKind]):
        super().__init__(parent)

        self.selected = selected_graphs
        self.ui = Ui_dataSelect()
        self.ui.setupUi(self)

        self.ui.addBtn.clicked.connect(self.on_add_clicked)
        self.ui.deleteBtn.clicked.connect(self.on_delete_clicked)
        self.ui.upBtn.clicked.connect(self.on_up_clicked)
        self.ui.downBtn.clicked.connect(self.on_down_clicked)

        self._fill_candidate()
        self._fill_selected()

    def _fill_candidate(self):
        for option in GRAPHABLE_DATA.keys():
            if option not in self.selected:
                name = GRAPHABLE_DATA[option].name
                item = QListWidgetItem(name, self.ui.candidateList)
                item.setData(Qt.UserRole, option)

    def _fill_selected(self):
        for option in self.selected:
            name = GRAPHABLE_DATA[option].name
            item = QListWidgetItem(name, self.ui.selectedList)
            item.setData(Qt.UserRole, option)

    def on_add_clicked(self):
        row = self.ui.candidateList.currentRow()
        item = self.ui.candidateList.takeItem(row)
        self.ui.selectedList.addItem(item)

    def on_delete_clicked(self):
        row = self.ui.selectedList.currentRow()
        item = self.ui.selectedList.takeItem(row)
        self.ui.candidateList.addItem(item)

    def on_up_clicked(self):
        row = self.ui.selectedList.currentRow()
        if row > 0:
            item = self.ui.selectedList.takeItem(row)
            self.ui.selectedList.insertItem(row - 1, item)

    def on_down_clicked(self):
        row = self.ui.selectedList.currentRow()
        if row < self.ui.selectedList.count() - 1:
            item = self.ui.selectedList.takeItem(row)
            self.ui.selectedList.insertItem(row + 1, item)

    def get_selected_graph_list(self):
        ret = []

        for idx in range(self.ui.selectedList.count()):
            item = self.ui.selectedList.item(idx)
            kind = item.data(Qt.UserRole)

            ret.append(kind)

        return ret
