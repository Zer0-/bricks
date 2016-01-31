from ceramic_forms import Form

class Route:
    def __init__(
        self,
        name=None,
        handler=None,
        permissions=(),
        handles_subtree=False,
        httpexception_handlers=dict(),
        routemap=dict(),
    ):
        self.name = name
        self.routemap = routemap
        self.permissions = permissions
        self.handles_subtree = handles_subtree
        self.handler = handler
        self.depends_on = [handler] if handler is not None else []
        self.depends_on += list(routemap.values())
        self.exc_handlers = getattr(self, 'httpexception_handlers', {})
        self.exc_handlers.update(httpexception_handlers)
        self._original_exc_handlers = frozenset(self.exc_handlers.items())
        self.depends_on += list(self.exc_handlers.values())

    def __call__(self, *deps):
        self.component = None if self.handler is None else deps[0]
        for i, (http_exc, handler) in enumerate(self.exc_handlers.items()):
            self.exc_handlers[http_exc] = deps[1+len(self.routemap)+i]
        return self

    def get_view(self, request):
        return getattr(self.component, request.method, None)

    def values(self):
        return self.routemap.values()

    def items(self):
        return self.routemap.items()

    def _defining_attributes(self):
        return (
            self.name,
            self.handler,
            self.permissions,
            self.handles_subtree,
            self._original_exc_handlers
        )

    def __add__(self, routemap):
        return Route(
            name=self.name,
            handler=self.handler,
            permissions=self.permissions,
            handles_subtree=self.handles_subtree,
            httpexception_handlers=dict(self._original_exc_handlers),
            routemap=routemap
        )

    def __eq__(self, other):
        return self._defining_attributes() == other._defining_attributes()

    def __hash__(self):
        return hash(self._defining_attributes())

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
        info = []
        if self.name:
            info.append('name: {}'.format(self.name))
        if self.handler:
            if type(self.handler) is type:
                info.append('handler: {}'.format(self.handler.__name__))
            else:
                info.append('handler: {}'.format(self.handler.__class__.__name__))
        if self.permissions:
            info.append('permissions: ' + str(self.permissions))
        if self.routemap:
            info.append('contains {} routes'.format(len(self.routemap)))
        if self.exc_handlers:
            info.append("handles exceptions: True")
        return "<{} {}>".format(
            self.__class__.__name__,
            ", ".join(info) if info else ""
        )

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
    def __init__(self, request, routemap, prefix=''):
        self.routemap = routemap
        path = [p for p in request.path.split('/') if len(p)]
        self._matched_routes = _match_routes(path, routemap)
        self.prefix = prefix + '/'

    @property
    def path(self):
        return [p for p, _ in self._matched_routes[1:]]

    @property
    def vars(self):
        routemap = self.routemap
        vars = []
        for part, route in self._matched_routes[1:]:
            if part in routemap:
                routemap = route
            else:
                vars.append(part)
                if route != routemap:
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

    def find(self, routename, path_args=()):
        def match(path):
            return len([i for i in path if not isinstance(i, str)]) == \
                    len(path_args)

        for path, existing_route in iter_routemap(self.routemap):
            if routename == existing_route.name:
                arg_iter = iter(path_args)
                if existing_route.handles_subtree:
                    arg_iter = arg_iter
                    filled_path = _fill_path(path, arg_iter)
                    if filled_path is False:
                        continue
                    return path_to_urlpart(
                            filled_path + list(arg_iter),
                            self.prefix
                            )
                elif match(path):
                    filled_path = _fill_path(path, arg_iter)
                    if filled_path is False:
                        continue
                    return path_to_urlpart(filled_path, self.prefix)

def path_to_urlpart(path, prefix='/'):
    return prefix + '/'.join(str(i) for i in path)

def _fill_path(path, path_args):
    filled_path = []
    for pathpart in path:
        if isinstance(pathpart, str):
            filled_path.append(pathpart)
        else:
            validator = Form([pathpart])
            if not validator.validate([next(path_args)]):
                return False
            filled_path.append(validator.cleaned[0])
    return filled_path

def iter_routemap(routemap, path=[]):
    yield path, routemap
    for pathpart, route in routemap.items():
        yield from iter_routemap(route, path + [pathpart])

def routeset(routemap):
    return set(i for _, i in iter_routemap(routemap))
