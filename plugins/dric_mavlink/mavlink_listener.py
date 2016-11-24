import dric
import dric.support
import dric.support.accept
import dric.aq

from eventlet import sleep
from struct import pack
from time import time
from string import upper
from json import dumps
from ast import literal_eval
from werkzeug.exceptions import NotFound

from lxml import etree as ET

from CodernityDB.database import Database, RecordNotFound
from CodernityDB.hash_index import HashIndex

from shutil import rmtree
from os.path import join, exists

from hashlib import md5
from logging import getLogger
from time import time
from json import dumps, loads

from .filtering import mavlink_filtering, FilterableMessage
from .rangequery import RangeQuery

import StringIO

_logger = getLogger('dric.mavlink')

class MavlinkIndex(HashIndex):

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '16s'
        super(MavlinkIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        return self.make_key(data), dict(message=data.get('message'), timestamp=data.get('timestamp'))

    def make_key(self, key):
        k = "{}.{}.{}".format(key.get('name'), key.get('esid'), key.get('n'))
        m = md5()
        m.update(k)
        return m.digest()

class MavlinkListener(dric.Plugin):


    def __init__(self):
        self.timeref = 0
        self.messages_count = {}
        self.messages_stats = {}
        self.messages = {}
        self.db = None
        self.message_datasources = {}
        self.esids = []
        self.esid_aq = dric.aq.AQ(self.aq_esid_list)

    def setup(self, eventbus):
        dbpath = join('data', 'mavlink', 'database')
        if exists(dbpath):
            rmtree(dbpath)
        self.db = Database(dbpath)
        self.db.create()
        key_ind = MavlinkIndex(self.db.path, 'key')
        self.db.add_index(key_ind)
        self.bus = eventbus

        self.timeref = time()

    @dric.on('MAVLINK')
    def mavlink_message_received(self, name, esid, message):
        # add esid
        if esid not in self.esids:
            self.esids.append(esid)
            self.messages_count[esid] = 0
            self.messages_stats[esid] = {}
            self.esid_aq.update_all()

            datasource = MavlinkMessageStatsDatasource(self.messages_stats[esid])
            source_name = "mavlink/messages_stats${}".format(esid)
            dric.add_datasource(source_name, datasource)

            datasource = MavlinkMessageCountDatasource(self.messages_count, esid)
            source_name = "mavlink/messages_count${}".format(esid)
            dric.add_datasource(source_name, datasource)

            datasource = MavlinkMessageCountPerSecondDatasource(self.messages_count, esid)
            source_name = "mavlink/messages_count_per_second${}".format(esid)
            dric.add_datasource(source_name, datasource)
        


        # statistics
        self.messages_count[esid] += 1
        if name not in self.messages_stats[esid]:
            self.messages_stats[esid][name] = 0
        self.messages_stats[esid][name] += 1
        
        # add message to database
        i = self.messages_stats[esid][name]
        
        filterable_message = mavlink_filtering.filter(FilterableMessage(name, i, message))
        name = filterable_message.name
        i = filterable_message.i
        message = filterable_message.message
        self.db.insert(dict(name=name, n=i, esid=esid, message=dumps(message), timestamp=(time() - self.timeref)))

        if name not in self.message_datasources:
            self.message_datasources[name] = {}
        message_datasource_dict = self.message_datasources[name]
        for parameter in message:
            if parameter not in message_datasource_dict:
                # check if parameter is plotable (float)
                noplot = False
                try:
                    float(message[parameter])
                except:
                    noplot = True
                datasource = MavlinkMessageDatasource(0.5, noplot)
                message_datasource_dict[parameter] = datasource
                source_name = "mavlink-{}/{}${}".format(name, parameter, esid)
                
                dric.add_datasource(source_name, datasource)
            message_datasource_dict[parameter].push(message[parameter])
        
        #dispatch event
        event_name = 'MAVLINK/{}'.format(name)
        self.bus.publish(event_name.upper, id=esid, message=message)

    @dric.route('mavlink_message', '/mavlink/message/<esid>/<name>/<int:n>')
    def get_mavlink_message(self, esid, name, n, request=None):
        try:
            return dric.Response(self.db.get('key', dict(name=name, n=n, esid=esid))['message'])
        except KeyError:
            raise NotFound()

    @dric.route('mavlink_download_range', '/mavlink/download/<esid>/<name>/<key>/<query>')
    def download_mavlink_log_range(self, esid, name, key, query, request=None):
        output = StringIO.StringIO()
        for i in RangeQuery(query):
            try:
                record = self.db.get('key', dict(name=name, n=i, esid=esid))
                message_as_dict = loads(record['message'])
                output.write(str(record['timestamp']))
                output.write(" ")
                output.write(str(message_as_dict[key]))
                output.write('\n');
            except RecordNotFound:
                pass
        return dric.Response(output.getvalue(), content_type="plain/txt")

    @dric.route('mavlink_download', '/mavlink/download/<esid>/<name>/<key>')
    def download_mavlink_log(self, esid, name, key, request=None):
        output = StringIO.StringIO()
        try:
            i = 0
            while True:
                i = i + 1
                record = self.db.get('key', dict(name=name, esid=esid, n=i))
                message_as_dict = loads(record['message'])
                output.write(str(record['timestamp']))
                output.write(" ")
                output.write(str(message_as_dict[key]))
                output.write('\n');
        except RecordNotFound:
            pass
        return dric.Response(output.getvalue(), content_type="plain/txt")
        
    @dric.route('mavlink_esid', '/mavlink/esid')
    def get_esid_list(self, request):
        if dric.support.accept.xml_over_json(request):
            root = ET.Element('systems')
            root.set('version', '1')
            for esid in self.esids:
                esid_el = ET.SubElement(root, 'systemid')
                esid_el.text = esid
            return dric.XMLResponse(root)
        elif dric.support.accept.json_over_xml(request):
            return dric.JSONResponse(self.esids)
        else:
            raise dric.exceptions.NotAcceptable('xml or json')

    @dric.websocket('mavlink_esid_ws', '/mavlink/esid/ws', ['AQ'])
    def ws_esid_list(self, ws, request):
        self.esid_aq.incoming(ws)

    def aq_esid_list(self):
        return unicode(dumps(self.esids))

    #@dric.datasource('mavlink/messages_count')
    #def message_count(self):
    #    while True:
    #        yield self.messages_count
    #        sleep(1)
    #message_count.isTimeSerie = True

    #@dric.datasource('mavlink/messages_count_per_second')
    #def message_count_fq(self):
    #    old = 0
    #    while True:
    #        yield self.messages_count - old
    #        old = self.messages_count
    #        sleep(1)
    #message_count_fq.isTimeSerie = True

    #@dric.support.datasource.noplot(True)
    #@dric.datasource('mavlink/messages_stats')
    #def message_stats(self):
    #    while True:
    #        json_text = (dumps(self.messages_stats, separators=(',',':')))
    #        yield pack('!d', time()) + json_text
    #        sleep(1)

class MavlinkMessageCountPerSecondDatasource(object):
    def __init__(self, messages_count, esid, sleep=1, noplot=False):
        self.sleep = sleep
        self.esid = esid
        self.noplot = noplot
        self.messages_count = messages_count
        self.isTimeSerie = True

    def __call__(self):
        old = 0
        while True:
            yield self.messages_count[self.esid] - old
            old = self.messages_count[self.esid]
            sleep(1)

class MavlinkMessageCountDatasource(object):
    def __init__(self, messages_count, esid, sleep=1, noplot=False):
        self.sleep = sleep
        self.esid = esid
        self.noplot = noplot
        self.messages_count = messages_count
        self.isTimeSerie = True

    def __call__(self):      
        while True:
            yield self.messages_count[self.esid]
            sleep(1)

class MavlinkMessageStatsDatasource(object):
    def __init__(self, messages_stats, sleep=1, noplot=True):
        self.sleep = sleep
        self.noplot = noplot
        self.messages_stats = messages_stats

    def __call__(self):      
        while True:
            json_text = (dumps(self.messages_stats, separators=(',',':')))
            yield pack('!d', time()) + json_text
            sleep(self.sleep)

class MavlinkMessageDatasource(object):

    def __init__(self, sleep=1, noplot=False):
        self.sleep = sleep
        self.queues = {}
        self.sleep = 1
        self.noplot = noplot
        self.withcontext = True

    def push(self, value):
        for cid in self.queues:
            queue = self.queues[cid]
            queue.append((time(), value))

    def __call__(self, context):
        queue = []
        self.queues[context['cid']] = queue
        
        while True:
            while len(queue) > 0:
                try:
                    popped = queue.pop(0)
                    yield pack('!dd', popped[0] - context['start'], popped[1])
                except (ValueError, TypeError) as e:
                    _logger.exception('Expected double. %s %s given.', type(popped[1]), popped[1], exc_info=e)
            sleep(self.sleep)

dric.register('MAVLINK/listener', MavlinkListener())