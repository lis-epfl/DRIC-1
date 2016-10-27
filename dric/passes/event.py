import dric

class EventPass(dric.Pass):
    """Add subscriber to the bus. 
    
Use `@dric.event('myevent')` to subscribe a plugin's
method to the corresponding bus' event. 
    
    """
    def load(self, plugin, name):
        # Iterate over all class attributes
        for method_name in dir(plugin):
            method = getattr(plugin, method_name)
            if callable(method):    # only methods
                if hasattr(method, 'event'):
                    event = getattr(method, 'event')
                    dric.bus.subscribe(event, method)
                    if hasattr(method, 'route'):
                        route = getattr(method, 'route')
                        dric.router.add(route, event)