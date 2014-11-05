from os.path import join, basename
from collections import defaultdict
from .asset import resolve_spec
from bricks.staticfiles import StaticfileOptimizationLevel as Lvl

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

    def get_url(self, static_component):
        asset_path = resolve_spec(static_component.asset)
        return self.static_url +\
            join(
                static_component.relpath,
                basename(asset_path)
            )

class OptimizingStaticManager:
    provides = ['static_manager']

    def __init__(self):
        self.components = {}

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

    def group_all(self, bricks):
        static_processed = set()
        groupmap = defaultdict(list)
        for component_type, component in bricks.components.items():
            if component_type in self.components:
                continue
            self._group_component(component, component, groupmap, static_processed)
        return groupmap

    def ordered_group(self, groupmap):
        groups = []
        for key, group in groupmap.items():
            groupstring = '\n'.join(resolve_spec(c.asset) for c in group)
            groups.append((key, groupstring))
        return sorted(groups, key=lambda i: i[1])

    def group_string(self, groupmap):
        return '\n\n'.join(s for _, s in self.ordered_group(groupmap))

    def get_url(self, component):
        pass
