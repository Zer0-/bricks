from pyramid.config import Configurator

class PyramidBricks:
    def __init__(self, *args):
        self.config = Configurator()
        for arg in args:
            self.add_component(arg)

    def add_component(self, component_type):
        component = component_type()
        if hasattr('url', component):
            self.add_route(component)

    def add_route(self, component):
        route_name = component.__name__
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
