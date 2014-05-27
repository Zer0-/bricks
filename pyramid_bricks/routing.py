def routing(url_tree, request):
    pathparts = [p for p in request.path.split('/') if len(p)]
    for part in pathparts:
        if part in url_tree:
            url_tree = url_tree[part]
        else:
            return 404
    return url_tree
