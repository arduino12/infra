import smbus2
import logging
import os.path
import subprocess


class MuxI2c(object):

    I2C_CHANNEL = 1
    bus = None
    _logger = logging.getLogger('mux_i2c')
    _I2C_BASE_ADDRESS = 0x70
    _BCM2708_SYSFS_RS_PATH = '/sys/module/i2c_bcm2708/parameters/combined'
    _muxes = {}

    def __init__(self, i2c_address, i2c_mux_index, mux_addr_off):
        self.i2c_address = i2c_address
        self.mux_addr = mux_addr_off
        self._io_msg = 'Failed %%s 0x%02X [0x%%02X] %%s bytes' % (i2c_address,)

        if self.bus is None:
            self.bus = smbus2.SMBus(self.I2C_CHANNEL)
            if os.path.exists(self._BCM2708_SYSFS_RS_PATH):
                # On the Raspberry Pi there is a bug where register reads
                # don't send a repeated start condition like the kernel smbus
                # I2C driver functions define. As a workaround this bit can be
                # changed to enable I2C repeated starts.
                # http://www.raspberrypi.org/forums/viewtopic.php?f=44&t=15840
                subprocess.check_call('chmod 666 {} && echo -n 1 > {}'.format(
                    self._BCM2708_SYSFS_RS_PATH), shell=True)

        if self.mux_addr is not None:
            self._io_msg += ', mux %s index %s' % (mux_addr_off, i2c_mux_index)
            self.mux_addr += self._I2C_BASE_ADDRESS
            self.mux_bitmask = 1 << i2c_mux_index
            if self.mux_addr not in self._muxes:
                self._muxes[self.mux_addr] = -1
                self._safe_write_mux(self.mux_addr, 0)

    def _safe_write_mux(self, mux_addr, mux_bitmask):
        if self._muxes[mux_addr] == mux_bitmask:
            return
        try:
            self.bus.write_byte(mux_addr, mux_bitmask)
        except Exception:
            self._logger.error(
                'Failed writing 0x%02X to mux 0x%02X', mux_bitmask, mux_addr)
        else:
            self._muxes[mux_addr] = mux_bitmask

    def _set_mux(self):
        if self.mux_addr is None:
            return
        for mux_addr in self._muxes:
            self._safe_write_mux(
                mux_addr, self.mux_bitmask if mux_addr == self.mux_addr else 0)

    def read(self, reg_address, size=1):
        self._set_mux()
        try:
            return self.bus.read_i2c_block_data(
                self.i2c_address, reg_address, size)
        except Exception:
            self._logger.error(self._io_msg, 'reading from', reg_address, size)
            return [0] * size

    def write(self, reg_address, data):
        self._set_mux()
        try:
            self.bus.write_i2c_block_data(self.i2c_address, reg_address, data)
        except Exception:
            self._logger.error(self._io_msg, 'writing to', reg_address, data)
