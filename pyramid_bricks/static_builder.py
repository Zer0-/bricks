from pyramid.path import AssetResolver
import os
from os.path import join, basename, isdir
from os import makedirs
from shutil import copyfile

def copytree(src, dst, symlinks=False, ignore=None):
    if not os.path.exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not os.path.exists(d) or os.stat(src).st_mtime - os.stat(dst).st_mtime > 1:
                copyfile(s, d)

def establish_static_assets(pbricks):
    settings = pbricks.components.get('json_settings')
    if settings is None:
        raise ValueError("establish_static app to have a settings component")
    static_manager = pbricks.components.get('static_manager')
    asset_components = static_manager.static_components.values()
    for asset in asset_components:
        if not hasattr(asset, 'asset'):
            continue
        if asset.has_build_stage:
            root_dir = settings.get('static_buildout_dir')
            if root_dir is None:
                raise ValueError("No 'static_buildout_dir' setting "
                                 "found in app settings")
        else:
            root_dir = settings.get('served_static_dir')
            if root_dir is None:
                raise ValueError("No 'static_buildout_dir' setting "
                                 "found in app settings")
        filename = basename(asset.asset_path)
        dest = join(root_dir, asset.relpath)
        makedirs(dest, exist_ok=True)
        if isdir(asset.asset_path):
            copytree(asset.asset_path, join(dest, filename))
        else:
            copyfile(asset.asset_path, join(dest, filename))
