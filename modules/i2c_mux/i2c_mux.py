import smbus2
import os.path
import subprocess


class MuxI2c(object):

    I2C_CHANNEL = 1
    bus = None

    def __init__(self, i2c_address, i2c_mux_index):
        self.i2c_address = i2c_address
        self.i2c_mux_index = i2c_mux_index
        if self.bus is None:
            self.bus = smbus2.SMBus(self.I2C_CHANNEL)

            if os.path.exists('/sys/module/i2c_bcm2708/parameters/combined'):
                # On the Raspberry Pi there is a bug where register reads don't send a
                # repeated start condition like the kernel smbus I2C driver functions
                # define.  As a workaround this bit in the BCM2708 driver sysfs tree can
                # be changed to enable I2C repeated starts.
                # http://www.raspberrypi.org/forums/viewtopic.php?f=44&t=15840
                subprocess.check_call('chmod 666 /sys/module/i2c_bcm2708/parameters/combined', shell=True)
                subprocess.check_call('echo -n 1 > /sys/module/i2c_bcm2708/parameters/combined', shell=True)

    def read(self, reg_address, size=1):
        return self.bus.read_i2c_block_data(self.i2c_address, reg_address, size)

    def write(self, reg_address, data):
        self.bus.write_i2c_block_data(self.i2c_address, reg_address, data)
