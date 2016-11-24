import dric

from .filtering import mavlink_filter

from logging import getLogger
from os.path import join, abspath, dirname
import xml.etree.ElementTree as ET

_logger = getLogger('dric.mavlink.unitconversion')

@dric.support.Configurable('units-conversion.config.yml')
@dric.support.Configurable('units-conversion.config.ini')
class ConversionPlugin(dric.Plugin):

    def __init__(self, *args, **kwargs):
        self.enabled_conversions = {}

    def configure(self, filter_configuration_file):
        filter_configuration = filter_configuration_file.configuration
        # process enabled conversion
        for name in filter_configuration:
            for key in filter_configuration[name]:
                filter_configuration[name][key] = filter_configuration[name][key].split()
        
        self.enabled_conversions = filter_configuration


    @mavlink_filter
    def convert(self, filtering_message):
        if filtering_message.name not in self.enabled_conversions:
            return filtering_message

        conversions = self.enabled_conversions[filtering_message.name]

        for key in filtering_message.message:
            if key in conversions:
                if key in filtering_message.message:
                    converted = dric.bus.publish('convert', conversions[key][0], conversions[key][1], filtering_message.message[key])
                    if converted is not None and len(converted) > 0:
                        filtering_message.message[key] = converted[0]
        return filtering_message

    @dric.route('mavlink.units', '/mavlink/units')
    def get_units(self, request):
        accept = request.accept_mimetypes.best_match(['application/xml', 'text/xml', 'application/json'])
        if accept == 'application/xml' or accept == 'text/xml':
            root = ET.Element('types')
            for name in self.enabled_conversions:
                messagetype = ET.SubElement(root, 'type')
                messagetype.set('name', name)
                conversions = self.enabled_conversions[name]
                for key in conversions:
                    elemkey = ET.SubElement(messagetype, 'key', {'name': key})
                    elemkey.text = str(conversions[key][1])
            return dric.Response(ET.tostring(root, encoding='UTF-8'), content_type=accept)
        else:
            root = {}
            for name in self.enabled_conversions:
                root[name] = {}
                conversions = self.enabled_conversions[name]
                for key in conversions:
                    root[name][key] = str(conversions[key][1])
            return dric.JSONResponse(root)

dric.register(__name__, ConversionPlugin())