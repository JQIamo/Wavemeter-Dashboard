import scipy.constants

from wavemeter_dashboard.util import convert_freq_for_display
from .flip_label import FlipLabel


class FreqWavelengthLabel(FlipLabel):
    def __init__(self, parent, freq=0):
        super().__init__(parent)

        self._frequency = freq
        self.error_text = ""

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, val):
        self.error_text = ""
        self._frequency = val
        self._update_text()

    @property
    def front(self):
        if self.error_text:
            return self.error_text

        if not self._frequency:
            return "---.------ THz"
        return convert_freq_for_display(self._frequency)

    @property
    def back(self):
        if self.error_text:
            return self.error_text

        if not self._frequency:
            return "---.------ nm"
        wavelength = scipy.constants.speed_of_light / self._frequency
        return f"{wavelength * 1e9:.6f} nm"

    def show_error(self, err):
        self.error_text = err
        self._update_text()

    def clear_error(self):
        self.error_text = ""
        self._frequency = 0
        self._update_text()
