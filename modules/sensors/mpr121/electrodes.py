from . import mpr121
from infra.core import utils
from infra.modules.i2c_mux import i2c_mux


class Electrode(object):

    ST_RELEASED = 0
    ST_NEWLY_TOUCHED = 1
    ST_TOUCHED = 2
    ST_NEWLY_RELEASED = 3

    NEXT_STATUS = {
        True: [ST_NEWLY_TOUCHED, ST_TOUCHED, ST_TOUCHED, ST_NEWLY_TOUCHED],
        False: [ST_RELEASED, ST_NEWLY_RELEASED, ST_NEWLY_RELEASED, ST_RELEASED]
    }

    def __init__(self):
        self.status = self.ST_RELEASED

    def _set_touched(self, touched):
        self.status = self.NEXT_STATUS[bool(touched)][self.status]

    def is_released(self):
        return self.status == self.ST_RELEASED or \
            self.status == self.ST_NEWLY_RELEASED

    def is_newly_touched(self):
        return self.status == self.ST_NEWLY_TOUCHED

    def is_touched(self):
        return self.status == self.ST_TOUCHED or \
            self.status == self.ST_NEWLY_TOUCHED

    def is_newly_released(self):
        return self.status == self.ST_NEWLY_RELEASED


class Electrodes(object):

    def __init__(self, elec_count):
        self.electrodes = []
        self.elec_count = elec_count

        for i in range(self.elec_count):
            e = Electrode()
            e.index = i
            self.electrodes.append(e)

    def _update(self, electrodes):
        for i in self.electrodes:
            i._set_touched()

    def _filter_by(self, func):
        return [i for i in self.electrodes if func(i)]

    def get_released(self):
        return self._filter_by(Electrode.is_released)

    def get_newly_touched(self):
        return self._filter_by(Electrode.is_newly_touched)

    def get_touched(self):
        return self._filter_by(Electrode.is_touched)

    def get_newly_released(self):
        return self._filter_by(Electrode.is_newly_released)


class Mpr121Electrodes(Electrodes):

    def __init__(self, mpr121_map):
        self.mprs = []
        elec_count = 0
        for mux_addr, mux_idx, dev_addr, elec_map in mpr121_map:
            elec_map_len = len(elec_map)
            dev = i2c_mux.MuxI2c(
                mpr121.Mpr121._I2C_BASE_ADDRESS + dev_addr, mux_idx, mux_addr)
            mpr = mpr121.Mpr121(dev, elec_map_len)
            mpr.elec_map = elec_map
            elec_count += elec_map_len
            self.mprs.append(mpr)
        self._all_mprs_dev = utils.Atter()
        self._all_mprs_dev.read = self._all_mprs_read
        self._all_mprs_dev.write = self._all_mprs_write
        self.all_mprs = mpr121.Mpr121(self._all_mprs_dev, elec_map_len)
        self.all_mprs.config_regs()
        Electrodes.__init__(self, elec_count)

    def _all_mprs_read(self, reg_address, size=1):
        return self.mprs[0]._dev.read(reg_address, size)

    def _all_mprs_write(self, reg_address, data):
        for mpr in self.mprs:
            mpr._dev.write(reg_address, data)

    def init(self):
        for mpr in self.mprs:
            mpr.config_regs()

    def update(self):
        bitmasks = [mpr._dev.read(0x00, 1)[0] for mpr in self.mprs]
        for bitmask, mpr in zip(bitmasks, self.mprs):
            for i in mpr.elec_map:
                self.electrodes[i]._set_touched(bitmask & 1)
                bitmask >>= 1


class Mpr121ElectrodesGrid(Mpr121Electrodes):

    def __init__(self, mpr121_map, grid_sizes, pixel_sizes):
        self.grid_sizes = grid_sizes
        self.pixel_sizes = pixel_sizes
        self.elec_pixel_sizes = (
            self.pixel_sizes[0] // self.grid_sizes[0],
            self.pixel_sizes[1] // self.grid_sizes[1])

        Mpr121Electrodes.__init__(self, mpr121_map)

        for i in self.electrodes:
            i.grid_indexes = (
                i.index % self.grid_sizes[0], i.index // self.grid_sizes[0])
            i.top_left_pixel = (
                i.grid_indexes[0] * self.elec_pixel_sizes[0],
                i.grid_indexes[1] * self.elec_pixel_sizes[1])
            i.mid_pixel = (
                i.top_left_pixel[0] + self.elec_pixel_sizes[0] // 2,
                i.top_left_pixel[1] + self.elec_pixel_sizes[1] // 2)
