
def _add_gradient(name, val, rgb_channels):
    r, g, b = ((rgb_channels >> i) & 1 for i in range(3))
    while val > 0:
        globals()['{}_{}'.format(name, val)] = (r * val, g * val, b * val)
        val -= 1

_add_gradient('RED', 255, 1)
_add_gradient('GREEN', 255, 2)
_add_gradient('YELLOW', 255, 3)
_add_gradient('BLUE', 255, 4)
_add_gradient('MAGENTA', 255, 5)
_add_gradient('CYAN', 255, 6)
_add_gradient('GRAY', 254, 7)

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
