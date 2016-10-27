from dric import Pass
from inspect import getsourcefile
from os.path import dirname, join, abspath, splitext
from os import listdir
from logging import getLogger
from yaml import load as reader_yaml_load
from configparser import ConfigParser

_logger = getLogger('dric.support.configuration_pass')

configuration_file_readers = {}

class Configurable(object):
    def __init__(self, file, id=None):
        self.file = file
        self.id = id
    def __call__(self, class_):
        class_.dric_support_configurable = True

        config_id_path = (self.id, self.file)
        if(hasattr(class_, 'dric_configuration_file')):
            class_.dric_configuration_file.append(config_id_path)
        else:
            class_.dric_configuration_file = [config_id_path]
        return class_

class ConfigurePass(Pass):
    def load(self, plugin, name):
        if(hasattr(plugin.__class__, 'dric_support_configurable') and plugin.__class__.dric_support_configurable is True):
            dir = dirname(getsourcefile(plugin.__class__))
            
            config_id_paths = plugin.__class__.dric_configuration_file

            for config_id_path in config_id_paths:
                absolute_path = abspath(join(dir, config_id_path[1]))
                try:
                    configuration = _read_configuration_file(absolute_path)
                    plugin.configure(Configuration(configuration, config_id_path[0], config_id_path[1]))
                except _NoConfigurationReader as e:
                    _logger.warn('No configuration reader for file %s (extension "%s")', e.path, e.file_extension)

class Configuration(object):
    def __init__(self, configuration, id, file):
        self.configuration = configuration
        self.id = id
        self.file = file

def _read_configuration_file(path):
    file_extension = splitext(path)[1]
    if(file_extension in configuration_file_readers):
        reader = configuration_file_readers[file_extension]
        config = reader.read(path)
        return config
    else:
        raise _NoConfigurationReader(path, file_extension)

class _NoConfigurationReader(Exception):
    def __init__(self, path, file_extension):
        self.path = path
        self.file_extension = file_extension

def reader(*exts):
    def decorator(decorated_reader):
        decorated_reader.read = decorated_reader
        for ext in exts:
            configuration_file_readers[ext] = decorated_reader
        return decorated_reader
    return decorator

@reader('.yml')
def yaml_reader(path):
    return reader_yaml_load(file(path, 'r'))

@reader('.ini')
def configparser_reader(path):
    parser = ConfigParser()
    parser.read(path)
    dictionary = {}
    for section in parser.sections():
        dictionary[section] = {}
        for option in parser.options(section):
            dictionary[section][option] = parser.get(section, option)
    return dictionary