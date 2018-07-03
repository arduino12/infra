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
    _logger.setLevel(logging.INFO)

    def on_connect(self, conn):
        self._logger.info('on_connect')
        conn._config.update(dict(
            allow_all_attrs = True,
            allow_pickle = True,
            allow_getattr = True,
            allow_setattr = True,
            allow_delattr = True,
            import_custom_exceptions = True,
            instantiate_custom_exceptions = True,
            instantiate_oldstyle_exceptions = True,
        ))
        self.exposed_app = globals()['app']

    def on_disconnect(self, conn):
        self._logger.info('on_disconnect')


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
        choices=('ipython', 'rpyc', 'none'),
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
    if _args.cmd:
        exec(_args.cmd) # eval(_args.cmd)
    if _args.interface == 'ipython':
        _ipython.InteractiveShellEmbed()()
    elif _args.interface == 'rpyc':
        rpyc.utils.server.ThreadedServer(
            service=_AppService,
            port=_args.rpyc_port,
            logger=_AppService._logger).start()
    app._unload_()
