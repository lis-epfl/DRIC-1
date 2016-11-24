from os.path import join, dirname
from pystache import render, parse

class JavascriptFileGenerator(object):
    def __init__(self, graph, quantities):
        self.edges = graph.edges
        self.quantities = quantities

    def get_file_content(self):
        with open(join(dirname(__file__), 'templates', 'conversions.template.js'), 'r') as template_file:
            return render(parse(unicode(template_file.read())), {'edges': self.edges, 'quantities': self.quantities})
        return ''