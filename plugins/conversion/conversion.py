import dric

from logging import getLogger
from os.path import join, abspath, dirname

from py_expression_eval import Parser
import xml.etree.ElementTree as etree

from .jsgen import JavascriptFileGenerator

_logger = getLogger('dric.conversion')

class Edge(object):
    def __init__(self, from_vertex, to_vertex, expr):
        self.from_vertex = from_vertex
        self.to_vertex = to_vertex
        self.expr = expr

    def __repr__(self):
        return '{{"from":"{}", "to":"{}", "expr":"{}"}}'.format(self.from_vertex, self.to_vertex, self.expr)

class ConversionGraph(object):
    def __init__(self):
        self.edges = []
        self.parser = Parser()
        self.cache = {}

    def add_edge(self, from_vertex, to_vertex, expr):
        self.edges.append(Edge(from_vertex, to_vertex, expr))

    def convert(self, from_unit, to_unit, value):
        key = (from_unit, to_unit) 
        if key not in self.cache:
            path = self.find_shortest_conversion_path(from_unit, to_unit)
            if path is None:
                compiled = None
            else:
                compiled = self.parser.parse('x')
                for edge in path:
                    compiled = compiled.substitute('x', edge.expr)
                compiled = compiled.simplify({})
                _logger.debug('Add compiled conversion from %s to %s to cache: %s', from_unit, to_unit, compiled.toString())
            self.cache[key] = compiled
        
        compiled = self.cache[key]
        if compiled is None:
            return None
        return compiled.evaluate({'x':value})

    def find_shortest_conversion_path(self, from_vertex, to_vertex):
        def recursive_search(from_vertex, to_vertex, history):
            path = None
            if from_vertex == to_vertex:
                return []
            for edge in history:
                if edge.from_vertex == from_vertex:
                    return None
            for edge in self.edges:
                if edge not in history and edge.from_vertex == from_vertex:
                    history.append(edge)
                    new_path = recursive_search(edge.to_vertex, to_vertex, history)
                    history.pop()
                    if new_path is not None and (path is None or len(new_path) < len(path)):
                        path = new_path
                        path.append(edge)
            return path

        path = recursive_search(from_vertex, to_vertex, [])
        return path

class ConversionPlugin(dric.Plugin):

    def __init__(self, *args, **kwargs):
        self.conversion_graph = ConversionGraph()
        self.js = ''
        self.quantities = {}

    def setup(self, bus):
        # read file conversions.xml 
        conversions_xml = join(abspath(dirname(__file__)), 'conversions.xml')
        _logger.debug('parsing file %s', conversions_xml)
        tree = etree.parse(conversions_xml)
        root = tree.getroot()

        for child in root:
            from_vertex = child.attrib['from']
            to_vertex = child.attrib['to']
            expr = child.text
            _logger.debug("Adding conversion from %s to %s: %s", from_vertex, to_vertex, expr)
            self.conversion_graph.add_edge(from_vertex, to_vertex, expr)

            quantity = child.attrib['quantity']
            if quantity not in self.quantities:
                self.quantities[quantity] = []
            if to_vertex not in self.quantities[quantity]:
                self.quantities[quantity].append(to_vertex);
            if from_vertex not in self.quantities[quantity]:
                self.quantities[quantity].append(from_vertex);

        # TODO: unit testing:
        _logger.info("from K to F: %s", repr(self.conversion_graph.find_shortest_conversion_path("K", "F")))
        _logger.info("from F to K: %s", repr(self.conversion_graph.find_shortest_conversion_path("F", "K")))
        _logger.info("from C to mm: %s", repr(self.conversion_graph.find_shortest_conversion_path("C", "mm")))

        _logger.info("300K to F: %s", repr(self.conversion_graph.convert("K", "F", 300)))
        _logger.info("0K to F: %s", repr(self.conversion_graph.convert("K", "F", 0)))
        _logger.info("150F to C: %s", repr(self.conversion_graph.convert("F", "C", 150)))
        _logger.info("20mm to m: %s", repr(self.conversion_graph.convert("mm", "m", 20)))
        _logger.info("50m to K: %s", repr(self.conversion_graph.convert("m", "K", 50)))
        _logger.info("50m to schmurfs: %s", repr(self.conversion_graph.convert("m", "schmurf", 50)))        

    @dric.route('conversion_js', '/core/conversions/_/conversion.js')
    def serve_conversion_js(self, request):
        return dric.Response(JavascriptFileGenerator(self.conversion_graph, self.quantities).get_file_content(), content_type='application/javascript')

    @dric.on('convert')
    def convert(self, from_unit, to_unit, value):
        return self.conversion_graph.convert(from_unit, to_unit, value)

dric.register(__name__, ConversionPlugin())
dric.support.inject_content_script('/core/conversions/_/conversion.js', runat='start')
dric.support.inject_content_script('/content/core/conversion/dist/js/conversion.js')