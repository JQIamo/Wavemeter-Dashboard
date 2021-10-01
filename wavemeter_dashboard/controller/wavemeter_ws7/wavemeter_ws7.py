from . import const
from . import api
from ctypes import c_double, c_long, c_ulong, c_ushort, byref, POINTER, cast
import numpy as np

DLL_PATH = "wlmData.dll"


class WavemeterWS7Exception(Exception):
    pass


class WavemeterWS7BadSignalException(WavemeterWS7Exception):
    pass


class WavemeterWS7NoSignalException(WavemeterWS7Exception):
    pass


class WavemeterWS7LowSignalException(WavemeterWS7Exception):
    pass


class WavemeterWS7HighSignalException(WavemeterWS7Exception):
    pass


class WavemeterWS7:
    def __init__(self):
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
        api.dll.Operation(const.cCtrlStartMeasurement)

    def get_frequency(self):
        frequency = api.dll.GetFrequency(0.0)
        if frequency == const.ErrWlmMissing:
            raise WavemeterWS7Exception("WLM inactive")
        elif frequency == const.ErrNoSignal:
            raise WavemeterWS7NoSignalException
        elif frequency == const.ErrBadSignal:
            raise WavemeterWS7BadSignalException
        elif frequency == const.ErrLowSignal:
            raise WavemeterWS7LowSignalException
        elif frequency == const.ErrBigSignal:
            raise WavemeterWS7HighSignalException

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

    def is_auto_exposure(self):
        return api.dll.GetExposureMode()

    def set_auto_exposure(self, on):
        ret = api.dll.SetExposureMode(on)
        assert ret == 0, f"WLM Error: {self.error_msg_for_set_func(ret)}"

    def get_exposure(self):
        # Read exposure of CCD arrays, return value in ms
        exposure = api.dll.GetExposure(0)
        exposure2 = api.dll.GetExposure2(0)

        if exposure == const.ErrWlmMissing:
            raise WavemeterWS7Exception("Exposure: WLM not active")
        elif exposure == const.ErrNotAvailable:
            raise WavemeterWS7Exception("Exposure: Not available")

        return exposure, exposure2

    def set_exposure(self, expo, expo2):
        ret = api.dll.SetExposure(expo)
        if ret != 0:
            raise WavemeterWS7Exception(
                f"WLM Error: {self.error_msg_for_set_func(ret)}")

        ret = api.dll.SetExposure2(expo2)
        if ret != 0:
            raise WavemeterWS7Exception(
                f"WLM Error: {self.error_msg_for_set_func(ret)}")

    def get_next_pattern(self, wide=False):
        if not self._pattern_wait_event_registered:
            # the last arg is timeout, -1 means keep waiting
            api.dll.Instantiate(const.cInstNotification,
                                const.cNotifyInstallWaitEvent,
                                c_long(500), c_long(0))
            self._pattern_wait_event_registered = True                    

        mode = c_long(0)
        intval = c_long(1)
        dblval = c_double(0)

        pattern_flag = const.cSignal1Interferometers if not wide else \
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
                                c_long(500), c_long(0))
            self._pattern_wait_event_registered = True

        pattern_flag = const.cSignal1Interferometers if not wide else \
            const.cSignal1WideInterferometer

        count = api.dll.GetPatternItemCount(pattern_flag)

        if count == 0:
            return None

        assert api.dll.GetPatternItemSize(pattern_flag) == 2

        patterns = (c_ushort * count)()
        unit_size = api.dll.GetPatternData(pattern_flag, cast(patterns, POINTER(c_ulong)))

        return np.frombuffer(patterns, dtype=np.ushort)

    def error_msg_for_set_func(self, code):
        _lookup = {
            0: "ResERR_NoErr",
            -1: "ResERR_WlmMissing",
            -2: "ResERR_CouldNotSet",
            -3: "ResERR_ParmOutOfRange",
            -4: "ResERR_WlmOutOfResources",
            -5: "ResERR_WlmInternalError",
            -6: "ResERR_NotAvailable",
            -7: "ResERR_WlmBusy",
            -8: "ResERR_NotInMeasurementMode",
            -9: "ResERR_OnlyInMeasurementMode",
            -10: "ResERR_ChannelNotAvailable",
            -11: "ResERR_ChannelTemporarilyNotAvailable",
            -12: "ResERR_CalOptionNotAvailable",
            -13: "ResERR_CalWavelengthOutOfRange",
            -14: "ResERR_BadCalibrationSignal",
            -15: "ResERR_UnitNotAvailable",
            -16: "ResERR_FileNotFound",
            -17: "ResERR_FileCreation",
            -18: "ResERR_TriggerPending",
            -19: "ResERR_TriggerWaiting",
            -20: "ResERR_NoLegitimation",
        }

        return _lookup
