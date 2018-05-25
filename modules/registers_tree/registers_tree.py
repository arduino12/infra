
class SubReg(object):
    
    def __init__(self, start_bit, bits_count):
        self._reg = None
        self._name = None
        self._start_bit = start_bit
        self._bits_count = bits_count
        self._bitmask = (1 << bits_count) - 1

    def _sub_write(self, reg_value, sub_reg_value):
        reg_value &= ~(self._bitmask << self._start_bit)
        reg_value |= (sub_reg_value & self._bitmask) << self._start_bit
        return reg_value

    def get(self, read=True):
        return (self._reg.get(read) >> self._start_bit) & self._bitmask

    def set(self, value, overwrite=True):
        self._reg.set(self._sub_write(self._reg.get(False), value), overwrite)

    def __call__(self):
        return self.get()

    def __str__(self):
        return '{self._name}={value:value_format}'.format(
            self=self,
            value=self.get(False),
            value_format='#04x' if self._bits_count > 3 else '')

    def __repr__(self):
        return self.__str__()


class Register(object):
    
    def __init__(self, address, bits_count, initial_value, **sub_regs):
        self._dev = None
        self._name = None
        self._address = address
        self._bits_count = bits_count
        self._bytes_count = (self._bits_count + 7) // 8
        self._values = self._to_values(initial_value)
        self._sub_regs = sub_regs.values()

        for k, v in sub_regs.items():
            v._reg = self
            setattr(self, k, v)

    def _crop_values(self, values):
        values = values[:self._bytes_count]
        values.extend([0] * (self._bytes_count - len(values)))
        values[-1] &= (1 << ((self._bits_count + 7) % 8 + 1)) - 1
        return values

    def _to_values(self, value):
        return self._crop_values([(value >> (i * 8)) & 0xFF for i in range(self._bytes_count)])

    def _read(self):
        self._values = self._crop_values(self._dev.read(self._address, self._bytes_count))
        return self._values

    def _write(self, values, overwrite=True):
        values = self._crop_values(values)
        if overwrite or self._values != values:
            self._values = values
            self._dev.write(self._address, self._values)

    def get(self, read=True):
        if read:
            self._read()
        return sum(v << (i * 8) for i, v in enumerate(self._values))

    def set(self, value=None, overwrite=True, **sub_regs):
        if value is None:
            value = self.get(False)
            for k, v in sub_regs.items():
                value = getattr(self, k)._sub_write(value, v)

        self._write(self._to_values(value), overwrite)

    def __call__(self):
        return self.get()

    def __str__(self):
        return '{self._name} [{self._address:#04x}] = {value:#0{size}x}'.format(
            self=self,
            value=self.get(),
            size=self._bytes_count * 2 + 2)


class Registers(object):
    
    def __init__(self, dev, **regs):
        self._dev = dev
        self._regs = regs.values()

        for k, v in regs.items():
            v._dev = self._dev
            v._name = k
            setattr(self, k, v)

    def __str__(self):
        return '\n'.join(map(str, self._regs))
