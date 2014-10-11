from os.path import join, basename
from collections import defaultdict
from .asset import resolve_spec
from bricks.staticfiles import StaticfileOptimizationLevel as Lvl

class StaticManager:
    requires_configured = ['json_settings']
    provides = ['static_manager']

    def __init__(self, settings):
        self.static_url = settings['served_static_url']
        self.static_components = {}

    def add(self, static_component):
        self.static_components[type(static_component)] = static_component

    def render_static(self, component, visited=None):
        if visited is None:
            visited = set()
        if component in visited:
            return ''
        visited.add(component)
        resources_string = self.static_components.get(component, str)()
        return resources_string + ''.join(
            [self.render_static(dep, visited)
             for dep in getattr(component, 'depends_on', [])]
        )

    def get_url(self, static_component):
        asset_path = resolve_spec(static_component.asset)
        return self.static_url +\
            join(
                static_component.relpath,
                basename(asset_path)
            )

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

class OptimizingStaticManager:
    provides = ['static_manager']

    def __init__(self):
        self.components = {}

    def add(self, static_component):
        self.components[type(static_component)] = static_component

    def _group_component(self, parent, component, groups, static_processed):
        for dep in getattr(component, 'depends_on', []):
            self._group_component(parent, dep, groups, static_processed)
        if component in self.components:
            component = self.components[component]#get the instance
            key = static_group_key(component, parent)
            if (key, component) in static_processed:
                return
            static_processed.add((key, component))
            groups[key].append(component)

    def group_all(self, bricks):
        static_processed = set()
        groups = defaultdict(list)
        for component in bricks.components.values():
            if component in self.components:
                continue
            self._group_component(component, component, groups, static_processed)
        return groups
