import sys
import os.path
import argparse
import importlib
import rpyc
import rpyc.utils.server
import IPython.terminal.embed as _ipython


# set PYTHONPATH
_base_path = os.path.abspath(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))
sys.path.extend([_base_path])


import infra.core.utils


class _App(object):
    
    def __init__(self, app):
        self._app_ = None
        self._app_module_ = importlib.import_module(app)
        self._load_()
    
    def _reload_(self):
        self._unload_()
        importlib.invalidate_caches()
        if hasattr(self._app_, '_modules'):
            for i in self._app_._modules:
                print('reloading %s' % (i.__name__,))
                importlib.reload(i)
        print('reloading %s' % (self._app_module_.__name__,))
        importlib.reload(self._app_module_)
        self._load_()

    def _load_(self):
        self._app_ = getattr(self._app_module_, infra.core.utils.module_to_class_name(
            self._app_module_.__name__.rsplit('.', 1)[1]))()
        self._app_.reload = self._reload_
        for i in dir(self._app_):
            if not i.startswith('__'):
                setattr(self, i, getattr(self._app_, i))

    def _unload_(self):
        if hasattr(self._app_, '__exit__'):
            self._app_.__exit__()


class _AppService(rpyc.Service):

    def on_connect(self):
        print('AppService.on_connect')
        self._conn._config.update(dict(
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

    def on_disconnect(self):
        print('AppService.on_disconnect')


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
        choices=('ipython', 'rpyc'),
        help='the app interface')
    _parser.add_argument(
        '--app',
        metavar='<app package>',
        dest='app',
        type=str,
        required=True,
        help='the app package')

    _args, _ = _parser.parse_known_args()
    app = _App(_args.app)
    if _args.interface == 'ipython':
        _ipython.InteractiveShellEmbed()()
    elif _args.interface == 'rpyc':
        rpyc.utils.server.ThreadedServer(
            service=_AppService,
            port=rpyc.utils.classic.DEFAULT_SERVER_PORT).start()
    app._unload_()
