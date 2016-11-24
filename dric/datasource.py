import dric
import logging

_logger = logging.getLogger('dric.datasource')

def datasource(name):
    """
A function decorator for datasources. 
    """
    def datasource_wrap(func):
        func.datasource_name = name
        return func
    return datasource_wrap

_datasources = {}

def add_datasource(source_name, source):
    _logger.debug('Add source %s', source_name)
    _datasources[source_name] = source

def remove_datasource(source_name, source):
    _datasources[source_name] = source

class DatasourceEndpoint(object):
    def has_source(self, source_name):
        return source_name in _datasources
    def source(self, source_name):
        return _datasources[source_name]
    def sources(self):
        return dict(_datasources)

class DatasourcePass(dric.Pass):
    def load(self, plugin, name):
        # Iterate over all class attributes
        for method_name in dir(plugin):
            method = getattr(plugin, method_name)
            if callable(method):    # only methods
                if hasattr(method, 'datasource_name'):
                    source_name = getattr(method, 'datasource_name')
                    _logger.debug('Datasource %s found: %s', source_name, method)
                    add_datasource(source_name, method)