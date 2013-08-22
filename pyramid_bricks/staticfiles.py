from component import CustomComponent

class StaticManager:
    provides = ['static_manager']

    def __init__(self):
        self.static_components = {}

    def add(self, static_component):
        self.static_components[type(static_component)] = static_component

    def render_static(self, component, visited=None):
        if not visited:
            visited = set()
        resources_string = ''
        if component in visited:
            return resources_string
        resources_string = self.static_components.get(component, str)()
        return resources_string + ''.join(
            [self.render_static(dep, visited)
             for dep in getattr(component, 'depends_on', [])]
        )

class StaticFile(CustomComponent):
    custom_attributes = ('resource_url',)
    requires_configured = ['static_manager']

    def __init__(self, static_manager):
        static_manager.add(self)

    def __call__(self):
        return self.resource_url

class StaticCss(StaticFile):
    def __call__(self):
        return '<link rel="stylesheet" href="{}" />'.format(self.resource_url)
