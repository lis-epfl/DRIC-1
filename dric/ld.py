"""
    Execute plugins. 
"""

import dric.router
import dric.static
import imp
import json
import logging
import os
import os.path
import re
import sys
from future.utils import iteritems

from importlib import import_module

_logger = logging.getLogger('dric.ld')

def load_plugins(plugin_dirs=['core', 'plugins', 'samples']):
    # appends the plugin_dirs to path
    for d in plugin_dirs:
        sys.path.append(os.path.abspath(d))

    for plugin_dir in plugin_dirs:
        print(plugin_dir)
        if(os.path.isdir(plugin_dir) is True):
            _load_plugins_in_dir(plugin_dir)
        else:
            _logger.warn('Directory ignored: %s (not a directory)', plugin_dir)

def _load_plugins_in_dir(dir):
    """ Load all plugins in directory dir """
    # List all plugins dirs inside dir
    plugin_dirs = os.listdir(dir)
    # Iterate over each dir to find the manifest file of each plugin
    for pdir in plugin_dirs:
        plugin_basedir = os.path.join(dir, pdir)
        ignore_path = os.path.join(plugin_basedir, '.dricignore')
        manifest_path = os.path.join(plugin_basedir, 'plugin.json')
        # check if pdir is a directory
        if(os.path.isdir(plugin_basedir) is False):
            _logger.warn('Directory ignored: %s (not a directory)', plugin_dir)
            continue
        # check if directory contains a file named '.dricignore'
        if(os.path.isfile(ignore_path) is True):
            _logger.warn('Directory ignored: %s (file .dricignore present)', plugin_basedir)
            continue
        # check if directory contains a manifest file
        if(os.path.isfile(manifest_path) is False):
            _logger.warn('Directory ignored: (unable to find plugin.json)', plugin_basedir)
            continue
        # load plugin.json
        with open(manifest_path) as manifest_file:
            manifest = json.load(manifest_file)
            _load_plugin(plugin_basedir, manifest)


def _load_plugin(pdir, manifest):
    """ Load one plugin in directory pdir """
    # retrieve info from manifest file
    # the plugin id
    id = manifest['id']
    
    # id must be an alphanumeric string
    if(re.match('[a-zA-Z]+', id) is False):
        _logger.error('Invalid plugin id: "%s"', id)
        return
    
    if 'routes' in manifest:
        _load_routes(manifest['routes'])
    if 'static_files' in manifest:
        _load_static_files(manifest['static_files'], pdir)
    if 'static_dirs' in manifest:
        _load_static_dirs(manifest['static_dirs'], pdir)
    
    # attempt to load plugin as a package (Python>=3.4 only!)
    name = os.path.basename(pdir)
    pck = import_module(name)

    #if 'load' in manifest:
    #    _load_files(pdir, manifest['load'], id)


def _load_files(pdir, files_to_load, id):
    i = -1
    # load all module files
    for file in files_to_load:
        modulefile = os.path.join(pdir, file)
        #find a name for the module to load
        while True:
            i += 1
            name = id + '_' + str(i)
            if(name not in sys.modules):
                break
            if(i == sys.maxint):
                _logger.error('Could not give a name to module %s', modulefile)
                return
        # load the module
        imp.load_source(name, modulefile)

def _load_routes(routes):
    for (url, route ) in iteritems(routes):
        dric.router.add(url, route)

def _load_static_files(files, pdir):
    for (url, f) in iteritems(files):
        dric.router.add(url, 'static_file')
        dric.static.add_file(pdir, f, url)

def _load_static_dirs(dirs, pdir):
    for (url, d) in iteritems(dirs):
        dir_url = '{0}<path:fpath>'.format(url)
        dric.router.add(dir_url, 'static_dir')
        dric.static.add_dir(pdir, d, url)