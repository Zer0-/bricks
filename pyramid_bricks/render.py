from pyramid.renderers import RendererHelper

def render_to_response(renderer_name, value, request, component):
    helper = RendererHelper(name=renderer_name)
    context = {'component': component}
    return helper.render_to_response(value, context, request=request)

def render(renderer):
    def render_decorator(viewfn):
        def wrapper(clsinst, context, request):
            view_result = viewfn(clsinst, request)
            return render_to_response(renderer, view_result, request, clsinst)
        return wrapper
    return render_decorator
