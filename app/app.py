import logging
from infra.core import utils
from infra.core.logor import Logor


class App(object):

    def __init__(self, constants=None):
        self._modules = []
        self._app_logger = logging.getLogger(App.__name__)
        if utils.hasattrs(constants, 'LOGOR_FORMATS', 'LOGOR_LEVEL', 'LOGOR_COLOR_MAP'):
            Logor(constants.LOGOR_FORMATS, constants.LOGOR_LEVEL, constants.LOGOR_COLOR_MAP)
        self._app_logger.info('App started')

    def __exit__(self):
        self._app_logger.warn('App ended\n')
