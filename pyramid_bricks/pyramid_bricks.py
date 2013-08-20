from pyramid.config import Configurator

class PyramidBricks:
    def __init__(self, *args):
        self.config = Configurator()
        for arg in args:
            self.add_component(arg)

    def add_component(self, component_type, components=None):
        if not components:
            components = {}
        if component_type in components:
            return components[component_type]
        if hasattr(component_type, 'depends_on'):
            deps = tuple(self.add_component(comp_type, components) for
                        comp_type in component_type.depends_on)
            component = component_type(*deps)
        else:
            component = component_type()
        self.init_component(component)
        components[component_type] = component
        return component

    def init_component(self, component):
        if hasattr(component, 'url'):
            self.route_component(component)

    def route_component(self, component):
        route_name = component.__class__.__name__
        self.config.add_route(route_name, component.url)
        for method in ['GET', 'POST', 'PUT', 'DELETE']:
            view = getattr(component, method, None)
            if not view:
                continue
            self.config.add_view(
                view,
                route_name=route_name,
                request_method=method
            )

    def make_app(self):
        return self.config.make_wsgi_app()
