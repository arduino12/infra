from infra.modules.i2c_mux.i2c_mux import MuxI2c
from infra.modules.registers_tree.registers_tree import Registers, Register, SubReg


class Mpr121(object):
    ELECTRODES_COUNT = 12
    _I2C_BASE_ADDRESS = 0x5A
    _ELECTRODES_RANGE = list(range(ELECTRODES_COUNT))

    def __init__(self, i2c_address_offset=0, i2c_mux_index=0):
        self._dev = MuxI2c(self._I2C_BASE_ADDRESS + i2c_address_offset, i2c_mux_index)
        self.regs = Registers(self._dev,
            touch_status=Register(0x00, 16, 0,
                eleprox=SubReg(12, 1),
                ovcf=SubReg(15, 1),
                **{'e{}'.format(i): SubReg(i, 1) for i in self._ELECTRODES_RANGE}),
            oor_status=Register(0x02, 16, 0,
                eleprox=SubReg(12, 1),
                acff=SubReg(14, 1),
                arff=SubReg(15, 1),
                **{'e{}'.format(i): SubReg(i, 1) for i in self._ELECTRODES_RANGE}),
            electrode_value=Register(0x04, 208, 0,
                eleprox=SubReg(192, 10),
                **{'e{}'.format(i): SubReg(i * 16, 10) for i in self._ELECTRODES_RANGE}),
            baseline_value=Register(0x1E, 104, 0,
                eleprox=SubReg(96, 8),
                **{'e{}'.format(i): SubReg(i * 8, 8) for i in self._ELECTRODES_RANGE}),
            baseline_filters=Register(0x2B, 88, 0,
                rising_mhd=SubReg(0, 6),
                rising_nhd=SubReg(8, 6),
                rising_ncl=SubReg(16, 8),
                rising_fdl=SubReg(24, 8),
                falling_mhd=SubReg(32, 6),
                falling_nhd=SubReg(40, 6),
                falling_ncl=SubReg(48, 8),
                falling_fdl=SubReg(56, 8),
                touched_nhd=SubReg(64, 6),
                touched_ncl=SubReg(72, 8),
                touched_fdl=SubReg(80, 8)),
            eleprox_baseline_filters=Register(0x36, 88, 0,
                rising_mhd=SubReg(0, 6),
                rising_nhd=SubReg(8, 6),
                rising_ncl=SubReg(16, 8),
                rising_fdl=SubReg(24, 8),
                falling_mhd=SubReg(32, 6),
                falling_nhd=SubReg(40, 6),
                falling_ncl=SubReg(48, 8),
                falling_fdl=SubReg(56, 8),
                touched_nhd=SubReg(64, 6),
                touched_ncl=SubReg(72, 8),
                touched_fdl=SubReg(80, 8)),
            electrode_threshold=Register(0x41, 208, 0,
                eleprox_touch=SubReg(192, 8),
                eleprox_release=SubReg(200, 8),
                **{'e{}_touch'.format(i): SubReg(i * 16, 8) for i in self._ELECTRODES_RANGE},
                **{'e{}_release'.format(i): SubReg(i * 16 + 8, 8) for i in self._ELECTRODES_RANGE}),
            debounce=Register(0x5B, 8, 0,
                touch=SubReg(0, 3),
                release=SubReg(4, 3)),
            afe_configuration=Register(0x5C, 16, 0x2410,
                cdc=SubReg(0, 6),
                ffi=SubReg(6, 2),
                esi=SubReg(8, 3),
                sfi=SubReg(11, 2),
                cdt=SubReg(13, 3)),
            electrode_configuration=Register(0x5E, 8, 0,
                ele=SubReg(0, 4),
                eleprox=SubReg(4, 2),
                cl=SubReg(6, 2)),
            electrode_current=Register(0x5F, 104, 0,
                eleprox=SubReg(96, 6),
                **{'e{}'.format(i): SubReg(i * 8, 6) for i in self._ELECTRODES_RANGE}),
            gpio=Register(0x73, 64, 0,
                control=SubReg(0, 16),
                data=SubReg(16, 8),
                direction=SubReg(24, 8),
                enable=SubReg(32, 8),
                data_set=SubReg(40, 8),
                data_clear=SubReg(48, 8),
                data_toggle=SubReg(56, 8)),
            auto_configuration=Register(0x7B, 40, 0,
                ace=SubReg(0, 1),
                are=SubReg(1, 1),
                bva=SubReg(2, 2),
                retry=SubReg(4, 2),
                afes=SubReg(6, 2),
                acfie=SubReg(8, 1),
                arfie=SubReg(9, 1),
                oorie=SubReg(10, 1),
                scts=SubReg(15, 1),
                usl=SubReg(16, 8),
                lsl=SubReg(24, 8),
                tl=SubReg(32, 8)))
    
    def reset(self):
        self._dev.write(0x80, [0x63])

    def config_regs(self, electrodes_count=ELECTRODES_COUNT):
        # software reset
        self.reset()
        # goto stand-by in order to write settings
        self.regs.electrode_configuration.set(0x00)
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
        self.regs.afe_configuration.set(cdc=63, cdt=2)
        # auto config baseline and filters
        self.regs.auto_configuration.set(ace=1, are=1, bva=3,
            usl=800 >> 2, lsl=600 >> 2, tl=700 >> 2)
        # enable electrodes and goto run mode (must be the final register to config)
        self.regs.electrode_configuration.set(cl=2, ele=electrodes_count)
