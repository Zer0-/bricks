from ceramic_forms import Form

def _match_pathpart(routemap, part):
    #wrap schema and pathpart in a list because Form cannot handle naked values.
    subject = [part]
    for key in routemap:
        validator = Form([key])
        if validator.validate(subject):
            return validator.cleaned[0], routemap[key]

def _match_routes(path, routemap):
    matched = [('/', routemap)]
    for part in path:
        match = _match_pathpart(routemap, part)
        if match is None:
            if routemap.handles_subtree == False:
                return 404
        else:
            part, routemap = match
        matched.append((part, routemap))
    return matched

class RequestRoute:
    def __init__(self, request, routemap):
        self.routemap = routemap
        path = [p for p in request.path.split('/') if len(p)]
        self._matched_routes = _match_routes(path, routemap)

    @property
    def path(self):
        return [p for p, _ in self._matched_routes[1:]]

    @property
    def vars(self):
        routemap = self.routemap
        vars = []
        for part, route in self._matched_routes:
            if part in routemap:
                routemap = route
            elif route != routemap:
                vars.append(part)
                routemap = route
        return vars

    @property
    def route(self):
        return self._matched_routes[-1][1]

