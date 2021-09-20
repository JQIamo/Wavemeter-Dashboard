from serial import Serial


class DACOutOfBoundException(Exception):
    pass


class DAC:
    DAC_MIN = 0
    DAC_MAX = 64000

    def __init__(self, com_port, channel_num=16):
        self.channel_num = channel_num
        self.serial = Serial(com_port, 115200, timeout=10)

    def query(self, qry):
        self.write(qry)
        return self.serial.readline().rstrip()

    def write(self, w):
        self.serial.write(w.encode("utf-8") + b"\n")

    def is_railed(self, ch):
        return self.DAC_MIN < self.get_dac_value(ch) < self.DAC_MAX

    def get_dac_value(self, ch):
        return int(self.query(f"Q {ch}"))

    def set_dac_value(self, ch, val):
        if val <= self.DAC_MIN:
            self.write(f"S {ch} {self.DAC_MIN}")
            raise DACOutOfBoundException
        elif val >= self.DAC_MAX:
            self.write(f"S {ch} {self.DAC_MAX}")
            raise DACOutOfBoundException

        self.write(f"S {ch} {val}")

    def set_dac_inc(self, ch, inc):
        self.write(f"D {ch} {inc}")
        if self.is_railed(ch):
            raise DACOutOfBoundException
