from mako.template import Template
from pyramid.path import AssetResolver
from pyramid_mako import PkgResourceTemplateLookup

def string_response(viewfn):
    def wrapper(clsinst, request, response):
        view_result = viewfn(clsinst, request, response)
        response.content_type =  'text/plain'
        response.text = view_result
    return wrapper

def json_response(viewfn):
    from json import dumps
    def wrapper(clsinst, request, response):
        view_result = viewfn(clsinst, request, response)
        response.content_type = 'application/json'
        response.text = view_result
    return wrapper

def mako_response(template_assetspec):
    template_filepath = AssetResolver().resolve(template_assetspec).abspath()
    template = Template(filename=template_filepath,
                        lookup=PkgResourceTemplateLookup())
    def render_decorator(viewfn):
        def wrapper(clsinst, request, response):
            view_result = viewfn(clsinst, request, response)
            context = {'component': clsinst, 'request': request}
            context.update(view_result)
            body = template.render(**context)
            response.text = body
            response.content_type = 'text/html'
        return wrapper
    return render_decorator
