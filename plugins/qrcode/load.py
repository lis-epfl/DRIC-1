import dric
import dric.support

contentScripts = [
    {'path': '/content/plugins/qrcode/js/script.js'},
    {'path': '/content/plugins/qrcode/js/jquery.qrcode.min.js'}
]
dric.register(__name__, dric.support.ContentScriptInjector(contentScripts));