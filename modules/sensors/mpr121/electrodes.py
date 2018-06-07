# from infra.core import utils utils.bits_list(i, 8)
from infra.modules.sensors.mpr121 import mpr121


class Electrode(object):

    STATUS_RELEASED = 0
    STATUS_NEWLY_TOUCHED = 1
    STATUS_TOUCHED = 2
    STATUS_NEWLY_RELEASED = 3

    NEXT_STATUS = {
        False: [STATUS_RELEASED, STATUS_NEWLY_RELEASED, STATUS_NEWLY_RELEASED, STATUS_RELEASED],
        True: [STATUS_NEWLY_TOUCHED, STATUS_TOUCHED, STATUS_TOUCHED, STATUS_NEWLY_TOUCHED],
    }

    def __init__(self):
        self.status = self.STATUS_RELEASED

    def _set_touched(self, touched):
        self.status = self.NEXT_STATUS[bool(touched)][self.status]

    def is_released(self):
        return self.status == self.STATUS_RELEASED or self.status == self.STATUS_NEWLY_RELEASED

    def is_newly_touched(self):
        return self.status == self.STATUS_NEWLY_TOUCHED

    def is_touched(self):
        return self.status == self.STATUS_TOUCHED or self.status == self.STATUS_NEWLY_TOUCHED

    def is_newly_released(self):
        return self.status == self.STATUS_NEWLY_RELEASED


class Electrodes(object):

    def __init__(self, electrodes_count):
        self.electrodes = []
        self.electrodes_count = electrodes_count

        for i in range(self.electrodes_count):
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
        electrodes_count = 0
        for i2c_mux_index, i2c_address_offset, electrodes_map in mpr121_map:
            mpr = mpr121.Mpr121(i2c_address_offset, i2c_mux_index)
            mpr.electrodes_map = electrodes_map
            electrodes_map_len = len(mpr.electrodes_map)
            electrodes_count += electrodes_map_len
            mpr.config_regs(electrodes_map_len)
            self.mprs.append(mpr)

        Electrodes.__init__(self, electrodes_count)

    def update(self):
        bitmasks = [mpr._dev.read(0x00, 1)[0] for mpr in self.mprs]
        for bitmask, mpr in zip(bitmasks, self.mprs):
            for i in mpr.electrodes_map:
                self.electrodes[i]._set_touched(bitmask & 1)
                bitmask >>= 1


class Mpr121ElectrodesGrid(Mpr121Electrodes):

    def __init__(self, mpr121_map, grid_sizes, pixel_sizes):
        self.grid_sizes = grid_sizes
        self.pixel_sizes = pixel_sizes
        self.electrod_pixel_sizes = (
            self.pixel_sizes[0] // self.grid_sizes[0], self.pixel_sizes[1] // self.grid_sizes[1])

        Mpr121Electrodes.__init__(self, mpr121_map)

        for i in self.electrodes:
            i.grid_indexes = (i.index % self.grid_sizes[0], i.index // self.grid_sizes[0])
            i.top_left_pixel = (i.grid_indexes[0] * self.electrod_pixel_sizes[0],
                i.grid_indexes[1] * self.electrod_pixel_sizes[1])
            i.mid_pixel = (i.top_left_pixel[0] + self.electrod_pixel_sizes[0] // 2,
                i.top_left_pixel[1] + self.electrod_pixel_sizes[1] // 2)
