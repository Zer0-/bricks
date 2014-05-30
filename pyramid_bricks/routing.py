from ceramic_forms import Form

class RequestRouteApi:
    def __init__(self, vars):
        self.vars = vars

def _matches_pathpart(url_tree, pathpart):
    #wrap schema and pathpart in a list because Form cannot handle naked values.
    subject = [pathpart]
    for route in url_tree:
        validator = Form([route])
        if validator.validate(subject):
            return (validator.cleaned[0], route)
    return False

def routing(url_tree, request):
    pathparts = [p for p in request.path.split('/') if len(p)]
    vars = []#variable url paths that we components will use
    for part in pathparts:
        if part in url_tree:
            url_tree = url_tree[part]
            continue
        match = _matches_pathpart(url_tree, part)
        if match is not False:
            varpart, varmatch = match
            vars.append(varpart)
            url_tree = url_tree[varmatch]
        elif url_tree.handles_subtree:
            pass
        else:
            return 404
    request.route = RequestRouteApi(vars)
    return url_tree
