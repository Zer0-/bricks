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

def create_app(main_component, dependencies=[], routemap=None):
    bricks = Bricks()
    for component in dependencies:
        bricks.add(component)
    main = bricks.add(main_component)

    def wsgi_app(environ, start_response):
        request = Request(environ)
        response = Response()
        try:
            result = main(request, response)
        except HTTPException as e:
            result = e
        if isinstance(result, HTTPException):
            #check the current Route for components that handle HTTPExceptions
            #be careful - since the main component is responsible for attaching
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
    def __init__(self, *args):
        self.routemap = args[-1]

    @staticmethod
    def not_found_view(*args):
        return HTTPNotFound()

    def get_view(self, request):
        request.route = RouteApi(request, self.routemap)
        if request.route._matched_routes == 404:
            return self.not_found_view
        route = request.route.route
        view = route.get_view(request)
        if view is None:
            return self.not_found_view
        route = request.route.route
        return view

    def __call__(self, request, response):
        return self.get_view(request)(request, response)

def mc_from_routemap(routemap, base_component=BaseMC):
    deps = []
    if hasattr(base_component, 'depends_on'):
        deps += base_component.depends_on
    deps.append(routemap)
    return type(
        "MainComponent",
        (base_component,),
        dict(depends_on=deps)
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
    return create_app(mc_from_routemap(routemap, main_component), components, routemap)
