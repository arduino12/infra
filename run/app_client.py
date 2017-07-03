import IPython.terminal.embed as _ipython
import rpyc


class App(object):

    def __init__(self):
        self._conn = None

    def reconnect(self):
        self.disconnect()
        self._conn = rpyc.connect('', rpyc.utils.classic.DEFAULT_SERVER_PORT)
        self.reload(False)

    def disconnect(self):
        try:
            self._conn.close()
        except Exception:
            pass

    def reload(self, reload=True):
        app = self._conn.root.exposed_app
        if reload:
            app.reload()
        for i in dir(app):
            if i.startswith('__') or i.endswith('_') or i == 'reload':
                continue
            setattr(self, i, getattr(app, i))


if __name__ == '__main__':
    app = App()
    try:
        app.reconnect()
    except Exception:
        pass
    _ipython.InteractiveShellEmbed()()
    app.disconnect()
