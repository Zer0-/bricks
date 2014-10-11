from collections import defaultdict
from bricks.staticfiles import StaticfileOptimizationLevel as Lvl

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
