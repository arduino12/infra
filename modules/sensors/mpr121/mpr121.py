from infra.modules.registers_tree import registers_tree


class Mpr121(object):
    ELECTRODES_COUNT = 12
    _I2C_BASE_ADDRESS = 0x5A
    _ELECTRODES_RANGE = list(range(ELECTRODES_COUNT))

    def __init__(self, dev, elec_count=ELECTRODES_COUNT):
        self._configured = False
        self._dev = dev
        self.elec_count = elec_count
        self.regs = registers_tree.Registers(
            self._dev,
            touch_status=registers_tree.Register(
                0x00, 16, 0,
                eleprox=registers_tree.SubReg(12, 1),
                ovcf=registers_tree.SubReg(15, 1),
                **self._sub_regs(1)),
            oor_status=registers_tree.Register(
                0x02, 16, 0,
                eleprox=registers_tree.SubReg(12, 1),
                acff=registers_tree.SubReg(14, 1),
                arff=registers_tree.SubReg(15, 1),
                **self._sub_regs(1)),
            electrode_value=registers_tree.Register(
                0x04, 208, 0,
                eleprox=registers_tree.SubReg(192, 10),
                **self._sub_regs(10, 16)),
            baseline_value=registers_tree.Register(
                0x1E, 104, 0,
                eleprox=registers_tree.SubReg(96, 8),
                **self._sub_regs(8, 8)),
            baseline_filters=registers_tree.Register(
                0x2B, 88, 0, write_hook=self._reg_write_hook,
                rising_mhd=registers_tree.SubReg(0, 6),
                rising_nhd=registers_tree.SubReg(8, 6),
                rising_ncl=registers_tree.SubReg(16, 8),
                rising_fdl=registers_tree.SubReg(24, 8),
                falling_mhd=registers_tree.SubReg(32, 6),
                falling_nhd=registers_tree.SubReg(40, 6),
                falling_ncl=registers_tree.SubReg(48, 8),
                falling_fdl=registers_tree.SubReg(56, 8),
                touched_nhd=registers_tree.SubReg(64, 6),
                touched_ncl=registers_tree.SubReg(72, 8),
                touched_fdl=registers_tree.SubReg(80, 8)),
            eleprox_baseline_filters=registers_tree.Register(
                0x36, 88, 0,
                rising_mhd=registers_tree.SubReg(0, 6),
                rising_nhd=registers_tree.SubReg(8, 6),
                rising_ncl=registers_tree.SubReg(16, 8),
                rising_fdl=registers_tree.SubReg(24, 8),
                falling_mhd=registers_tree.SubReg(32, 6),
                falling_nhd=registers_tree.SubReg(40, 6),
                falling_ncl=registers_tree.SubReg(48, 8),
                falling_fdl=registers_tree.SubReg(56, 8),
                touched_nhd=registers_tree.SubReg(64, 6),
                touched_ncl=registers_tree.SubReg(72, 8),
                touched_fdl=registers_tree.SubReg(80, 8)),
            electrode_threshold=registers_tree.Register(
                0x41, 208, 0, write_hook=self._reg_write_hook,
                eleprox_touch=registers_tree.SubReg(192, 8),
                eleprox_release=registers_tree.SubReg(200, 8),
                **self._sub_regs(8, 16, 'e{}_touch'),
                **self._sub_regs(8, 16, 'e{}_release')),
            debounce=registers_tree.Register(
                0x5B, 8, 0, write_hook=self._reg_write_hook,
                touch=registers_tree.SubReg(0, 3),
                release=registers_tree.SubReg(4, 3)),
            afe_configuration=registers_tree.Register(
                0x5C, 16, 0x2410, write_hook=self._reg_write_hook,
                cdc=registers_tree.SubReg(0, 6),
                ffi=registers_tree.SubReg(6, 2),
                esi=registers_tree.SubReg(8, 3),
                sfi=registers_tree.SubReg(11, 2),
                cdt=registers_tree.SubReg(13, 3)),
            electrode_configuration=registers_tree.Register(
                0x5E, 8, 0,
                ele=registers_tree.SubReg(0, 4),
                eleprox=registers_tree.SubReg(4, 2),
                cl=registers_tree.SubReg(6, 2)),
            electrode_current=registers_tree.Register(
                0x5F, 104, 0, write_hook=self._reg_write_hook,
                eleprox=registers_tree.SubReg(96, 6),
                **self._sub_regs(6, 8)),
            gpio=registers_tree.Register(
                0x73, 64, 0,
                control=registers_tree.SubReg(0, 16),
                data=registers_tree.SubReg(16, 8),
                direction=registers_tree.SubReg(24, 8),
                enable=registers_tree.SubReg(32, 8),
                data_set=registers_tree.SubReg(40, 8),
                data_clear=registers_tree.SubReg(48, 8),
                data_toggle=registers_tree.SubReg(56, 8)),
            auto_configuration=registers_tree.Register(
                0x7B, 40, 0, write_hook=self._reg_write_hook,
                ace=registers_tree.SubReg(0, 1),
                are=registers_tree.SubReg(1, 1),
                bva=registers_tree.SubReg(2, 2),
                retry=registers_tree.SubReg(4, 2),
                afes=registers_tree.SubReg(6, 2),
                acfie=registers_tree.SubReg(8, 1),
                arfie=registers_tree.SubReg(9, 1),
                oorie=registers_tree.SubReg(10, 1),
                scts=registers_tree.SubReg(15, 1),
                usl=registers_tree.SubReg(16, 8),
                lsl=registers_tree.SubReg(24, 8),
                tl=registers_tree.SubReg(32, 8)))

    def _sub_regs(self, bits_count, bits_size=1, fmt=None):
        if fmt is None:
            fmt = 'e{}'
        return {fmt.format(i): registers_tree.SubReg(i * bits_size, bits_count)
                for i in self._ELECTRODES_RANGE}

    def _reg_write_hook(self, pre_write):
        if self._configured:
            if pre_write:
                self.regs.electrode_configuration.set(0x00)
            else:
                self.regs.electrode_configuration.set(
                    cl=2, ele=self.elec_count)

    def reset(self):
        self._dev.write(0x80, [0x63])

    def config_regs(self):
        # software reset
        self.reset()
        # goto stand-by in order to write settings
        self._configured = True
        self._reg_write_hook(True)
        self._configured = False
        # set all electrodes threshholds
        self.regs.electrode_threshold._write([2] * 26)
        # set baseline filters
        self.regs.baseline_filters.set(
            rising_mhd=0x01,
            rising_nhd=0x01,
            rising_ncl=0x00,
            rising_fdl=0x00,
            falling_mhd=0x01,
            falling_nhd=0x01,
            falling_ncl=0xFF,
            falling_fdl=0x02)
        # 7 readings for touch and release
        self.regs.debounce.set(touch=7, release=7)
        # charge electrodes with 63mA in 1us
        self.regs.afe_configuration.set(cdc=63, ffi=0, esi=0, sfi=3, cdt=2)
        # auto config baseline and filters
        self.regs.auto_configuration.set(
            ace=1, are=1, bva=3, usl=800 >> 2, lsl=600 >> 2, tl=700 >> 2)
        # enable electrodes and goto run mode (must be the last configuration)
        self._configured = True
        self._reg_write_hook(False)
