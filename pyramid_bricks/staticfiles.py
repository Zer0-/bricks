from os.path import join, basename
from pyramid.path import AssetResolver
from .component import CustomComponent

class StaticManager:
    provides = ['static_manager']

    def __init__(self):
        self.static_components = {}

    def add(self, static_component):
        self.static_components[type(static_component)] = static_component

    def render_static(self, component, visited=None):
        if visited is None:
            visited = set()
        if component in visited:
            return ''
        visited.add(component)
        resources_string = self.static_components.get(component, str)()
        return resources_string + ''.join(
            [self.render_static(dep, visited)
             for dep in getattr(component, 'depends_on', [])]
        )

class StaticFile(CustomComponent):
    """Static asset that's part of a component (served locally)
    For things like coffeescript or sass that need to be compiled,
    'has_build_stage' should be set to True.
    The 'relpath' is where the asset is relative to the root static path.
    """
    custom_attributes = ('asset',)
    requires_configured = ['static_manager', 'json_settings']
    has_build_stage = False
    relpath = ''

    def __init__(self, static_manager, settings):
        static_manager.add(self)
        self.static_url = settings['served_static_url']
        self.asset_path = AssetResolver().resolve(self.asset).abspath()

    def get_url(self):
        return self.static_url +\
                join(self.relpath, basename(self.asset_path))

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

class ExternalStatic(CustomComponent):
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
