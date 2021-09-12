from PyQt5.QtWidgets import QLabel


class FlipLabel(QLabel):
    def __init__(self, parent, front="", back=""):
        super().__init__(parent)

        self._front = front
        self._back = back
        self.front_side = True

        if self._front:
            self.setText(self._front)

    @property
    def front(self):
        return self._front

    @front.setter
    def front(self, val):
        self._front = val
        self._update_text()

    @property
    def back(self):
        return self._back

    @back.setter
    def back(self, val):
        self._back = val
        self._update_text()

    def _update_text(self):
        if self.front_side:
            self.setText(self.front)
        else:
            self.setText(self.back)

    def mousePressEvent(self, event):
        self.front_side = not self.front_side

        self._update_text()

