"""
Provide server's LAN ip on endpoint /ip.
"""

import dric
import dric.support
dric.register(__name__, dric.support.ContentScriptInjector([{"path":"/js/dricnetwork_box.js"}]))