from os.path import join, dirname, split
from collections import defaultdict
from .asset import resolve_spec
from .staticfiles import StaticfileOptimizationLevel as Lvl
from .staticfiles import StaticCss, StaticJs

def traverse_deps(component, fn):
    for dep in getattr(component, 'depends_on', []):
        traverse_deps(dep, fn)
    fn(component)

def static_group_key(static_component, parent_component):
    if static_component.optim in (Lvl.NOOPT, Lvl.INLINE):
        return static_component
    elif static_component.optim == Lvl.CONCAT:
        return (static_component.bottom, static_component.relpath)
    elif static_component.optim == Lvl.CONCAT_PAGE:
        return (
            static_component.bottom,
            static_component.relpath,
            parent_component
        )

def _nice_name(name):
    if len(name) <= 5:
        if '-' in name or '_' in name:
            return True
        elif name.lower() != name:
            return True
        else:
            return False
    return True

def path_to_src(path):
    """
    Takes a filepath and gives us a (shorter) relative path to the asset.
    Used to determine the relative path from the served static directory to
    the asset for example.
    """
    dirpath, filename = split(path)
    subfolders = 1
    if not _nice_name(filename.split('.')[0]):
        subfolders = 2
    nice_path = []
    for part in dirpath.strip('/').split('/')[::-1]:
        if _nice_name(part):
            nice_path.append(part)
        if len(nice_path) >= subfolders:
            break
    return '/'.join(nice_path[::-1] + [filename])

def fetch_asset(url):
    from urllib import request
    with request.urlopen(url) as asset:
        return asset.read()

class StaticManager:
    requires_configured = ['json_settings']
    provides = ['static_manager']

    def __init__(self, settings):
        self.static_url = settings['served_static_url']
        self.static_components = {}

    def add(self, static_component):
        self.static_components[type(static_component)] = static_component

    def render_static(self, component):
        visited = set()
        to_render = []
        def append_static(c):
            if c not in visited and c in self.static_components:
                to_render.append(self.static_components[c])
                visited.add(c)
        traverse_deps(component, append_static)
        return ''.join(c() for c in to_render)

    def render_bottom_static(self, *_):
        """Dummy method for interchangability with OptimizingStaticManager"""
        return ''

    def get_url(self, static_component):
        asset_path = resolve_spec(static_component.asset)
        return self.static_url + path_to_src(asset_path)

class OptimizingStaticManager:
    provides = ['static_manager']
    requires_configured = ['bricks']

    def __init__(self, bricks):
        self.components = {}
        self.bricks = bricks

    def add(self, static_component):
        self.components[type(static_component)] = static_component

    def _group_component(self, parent, component, groupmap, static_processed):
        for dep in getattr(component, 'depends_on', []):
            self._group_component(parent, dep, groupmap, static_processed)
        if component in self.components:
            component = self.components[component]#get the instance
            key = static_group_key(component, parent)
            if (key, component) in static_processed:
                return
            static_processed.add((key, component))
            groupmap[key].append(component)

    def group_all(self):
        static_processed = set()
        groupmap = defaultdict(list)
        for component_type, component in self.bricks.components.items():
            #we are assuming that static components (those in self.components)
            #will be children of some parent component. Thus we ignore them
            #at the top level.
            if component_type in self.components:
                continue
            self._group_component(component, component_type, groupmap, static_processed)
        return groupmap

    def ordered_group(self, groupmap):
        groups = []
        for key, group in groupmap.items():
            groupstring = '\n'.join(resolve_spec(c.asset) for c in group)
            groups.append((key, groupstring))
        return sorted(groups, key=lambda i: i[1])

    def group_string(self, groupmap):
        return '\n\n'.join(s for _, s in self.ordered_group(groupmap))

    def make_group_url_map(self, groupmap, url_list):
        ordered_keys = [i for i, _ in self.ordered_group(groupmap)]
        return dict(zip(ordered_keys, url_list))

    def load_group_urls(self, url_list):
        #defer running this method until all [static] components have been initialized
        groups = self.group_all()
        url_map = self.make_group_url_map(groups, url_list)
        self.groupmap = {}
        for key, group in groups.items():
            self.groupmap[key] = self.gen_group_component(
                                            group[0], url_map[key])

    def map_component(self, static_component, parent):
        key = static_group_key(static_component, parent)
        return self.groupmap[key]

    def gen_group_component(self, component, group_url):
        if component.target_type == 'css':
            newtype = StaticCss
        elif component.target_type == 'js':
            newtype = StaticJs
        else:
            raise NotImplementedError()
        if component.optim == Lvl.INLINE:
            asset = fetch_asset(group_url)
        else:
            asset = group_url
        group = newtype(
            group_url,
            asset=asset,
            optim=component.optim,
            bottom=component.bottom
        )
        return self.bricks.add(group)

    def _render_static(self, component, bottom=False):
        visited = set()
        to_render = []
        def append_static(c):
            if c in self.components:
                c = self.components[c]
                if not c.bottom == bottom:
                    return
                key = static_group_key(c, component)
                if key not in visited:
                    to_render.append(c)
                    visited.add(c)
        traverse_deps(component, append_static)
        return ''.join(self._render(c) for c in to_render)

    def _render(self, static_component):
        if static_component.optim == Lvl.INLINE:
            if static_component.target_type == 'css':
                return '<style>{}</style>'.format(static_component.asset)
            elif static_component.target_type == 'js':
                return '<script>{}</script>'.format(static_component.asset)
            else:
                raise NotImplementedError()
        else:
            return static_component()

    def render_static(self, component):
        return self._render_static(component)

    def render_bottom_static(self, component):
        return self._render_static(component, bottom=True)

    def get_url(self, *_):
        return ""
