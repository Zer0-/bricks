from pyramid.renderers import render_to_response

def render(renderer):
    def render_decorator(viewfn):
        def wrapper(clsinst, context, request):
            view_result = viewfn(clsinst, request)
            return render_to_response(renderer, view_result)
        return wrapper
    return render_decorator
