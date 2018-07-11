
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


class ElectrodesGrid(Electrodes):

    def __init__(self, grid_sizes, pixel_sizes):
        Electrodes.__init__(self, grid_sizes[0] * grid_sizes[1])
        self.grid_sizes = grid_sizes
        self.pixel_sizes = pixel_sizes
        self.elec_pixel_sizes = (
            self.pixel_sizes[0] // self.grid_sizes[0],
            self.pixel_sizes[1] // self.grid_sizes[1])

        for i in self.electrodes:
            i.grid_indexes = (
                i.index % self.grid_sizes[0], i.index // self.grid_sizes[0])
            i.top_left_pixel = (
                i.grid_indexes[0] * self.elec_pixel_sizes[0],
                i.grid_indexes[1] * self.elec_pixel_sizes[1])
            i.rect = i.top_left_pixel + self.elec_pixel_sizes
            i.mid_pixel = (
                i.top_left_pixel[0] + self.elec_pixel_sizes[0] // 2,
                i.top_left_pixel[1] + self.elec_pixel_sizes[1] // 2)
