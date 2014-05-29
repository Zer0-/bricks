from ceramic_forms import Form

def _matches_pathpart(url_tree, pathpart):
    if pathpart in url_tree:
        return pathpart
    #wrap schema and pathpart in a list because Form cannot handle naked values.
    subject = [pathpart]
    for route in url_tree:
        validator = Form([route])
        if validator.validate(subject):
            return route
    return False

def routing(url_tree, request):
    pathparts = [p for p in request.path.split('/') if len(p)]
    for part in pathparts:
        match = _matches_pathpart(url_tree, part)
        if match is not False:
            url_tree = url_tree[match]
        elif url_tree.handles_subtree:
            pass
        else:
            return 404
    return url_tree
