from typing import List
from enum import Enum


class ChannelAlertCode(Enum):
    WAVEMETER_UNKNOWN_ERROR = 0
    WAVEMETER_UNDER_EXPOSED = 1
    WAVEMETER_OVER_EXPOSED = 2
    WAVEMETER_NO_SIGNAL = 3
    WAVEMETER_BAD_SIGNAL = 4
    PID_DAC_UNKNOWN_ERROR = 5
    PID_ERROR_OUT_OF_BOUND_TEMPORAL = 6
    PID_ERROR_OUT_OF_BOUND_LASTING = 7
    PID_DAC_RAILED = 8
    IDLE = 9
    QUEUED_FOR_MONITORING = 10
    MONTIROING = 11
    PID_ENGAGED = 12
    PID_LOCKED = 13


class ChannelAlertAction(Enum):
    NOTHING = 0
    FLASH_WARNING = 1
    FLASH_ERROR = 2
    STATIC_WARNING = 3
    STATIC_ERROR = 4


class ChannelAlert:
    def __init__(self, code: ChannelAlertCode, alert_priority, alert_msg: str,
                 alert_action: ChannelAlertAction,
                 supersede: List[ChannelAlertCode] = None):
        self.code = code
        self.priority = alert_priority  # lowest: 0, highest: +infinity
        self.msg = alert_msg
        self.action = alert_action
        self.supersede = supersede


class ChannelWavemeterAlert(ChannelAlert):
    def __init__(self, code: ChannelAlertCode, alert_priority, alert_msg: str,
                 alert_action: ChannelAlertAction, wmt_label_alert_msg: str,
                 supersede: List[ChannelAlertCode] = None):
        super().__init__(code, alert_priority, alert_msg, alert_action, supersede)
        self.wmt_label_alert_msg = wmt_label_alert_msg


# RULES FOR DISPLAYING ALERTS:
#  - Alerts with highest priority to be displayed on the top
#  - Followed by alerts with less priorities,
#  - Alerts with the same priority sorted by their posting time
#  - One alert can supersede other alerts. When that alert is cleared, alerts
#    being superseded will be restored.
#  - Channel's alert behavior will be determined by the "action" defined in the
#    alert on the top.


CHANNEL_ALERTS = {
    ChannelAlertCode.WAVEMETER_UNKNOWN_ERROR: ChannelWavemeterAlert(
        ChannelAlertCode.WAVEMETER_UNKNOWN_ERROR,
        100,
        "WMT UNKNOWN ERR",
        ChannelAlertAction.FLASH_ERROR,
        "UNKNOWN ERR"
    ),
    ChannelAlertCode.WAVEMETER_UNDER_EXPOSED: ChannelWavemeterAlert(
        ChannelAlertCode.WAVEMETER_UNDER_EXPOSED,
        100,
        "UNDER EXPOSED",
        ChannelAlertAction.FLASH_ERROR,
        "UNDER EXPOSED"
    ),
    ChannelAlertCode.WAVEMETER_OVER_EXPOSED: ChannelWavemeterAlert(
        ChannelAlertCode.WAVEMETER_OVER_EXPOSED,
        100,
        "OVER EXPOSED",
        ChannelAlertAction.FLASH_ERROR,
        "OVER EXPOSED"
    ),
    ChannelAlertCode.WAVEMETER_NO_SIGNAL: ChannelWavemeterAlert(
        ChannelAlertCode.WAVEMETER_NO_SIGNAL,
        100,
        "WMT NO SIGNAL",
        ChannelAlertAction.FLASH_ERROR,
        "NO SIGNAL"
    ),
    ChannelAlertCode.WAVEMETER_BAD_SIGNAL: ChannelWavemeterAlert(
        ChannelAlertCode.WAVEMETER_BAD_SIGNAL,
        100,
        "WMT BAD SIGNAL",
        ChannelAlertAction.FLASH_ERROR,
        "BAD SIGNAL"
    ),
    ChannelAlertCode.PID_DAC_UNKNOWN_ERROR: ChannelAlert(
        ChannelAlertCode.PID_DAC_UNKNOWN_ERROR,
        90,
        "DAC UNKNOWN ERR",
        ChannelAlertAction.FLASH_ERROR
    ),
    ChannelAlertCode.PID_DAC_RAILED: ChannelAlert(
        ChannelAlertCode.PID_DAC_RAILED,
        90,
        "DAC RAILED",
        ChannelAlertAction.FLASH_ERROR
    ),
    ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_LASTING: ChannelAlert(
        ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_LASTING,
        80,
        "OUT OF LOCK",
        ChannelAlertAction.FLASH_ERROR,
        [ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_TEMPORAL]
    ),
    ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_TEMPORAL: ChannelAlert(
        ChannelAlertCode.PID_ERROR_OUT_OF_BOUND_TEMPORAL,
        70,
        "FREQ DEVIATING",
        ChannelAlertAction.FLASH_WARNING
    ),
    ChannelAlertCode.IDLE: ChannelAlert(
        ChannelAlertCode.IDLE,
        0,
        "IDLE",
        ChannelAlertAction.NOTHING
    ),
    ChannelAlertCode.QUEUED_FOR_MONITORING: ChannelAlert(
        ChannelAlertCode.QUEUED_FOR_MONITORING,
        0,
        "QUEUED",
        ChannelAlertAction.NOTHING,
        [ChannelAlertCode.IDLE]
    ),
    ChannelAlertCode.MONTIROING: ChannelAlert(
        ChannelAlertCode.MONTIROING,
        10,
        "MONITORING",
        ChannelAlertAction.NOTHING,
        [ChannelAlertCode.QUEUED_FOR_MONITORING,
         ChannelAlertCode.PID_ENGAGED,
         ChannelAlertCode.PID_LOCKED]
    ),
    ChannelAlertCode.PID_ENGAGED: ChannelAlert(
        ChannelAlertCode.PID_ENGAGED,
        10,
        "PID ENGAGED",
        ChannelAlertAction.NOTHING,
        [ChannelAlertCode.QUEUED_FOR_MONITORING]
    ),
    ChannelAlertCode.PID_LOCKED: ChannelAlert(
        ChannelAlertCode.PID_LOCKED,
        20,
        "LOCKED",
        ChannelAlertAction.NOTHING,
        [ChannelAlertCode.PID_ENGAGED]
    ),
}
