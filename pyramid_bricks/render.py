from webob import Response
from mako.template import Template
from pyramid.path import AssetResolver

def _response(body, mime):
    response = Response(content_type=mime)
    response.text = body
    return response

def string_response(viewfn):
    def wrapper(clsinst, request):
        view_result = viewfn(clsinst, request)
        return _response(view_result, 'text/plain')
    return wrapper

def json_response(viewfn):
    from json import dumps
    def wrapper(clsinst, request):
        view_result = viewfn(clsinst, request)
        return _response(dumps(view_result), 'application/json')
    return wrapper

def mako_response(template_assetspec):
    template_filepath = AssetResolver().resolve(template_assetspec).abspath()
    template = Template(filename=template_filepath)
    def render_decorator(viewfn):
        def wrapper(clsinst, request):
            view_result = viewfn(clsinst, request)
            context = {'component': clsinst, 'request': request}
            context.update(view_result)
            return _response(template.render(**context), 'text/html')
        return wrapper
    return render_decorator
