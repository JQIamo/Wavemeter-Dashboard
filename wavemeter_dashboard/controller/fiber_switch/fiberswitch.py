from serial import Serial

class FiberSwitch:
    def __init__(self, com_port, channel_num=16):
        self.channel_num = channel_num
        self.serial = Serial(com_port, 57600, timeout=200)

        assert self.query("firmware?")  # check serial connection

    def query(self, qry):
        self.write(qry)
        return self.serial.readline().rstrip()

    def write(self, w):
        self.serial.write(w.encode("utf-8") + b"\r\n")

    def switch_channel(self, channel):
        assert isinstance(channel, int) and 1 <= channel <= self.channel_num
        self.write(f"ch{channel}")
        assert self.query_channel() == channel

    def query_channel(self):
        return int(self.query("ch?"))
