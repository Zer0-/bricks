from mako.template import Template
from .asset import resolve_spec
from .mako_lookup import ResourceTemplateLookup

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
        response.text = dumps(view_result)
    return wrapper

def mako_response(template_assetspec):
    template_filepath = resolve_spec(template_assetspec)
    template = Template(
        filename=template_filepath,
        lookup=ResourceTemplateLookup(),
        input_encoding='utf-8',
    )
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

def mako_render(template_assetspec):
    template_filepath = resolve_spec(template_assetspec)
    template = Template(
        filename=template_filepath,
        lookup=ResourceTemplateLookup(),
        input_encoding='utf-8',
    )
    def render_decorator(viewfn):
        def wrapper(clsinst, *args, **kwargs):
            view_result = viewfn(clsinst, *args, **kwargs)
            context = {'component': clsinst}
            context.update(view_result)
            return template.render(**context)
        return wrapper
    return render_decorator
