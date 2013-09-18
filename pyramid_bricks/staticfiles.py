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
    custom_attributes = ('asset',)
    requires_configured = ['static_manager']

    def __init__(self, static_manager):
        static_manager.add(self)

    def __call__(self):
        return self.asset

class StaticCss(StaticFile):
    def __call__(self):
        return '<link rel="stylesheet" href="{}" />'.format(self.asset)

class StaticJs(StaticFile):
    def __call__(self):
        return '<script src="{}"></script>'.format(self.asset)
