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
    target_type = None

    def __init__(self, static_manager):
        static_manager.add(self)
        if self.asset.startswith('http'):
            self.url = self.asset
        else:
            self.url = static_manager.get_url(self)

    def __call__(self):
        return self.url()

class StaticCss(StaticFile):
    relpath = 'css'
    target_type = 'css'

    def __call__(self):
        return '<link rel="stylesheet" href="{}" />'.format(self.url())

class StaticJs(StaticFile):
    relpath = 'js'
    target_type = 'js'

    def __call__(self):
        return '<script src="{}"></script>'.format(self.url())
