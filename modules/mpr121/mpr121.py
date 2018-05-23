import smbus2


class Mpr121(object):

    # MPR121 registers
    _TOUCHSTATUS_L = 0x00
    _TOUCHSTATUS_H = 0x01
    _FILTDATA_0L = 0x04
    _FILTDATA_0H = 0x05
    _BASELINE_0 = 0x1E
    _MHDR = 0x2B
    _NHDR = 0x2C
    _NCLR = 0x2D
    _FDLR = 0x2E
    _MHDF = 0x2F
    _NHDF = 0x30
    _NCLF = 0x31
    _FDLF = 0x32
    _NHDT = 0x33
    _NCLT = 0x34
    _FDLT = 0x35
    _TOUCHTH_0 = 0x41
    _RELEASETH_0 = 0x42
    _DEBOUNCE = 0x5B
    _CONFIG1 = 0x5C
    _CONFIG2 = 0x5D
    _CHARGECURR_0 = 0x5F
    _CHARGETIME_1 = 0x6C
    _ECR = 0x5E
    _AUTOCONFIG0 = 0x7B
    _AUTOCONFIG1 = 0x7C
    _UPLIMIT = 0x7D
    _LOWLIMIT = 0x7E
    _TARGETLIMIT = 0x7F
    _GPIODIR = 0x76
    _GPIOEN = 0x77
    _GPIOSET = 0x78
    _GPIOCLR = 0x79
    _GPIOTOGGLE = 0x7A
    _SOFTRESET = 0x80

    ELECTRODES_COUNT = 12

    def __init__(self, i2c_address=0x5A, i2c_channel=1):
        self._i2c_address = i2c_address
        self._i2c_channel = i2c_channel
        self._bus = None

    def _write_reg(self, address, value):
        self.bus.write_byte_data(self._i2c_address, address, value)

    def _read_reg8(self, address):
        return self.bus.read_byte_data(self._i2c_address, address)

    def _read_reg16(self, address):
        return self.bus.read_word_data(self._i2c_address, address)

    def _set_threshholds(self, touch, release):
        for i in range(0, self.ELECTRODES_COUNT * 2, 2):
            self._write_reg(self._TOUCHTH_0 + i, touch)
            self._write_reg(self._RELEASETH_0 + i, release)

    def config_regs(self):
        # software reset
        self._write_reg(self._SOFTRESET, 0x63)
        # goto stand-by in order to write settings
        self._write_reg(self._ECR, 0x00)
        # set all electrodes threshholds
        self._set_threshholds(2, 2)
        # set filters
        self._write_reg(self._MHDR, 0x01)
        self._write_reg(self._NHDR, 0x01)
        self._write_reg(self._NCLR, 0x00)
        self._write_reg(self._FDLR, 0x00)
        self._write_reg(self._MHDF, 0x01)
        self._write_reg(self._NHDF, 0x01)
        self._write_reg(self._NCLF, 0xFF)
        self._write_reg(self._FDLF, 0x02)
        # 7 readings for touch and release
        self._write_reg(self._DEBOUNCE, 0x77)
        # charge electrodes with max current 63mA
        self._write_reg(self._CONFIG1, 63)
        # charge electrodes in 1us
        self._write_reg(self._CONFIG2, 0x40)
        # auto config baseline and filters
        self._write_reg(self._AUTOCONFIG0, 0x0F)
        self._write_reg(self._AUTOCONFIG1, 0x00)
        # set auto config values to ~700
        self._write_reg(self._UPLIMIT, 800 >> 2)
        self._write_reg(self._TARGETLIMIT, 700 >> 2)
        self._write_reg(self._LOWLIMIT, 600 >> 2)
        # enable 8 electrodes and goto run mode (must be the final register to config)
        self._write_reg(self._ECR, 0x88)

    def init(self):
        self.bus = smbus2.SMBus(self._i2c_channel)
        self.config_regs()

    def read_touch_bitmask(self):
        return self._read_reg16(self._TOUCHSTATUS_L) & 0x0FFF
