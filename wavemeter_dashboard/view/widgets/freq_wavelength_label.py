import scipy.constants

from .flip_label import FlipLabel


class FreqWavelengthLabel(FlipLabel):
    def __init__(self, parent, freq=0):
        super().__init__(parent)

        self._frequency = freq

    @property
    def frequency(self):
        return self._frequency

    @frequency.setter
    def frequency(self, val):
        self._frequency = val
        self._update_text()

    @property
    def front(self):
        if not self._frequency:
            return "---.------ THz"
        return f"{self._frequency / 1e12:.6f} THz"

    @property
    def back(self):
        if not self._frequency:
            return "---.------ nm"
        wavelength = scipy.constants.speed_of_light / self._frequency
        return f"{wavelength * 1e9:.6f} nm"
