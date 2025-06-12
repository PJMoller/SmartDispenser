import time
import digitalio

class HX711:
    def __init__(self, dout, pd_sck, gain=128):
        self.pSCK = pd_sck
        self.pOUT = dout

        self.pSCK.direction = digitalio.Direction.OUTPUT
        self.pOUT.direction = digitalio.Direction.INPUT

        self.GAIN = 0
        self.OFFSET = 0
        self.SCALE = 1

        self.set_gain(gain)

    def set_gain(self, gain):
        if gain == 128:
            self.GAIN = 1
        elif gain == 64:
            self.GAIN = 3
        elif gain == 32:
            self.GAIN = 2
        self.read_raw()

    def is_ready(self):
        return self.pOUT.value == 0

    def read_raw(self):
        while not self.is_ready():
            pass

        data = 0
        for _ in range(24):
            self.pSCK.value = True
            data = data << 1
            self.pSCK.value = False
            if self.pOUT.value:
                data += 1

        # set gain
        for _ in range(self.GAIN):
            self.pSCK.value = True
            self.pSCK.value = False

        if data & 0x800000:
            data |= ~0xffffff  # negative number

        return data

    def tare(self, times=10):
        sum = 0
        for _ in range(times):
            sum += self.read_raw()
        self.OFFSET = sum / times

    def set_scale(self, scale):
        self.SCALE = scale

    def get_units(self, times=1):
        sum = 0
        for _ in range(times):
            sum += self.read_raw()
        return (sum / times - self.OFFSET) / self.SCALE

