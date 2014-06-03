from webob import Request
from .routing import routeset, RouteApi
from .httpexceptions import (
    HTTPException,
    HTTPNotFound
)

class MissingConfiguration(Exception):
    pass

class Bricks:
    """Facilitates initialization of given components to provide
    simple dependency injection."""

    def __init__(self):
        self.components = {}

    def add(self, component_type):
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
            args += [self.add(comp_type) for
                        comp_type in component_type.depends_on]
        component = component_type(*args)
        if hasattr(component, 'provides'):
            for provision in component_type.provides:
                self.components[provision] = component
        self.components[component_type] = component
        return component

def create_app(main_component):
    bricks = Bricks()
    main = bricks.add(main_component)

    def wsgi_app(environ, start_response):
        request = Request(environ)
        response = main(request)
        return response(environ, start_response)

    return wsgi_app

class BaseMC:
    def __init__(self, *args):
        pass

    def get_view(self, request):
        request.route = RouteApi(request, self.routemap)
        if request.route._matched_routes == 404:
            return HTTPNotFound()
        route = request.route.route
        view = route.get_view(request)
        if view is None:
            return HTTPNotFound()
        return view

    def __call__(self, request):
        view = self.get_view(request)
        if isinstance(view, HTTPException):
            return view
        return view(request)

def mc_from_routemap(routemap, base_component=BaseMC, extra_dependencies=[]):
    if hasattr(base_component, 'depends_on'):
        deps = base_component.depends_on
    else:
        deps = []
    deps += extra_dependencies
    deps += list(routeset(routemap))
    return type(
        "MainComponent",
        (base_component,),
        dict(routemap=routemap, depends_on=deps)
    )

def app_from_routemap(routemap, main_component=BaseMC, components=[]):
    """Given a routemap (Route instance) this will create a wsgi app.
    main_component is the component that will be responsible for all
    requests. By default this is BaseMC which does routing and not much
    else.

    The components option should be a list of components that will get
    appended to the depends_on attribute of the main_component to the
    effect of them being initialized - useful if the components that render
    views depend on something.
    """
    return create_app(mc_from_routemap(routemap))
