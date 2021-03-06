import sys
import signal
import logging
import argparse
import importlib
import rpyc
import rpyc.utils.server
import IPython.terminal.embed as _ipython
import common
from infra.core import utils


class _App(object):

    def __init__(self, app):
        self._app_ = None
        self._app_attrs_ = []
        self._app_module_ = importlib.import_module(app)
        self._app_globals_ = common.Atters()
        self._base_app_module_ = importlib.import_module('infra.app.app')
        self._load_()

    def __loop__(self):
        try:
            while True:
                self._app_.__loop__()
        except KeyboardInterrupt:
            pass

    def _reload_(self):
        self._unload_()
        importlib.invalidate_caches()
        for i in self._app_._modules:
            print('reloading %s' % (i.__name__,))
            importlib.reload(i)
        self._load_()

    def _load_(self):
        self._app_ = getattr(self._app_module_, utils.module_to_class_name(
            self._app_module_.__name__.rsplit('.', 1)[1]))(self._app_globals_)
        self._app_._modules.extend([self._base_app_module_, self._app_module_])
        self._app_.reload = self._reload_
        utils.delattrs(self, self._app_attrs_)
        self._app_attrs_ = utils.get_exposed_attrs(self._app_)
        utils.cpyattrs(self._app_, self, self._app_attrs_)

    def _unload_(self):
        if hasattr(self._app_, '__exit__'):
            self._app_.__exit__()


class _AppService(rpyc.Service):

    _logger = logging.getLogger('rpyc')
    _logger.setLevel(logging.WARNING)

    def on_connect(self, conn):
        conn._config.update(dict(
            allow_all_attrs=True,
            allow_pickle=True,
            allow_getattr=True,
            allow_setattr=True,
            allow_delattr=True,
            import_custom_exceptions=True,
            instantiate_custom_exceptions=True,
            instantiate_oldstyle_exceptions=True))
        self.exposed_app = globals()['app']
        self.exposed_app._app_.__rpyc_connect__(conn)

    def on_disconnect(self, conn):
        self.exposed_app._app_.__rpyc_disconnect__(conn)


if __name__ == '__main__':
    _parser = argparse.ArgumentParser(
        description='App Runner',
        add_help=False)
    _parser.add_argument(
        '--interface',
        metavar='<interface>',
        dest='interface',
        type=str,
        default='ipython',
        choices=('ipython', 'rpyc', 'loop', 'none'),
        help='the app interface')
    _parser.add_argument(
        '--app',
        metavar='<app package>',
        dest='app',
        type=str,
        required=True,
        help='the app package')
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
        help='python line to run after app creation')

    _args, _ = _parser.parse_known_args()
    app = _App(_args.app)

    _signaled = False

    def _signal_handler(signum, frame):
        global _signaled
        if not _signaled:
            _signaled = True
            app._app_logger.info('Signal %s received, exiting...', signum)
            app._unload_()
            sys.exit(0)
    for _i in (signal.SIGTERM, signal.SIGINT):
        signal.signal(_i, _signal_handler)

    if _args.cmd:
        exec(_args.cmd)  # eval(_args.cmd)
    if _args.interface == 'ipython':
        _ipython.InteractiveShellEmbed()()
    elif _args.interface == 'rpyc':
        rpyc.utils.server.ThreadedServer(
            service=_AppService,
            port=_args.rpyc_port,
            logger=_AppService._logger).start()
    elif _args.interface == 'loop':
        app.__loop__()

    app._unload_()
