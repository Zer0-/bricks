import os
from os.path import join, basename, isdir, exists
from os import makedirs
from shutil import copyfile
import logging

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
                logging.debug("{} -> {}".format(s, d))
                copyfile(s, d)

def establish_static_assets(bricks):
    settings = bricks.components.get('json_settings')
    if settings is None:
        raise ValueError("Settings not loaded into bricks app, cannot establish static assets.")
    static_manager = bricks.components.get('static_manager')
    asset_components = static_manager.static_components.values()
    for asset in asset_components:
        if not hasattr(asset, 'asset'):
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
        filename = basename(asset.asset_path)
        dest = join(root_dir, asset.relpath)
        if not exists(dest):
            makedirs(dest, exist_ok=True)
        outfilepath = join(dest, filename)
        if isdir(asset.asset_path):
            copytree(asset.asset_path, outfilepath)
        else:
            logging.debug("{} -> {}".format(asset.asset_path, outfilepath))
            copyfile(asset.asset_path, outfilepath)
