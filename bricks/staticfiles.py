from enum import Enum
from os.path import join
from .custom import customizable

class StaticfileOptimizationLevel(Enum):
    NOOPT = 0
    CONCAT_PAGE = 1
    CONCAT = 2
    INLINE = 3

class StaticFile(metaclass=customizable):
    """Static asset that's part of a component (served locally)
    For things like coffeescript or sass that need to be compiled,
    'has_build_stage' should be set to True.
    The 'relpath' is where the asset is relative to the root static path.
    """
    custom_attributes = ('asset',)
    requires_configured = ['static_manager']
    optim = StaticfileOptimizationLevel.NOOPT
    bottom = False #optimization: sends link to resource to bottom of html
    has_build_stage = False
    relpath = ''

    def __init__(self, static_manager):
        self.static_manager = static_manager
        static_manager.add(self)

    def get_url(self):
        return self.static_manager.get_url(self)

    def __call__(self):
        return self.get_url()

def _css(url):
    return '<link rel="stylesheet" href="{}" />'.format(url)

def _js(url):
    return '<script src="{}"></script>'.format(url)

class StaticCss(StaticFile):
    relpath = 'css'

    def __call__(self):
        return _css(self.get_url())

class StaticJs(StaticFile):
    relpath = 'js'

    def __call__(self):
        return _js(self.get_url())

class ExternalStatic(metaclass=customizable):
    custom_attributes = ('url',)
    requires_configured = ['static_manager']

    def __init__(self, static_manager):
        static_manager.add(self)

    def get_url(self):
        return self.url

    def __call__(self):
        return self.url

class ExternalCss(ExternalStatic):
    def __call__(self):
        return _css(self.url)

class ExternalJs(ExternalStatic):
    def __call__(self):
        return _js(self.url)
