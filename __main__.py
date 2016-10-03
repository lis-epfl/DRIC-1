import dric


dric.load_plugins()
dric.start_plugins()
dric.Server('0.0.0.0', 8080).start()