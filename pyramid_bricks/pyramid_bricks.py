from pyramid.config import Configurator

class MissingConfiguration(Exception):
    pass

def get_component_route_name(component_type):
    return component_type.__name__

def get_component_url(request, component_type, *args, **kwargs):
    route_name = get_component_route_name(component_type)
    return request.route_url(route_name, *args, **kwargs)

class PyramidBricks:
    def __init__(self, *args):
        self.config = Configurator()
        self.config.include('pyramid_mako')
        self.config.add_request_method(get_component_url, 'component_url')
        self.components = {}
        for arg in args:
            self.add_component(arg)

    def add_component(self, component_type):
        if component_type in self.components:
            return self.components[component_type]
        args = []
        if hasattr(component_type, 'requires_configured'):
            try:
                args += [self.components[requirement] for requirement
                         in component_type.requires_configured]
            except KeyError as e:
                raise MissingConfiguration("{} requires something that "
                    "provides {} to be configured".format(
                        component_type, e.args[0]))
        if hasattr(component_type, 'depends_on'):
            args += [self.add_component(comp_type) for
                    comp_type in component_type.depends_on]
        component = component_type(*args)
        if hasattr(component, 'provides'):
            for provision in component_type.provides:
                self.components[provision] = component
        self.init_component(component)
        self.components[component_type] = component
        return component

    def init_component(self, component):
        if hasattr(component, 'url'):
            self.route_component(component)

    def route_component(self, component):
        route_name = get_component_route_name(type(component))
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
