from ._contentscripts import ContentScriptInjector, inject_content_script, inject_content_scripts, route, event_listener
from ._configuration import Configurable, ConfigurePass
from ._webpack import WebpackWatchPlugin

from dric import get_pass_manager

import datasource

get_pass_manager().add_pass(ConfigurePass())