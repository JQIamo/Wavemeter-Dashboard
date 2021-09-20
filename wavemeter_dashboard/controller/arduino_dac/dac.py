from serial import Serial


class DACOutOfBoundException(Exception):
    pass


class DAC:
    DAC_MIN = 0
    DAC_MAX = 32000

    def __init__(self, com_port, channel_num=16):
        self.channel_num = channel_num
        self.serial = Serial(com_port, 57600, timeout=200)

    def query(self, qry):
        self.write(qry)
        return self.serial.readline().rstrip()

    def write(self, w):
        self.serial.write(w.encode("utf-8") + b"\r\n")

    def is_railed(self, ch):
        return self.DAC_MIN <= self.get_dac_value(ch) < self.DAC_MAX

    def get_dac_value(self, ch):
        return int(self.query(f"Q {ch}"))

    def set_dac_inc(self, ch, inc):
        self.query(f"D {ch} {inc}")
        if self.DAC_MIN <= self.get_dac_value(ch) < self.DAC_MAX:
            raise DACOutOfBoundException
