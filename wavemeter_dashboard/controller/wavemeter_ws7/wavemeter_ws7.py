from . import const
from . import api
from ctypes import c_double, c_long, c_ulong, c_ushort, byref, POINTER, cast
import numpy as np

DLL_PATH = "wlmData.dll"


class WavemeterWS7Exception(Exception):
    pass


class WavemeterWS7:
    def __init__(self, logger=None):
        try:
            api.LoadDLL(DLL_PATH)
        except Exception:
            raise WavemeterWS7Exception("Failed to load dll. Check the path.")

        if api.dll.GetWLMCount(0) == 0:
            raise WavemeterWS7Exception("There is no running wlmServer instance(s).")

        version_type = api.dll.GetWLMVersion(0)
        version_ver = api.dll.GetWLMVersion(1)
        version_rev = api.dll.GetWLMVersion(2)
        version_build = api.dll.GetWLMVersion(3)
        self.version = "%s.%s.%s.%s" % (version_type, version_ver,
                                        version_rev, version_build)

        self._pattern_wait_event_registered = False

    def get_frequency(self):
        frequency = api.dll.GetFrequency(0.0)
        if frequency == const.ErrWlmMissing:
            raise WavemeterWS7Exception("WLM inactive")
        elif frequency == const.ErrNoSignal:
            raise WavemeterWS7Exception('No Signal')
        elif frequency == const.ErrBadSignal:
            raise WavemeterWS7Exception('Bad Signal')
        elif frequency == const.ErrLowSignal:
            raise WavemeterWS7Exception('Low Signal')
        elif frequency == const.ErrBigSignal:
            raise WavemeterWS7Exception('High Signal')

        return frequency

    def get_temperature(self):
        temperature = api.dll.GetTemperature(0.0)
        if temperature <= const.ErrTemperature:
            raise WavemeterWS7Exception("Temperature: Not available")

        return temperature

    def get_pressure(self):
        pressure = api.dll.GetPressure(0.0)
        if pressure <= const.ErrTemperature:
            raise WavemeterWS7Exception("Pressure: Not available")

        return pressure

    def get_exposure(self):
        # Read exposure of CCD arrays, return value in ms
        exposure = api.dll.GetExposure(0)
        if exposure == const.ErrWlmMissing:
            raise WavemeterWS7Exception("Exposure: WLM not active")
        elif exposure == const.ErrNotAvailable:
            raise WavemeterWS7Exception("Exposure: Not available")

        return exposure

    def get_next_pattern(self, wide=False):
        if not self._pattern_wait_event_registered:
            # the last arg is timeout, -1 means keep waiting
            api.dll.Instantiate(const.cInstNotification,
                                const.cNotifyInstallWaitEvent,
                                c_long(-1), c_long(0))

        mode = c_long(0)
        intval = c_long(1)
        dblval = c_double(0)

        pattern_flag = const.cSignal1Interferometers if not wide else\
            const.cSignal1WideInterferometer

        while True:
            ret = api.dll.WaitForWLMEvent(byref(mode), byref(intval), byref(dblval))

            if mode.value == const.cmiPatternAnalysisWritten:
                break

        count = api.dll.GetPatternItemCount(pattern_flag)

        if count == 0:
            return None

        assert api.dll.GetPatternItemSize(pattern_flag) == 2

        patterns = (c_ushort * count)()
        unit_size = api.dll.GetPatternData(pattern_flag, cast(patterns, POINTER(c_ulong)))

        return np.frombuffer(patterns, dtype=np.ushort)

    def get_pattern(self, wide=False):
        if not self._pattern_wait_event_registered:
            # -1 means keep waiting no timeout (for WaitForWLMEvent)
            api.dll.Instantiate(const.cInstNotification,
                                const.cNotifyInstallWaitEvent,
                                c_long(-1), c_long(0))

        pattern_flag = const.cSignal1Interferometers if not wide else\
            const.cSignal1WideInterferometer

        count = api.dll.GetPatternItemCount(pattern_flag)

        if count == 0:
            return None

        assert api.dll.GetPatternItemSize(pattern_flag) == 2

        patterns = (c_ushort * count)()
        unit_size = api.dll.GetPatternData(pattern_flag, cast(patterns, POINTER(c_ulong)))

        return np.frombuffer(patterns, dtype=np.ushort)
