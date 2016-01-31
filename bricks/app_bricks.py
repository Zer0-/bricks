from webob import Request, Response
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

    provides = ['bricks']

    def __init__(self):
        self.components = {Bricks: self, 'bricks': self}

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

def wsgi(main_component):
    def wsgi_app(environ, start_response):
        request = Request(environ)
        response = Response()
        try:
            result = main_component(request, response)
        except HTTPException as e:
            result = e
        if isinstance(result, HTTPException) and request.route._matched_routes != 404:
            #check the current Route for components that handle HTTPExceptions
            #be careful - since the main_component is responsible for attaching
            #the route api to the request, request.route may not exist.
            exception_handlers = request.route.route.exc_handlers
            err_handler = exception_handlers.get(type(result), {})
            err_view = getattr(err_handler, request.method, None)
            if err_view is not None:
                result = err_view(request, response)
        if isinstance(result, Response):
            response = result
        return response(environ, start_response)

    return wsgi_app

class BaseMC:
    server_prefix = ''

    def __init__(self, routemap, *args):
        self.routemap = routemap

    def get_view(self, request):
        request.route = RouteApi(request, self.routemap, self.server_prefix)
        if request.route._matched_routes == 404:
            raise HTTPNotFound()
        route = request.route.route
        view = route.get_view(request)
        if view is None:
            raise HTTPNotFound()
        return view

    def __call__(self, request, response):
        return self.get_view(request)(request, response)
