import rpyc
import argparse
import IPython.terminal.embed as _ipython
import common

from infra.core import utils


class _App(object):

    def __init__(self, rpyc_addr=None, rpyc_port=None):
        self._conn_ = None
        self._rpyc_addr_ = rpyc_addr or 'localhost'
        self._rpyc_port_ = rpyc_port or rpyc.utils.classic.DEFAULT_SERVER_PORT
        self._app_attrs_ = utils.get_exposed_attrs(self)

    def reconnect(self):
        self.disconnect()
        self._conn_ = rpyc.connect(self._rpyc_addr_, self._rpyc_port_)
        self.reload(False)

    def disconnect(self):
        try:
            self._conn_.close()
        except Exception:
            pass

    def reload(self, reload=True):
        app = self._conn_.root.exposed_app
        if reload:
            utils.delattrs(self, [
                i for i in app._app_attrs_ if i not in self._app_attrs_])
            app.reload()
        utils.cpyattrs(app, self, [
            i for i in app._app_attrs_ if i not in self._app_attrs_])


if __name__ == '__main__':
    _parser = argparse.ArgumentParser(
        description='App Client',
        add_help=False)
    _parser.add_argument(
        '--rpyc_addr',
        metavar='<ip address>',
        dest='rpyc_addr',
        type=str,
        default='localhost',
        help='the remote app rpyc address')
    _parser.add_argument(
        '--rpyc_port',
        metavar='<port number>',
        dest='rpyc_port',
        type=int,
        default=rpyc.utils.classic.DEFAULT_SERVER_PORT,
        help='the remote app rpyc port')
    _parser.add_argument(
        '--cmd',
        metavar='<python line>',
        dest='cmd',
        type=str,
        default='',
        help='python line insted of running ipython')
    _args, _ = _parser.parse_known_args()
    app = _App(_args.rpyc_addr, _args.rpyc_port)
    app._args = _args
    try:
        app.reconnect()
    except Exception:
        pass
    if app._args.cmd:
        exec(app._args.cmd)  # eval(app._args.cmd)
    else:
        _ipython.InteractiveShellEmbed()()
    app.disconnect()
