"""
Provides the DRIC index page. 
"""
import codecs
import dric
import os.path
import pystache

class IndexProvider(dric.Plugin):
    def __init__(self):
        self.__content_scripts = {
            'css':[],
            'css_async':[],
            'js_start':[],
            'js_end':[],
            'js_async':[]
        }
    
    def setup(self, eventbus):
        self.__eventbus = eventbus
    

    def start(self):
        # retrieve all content scripts (js or css) from all plugins
        # to be loaded asynchronously
        content_scripts = self.__eventbus.publish('index.contentscript')
        self.__config_content_scripts(content_scripts)

        
    def __config_content_scripts(self, content_scripts):
        for content_script in content_scripts:
            if isinstance(content_script, list):
                self.__config_content_scripts(content_script)
            else:
                self.__config_content_script(content_script)
                
    def __config_content_script(self, content_script):
        if 'runat' in content_script:
            runat = content_script['runat']
        else:
            runat = None
        if content_script['path'].endswith('.css'):
            #if runat == 'async':
            #    self.__content_scripts['css_async'].append(content_script['path'])
            #else:
            self.__content_scripts['css'].append(content_script['path'])
        elif content_script['path'].endswith('.js'):
            if runat == 'start':
                self.__content_scripts['js_start'].append(content_script['path'])
            elif runat == 'end':
                self.__content_scripts['js_end'].append(content_script['path'])
            else:
                self.__content_scripts['js_async'].append(content_script['path'])
            
        
    def index(self, request=None):
        filename = os.path.join(os.path.dirname(__file__), 'templates', 'index.mustache')
        txt = codecs.open(filename, 'r', encoding='utf-8').read()
        return dric.Response(pystache.render(txt, {'content_scripts': self.__content_scripts}))
    index.event = "index"
        

dric.register(__name__, IndexProvider())