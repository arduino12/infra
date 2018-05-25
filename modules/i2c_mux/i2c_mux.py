import smbus2


class MuxI2c(object):

    I2C_CHANNEL = 1
    bus = None

    def __init__(self, i2c_address, i2c_mux_index):
        self.i2c_address = i2c_address
        self.i2c_mux_index = i2c_mux_index
        if self.bus is None:
            self.bus = smbus2.SMBus(self.I2C_CHANNEL)

    def read(self, reg_address, size=1):
        return self.bus.read_i2c_block_data(self.i2c_address, reg_address, size)

    def write(self, reg_address, data):
        self.bus.write_i2c_block_data(self.i2c_address, reg_address, data)
