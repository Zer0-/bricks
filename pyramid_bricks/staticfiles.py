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

class StaticFile:
    requires_configured = ['static_manager']

    def __init__(self, static_manager):
        static_manager.add(self)

    def __call__(self):
        return self.url

    def __new__(cls, url, name):
        newcls = type(
            name,
            (object,),
            dict(
                url=url,
                requires_configured=cls.requires_configured,
                __init__=cls.__init__,
                __call__=cls.__call__
            )
        )
        return newcls

class StaticCss(StaticFile):
    def __call__(self):
        return '<link rel="stylesheet" href="{}" />'.format(self.url)
