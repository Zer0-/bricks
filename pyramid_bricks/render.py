from pyramid.renderers import RendererHelper

def render_to_response(renderer):
    def render_decorator(viewfn):
        def wrapper(clsinst, request):
            view_result = viewfn(clsinst, request)
            helper = RendererHelper(name=renderer)
            context = {'component': clsinst, 'request': request}
            return helper.render_to_response(view_result, context, request=request)
        return wrapper
    return render_decorator

def render(renderer):
    def render_decorator(viewfn):
        def wrapper(clsinst, *args, **kwargs):
            view_result = viewfn(clsinst, *args, **kwargs)
            helper = RendererHelper(name=renderer)
            context = {'component': clsinst}
            return helper.render(view_result, context)
        return wrapper
    return render_decorator
