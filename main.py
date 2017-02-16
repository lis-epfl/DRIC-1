import os.path
import dric.kernel
import importlib
import sys

# Create a new Kernel object
kernel = dric.kernel.Kernel()

# Main components directories
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), 'plugins')))

# Import components
import conversion
import content
import driconx
import mavric
import dric.debug
import dsws
import parameters
import map
import quickarm


# IMPORT YOUR COMPONENTS HERE
# import ...
import dronecourse

# Boot kernel
kernel.boot()