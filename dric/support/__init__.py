from ._contentscripts import ContentScriptInjector, inject_content_script, route, event_listener
from ._configuration import Configurable, ConfigurePass

from dric import get_pass_manager

get_pass_manager().add_pass(ConfigurePass())