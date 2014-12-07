import os
from os.path import join, dirname, isdir, exists
from shutil import copyfile
from .asset import resolve_spec
from .static_manager import path_to_src
import logging

def copytree(src, dst, symlinks=False, ignore=None):
    if not exists(dst):
        os.makedirs(dst)
    for item in os.listdir(src):
        s = join(src, item)
        d = join(dst, item)
        if isdir(s):
            copytree(s, d, symlinks, ignore)
        else:
            if not exists(d) or os.stat(src).st_mtime - os.stat(dst).st_mtime > 1:
                logging.debug("{} -> {}".format(s, d))
                copyfile(s, d)

def establish_static_assets(bricks):
    settings = bricks.components.get('json_settings')
    if settings is None:
        raise ValueError("Settings not loaded into bricks app, cannot establish static assets.")
    static_manager = bricks.components.get('static_manager')
    asset_components = static_manager.static_components.values()
    for asset in asset_components:
        if not hasattr(asset, 'asset') or asset.asset.startswith('http'):
            continue
        if asset.has_build_stage:
            root_dir = settings.get('static_buildout_dir')#change to static_stage_dir
            if root_dir is None:
                raise ValueError("No 'static_buildout_dir' setting "
                                 "found in app settings")
        else:
            root_dir = settings.get('served_static_dir')
            if root_dir is None:
                raise ValueError("No 'served_static_dir' setting "
                                 "found in app settings")
        asset_path = resolve_spec(asset.asset)
        dest = join(root_dir, path_to_src(asset_path))
        dest_dir = dirname(dest)
        if not exists(dest_dir):
            os.makedirs(dest_dir, exist_ok=True)
        if isdir(asset_path):
            copytree(asset_path, dest)
        else:
            logging.debug("{} -> {}".format(asset_path, dest))
            copyfile(asset_path, dest)
