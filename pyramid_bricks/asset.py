import pkg_resources

def resolve_spec(asset_spec):
    pkg, filename = asset_spec.split(':', 1)
    return pkg_resources.resource_filename(pkg, filename)
