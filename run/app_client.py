import rpyc
import IPython.terminal.embed as _ipython
import common

from infra.core import utils


class _App(object):

    def __init__(self):
        self._conn_ = None
        self._app_attrs_ = utils.get_exposed_attrs(self)

    def reconnect(self):
        self.disconnect()
        self._conn_ = rpyc.connect('localhost', rpyc.utils.classic.DEFAULT_SERVER_PORT)
        self.reload(False)

    def disconnect(self):
        try:
            self._conn_.close()
        except Exception:
            pass

    def reload(self, reload=True):
        app = self._conn_.root.exposed_app
        if reload:
            utils.delattrs(self, [i for i in app._app_attrs_ if i not in self._app_attrs_])
            app.reload()
        utils.cpyattrs(app, self, [i for i in app._app_attrs_ if i not in self._app_attrs_])


if __name__ == '__main__':
    app = _App()
    try:
        app.reconnect()
    except Exception:
        pass
    _ipython.InteractiveShellEmbed()()
    app.disconnect()
