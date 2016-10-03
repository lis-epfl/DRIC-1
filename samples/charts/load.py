import dric
import dric.support

contentScripts = [
    {'path': '/content/samples/charts/js/charts.js'}
]
dric.register(__name__, dric.support.ContentScriptInjector(contentScripts));