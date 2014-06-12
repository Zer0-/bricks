from ceramic_forms import Form

class Route:
    def __init__(
        self,
        handler=None,
        permissions=(),
        handles_subtree=False,
        httpexception_handlers=dict(),
        routemap=dict(),
    ):
        self.routemap = routemap
        self.permissions = permissions
        self.handles_subtree = handles_subtree
        self.handler = handler
        self.depends_on = [handler] if handler is not None else []
        self.exc_handlers = getattr(self, 'httpexception_handlers', {})
        self.exc_handlers.update(httpexception_handlers)
        self.depends_on += list(self.exc_handlers.values())

    def __call__(self, component=None):
        self.component = component
        return self

    def get_view(self, request):
        return getattr(self.component, request.method, None)

    def values(self):
        return self.routemap.values()

    def _defining_attributes(self):
        return (
            self.handler,
            self.permissions,
            self.handles_subtree,
            self.exc_handlers
        )

    def __add__(self, routemap):
        return Route(*self._defining_attributes() + (routemap,))

    def __eq__(self, other):
        return self._defining_attributes() == other._defining_attributes()

    def __hash__(self):
        return hash((tuple(self.depends_on), self.handles_subtree, self.permissions))

    def __setitem__(self, *args, **kwargs):
        return self.routemap.__setitem__(*args, **kwargs)

    def __getitem__(self, *args, **kwargs):
        return self.routemap.__getitem__(*args, **kwargs)

    def __contains__(self, key):
        return self.routemap.__contains__(key)

    def __iter__(self):
        for key in self.routemap:
            yield key

    def __repr__(self):
        return "<Route {}>".format(id(self))

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

class RouteApi:
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
        return tuple(vars)

    @property
    def relative(self):
        routemap = self.routemap
        relative_paths = []
        current_relative = []
        for part, route in self._matched_routes:
            if route == routemap and route.handles_subtree:
                current_relative.append(part)
            else:
                routemap = route
                if current_relative:
                    relative_paths.append(tuple(current_relative))
                    current_relative = []
        if current_relative:
            relative_paths.append(tuple(current_relative))
        return tuple(relative_paths)

    @property
    def route(self):
        return self._matched_routes[-1][1]

    @property
    def routes(self):
        visited = set()
        return [r for _, r in self._matched_routes\
                    if r not in visited and not visited.add(r)]

def _routeset(routemap, routeset):
    for value in routemap.values():
        routeset.add(value)
        _routeset(value, routeset)
    return routeset

def routeset(routemap):
    routeset = set()
    routeset.add(routemap)
    return _routeset(routemap, routeset)
