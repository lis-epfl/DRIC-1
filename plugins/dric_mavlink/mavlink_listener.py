import dric, dric.support
from eventlet import sleep
from struct import pack
from time import time
from string import upper
from json import dumps
from werkzeug.exceptions import NotFound

from CodernityDB.database import Database
from CodernityDB.hash_index import HashIndex

from shutil import rmtree
from os.path import join, exists

from hashlib import md5

class MavlinkIndex(HashIndex):

    def __init__(self, *args, **kwargs):
        kwargs['key_format'] = '16s'
        super(MavlinkIndex, self).__init__(*args, **kwargs)

    def make_key_value(self, data):
        key = str(data.get('name')) + '.' + str(data.get('n'))
        m = md5()
        m.update(key)
        return m.digest(), dict(message=data.get('message'))

    def make_key(self, key):
        k = str(key.get('name')) + '.' + str(key.get('n'))
        m = md5()
        m.update(k)
        return m.digest()

class MavlinkListener(dric.Plugin):

    messages_count = 0
    messages_stats = {}
    messages = {}
    db = None

    def setup(self, eventbus):
        dbpath = join('data', 'mavlink', 'database')
        if exists(dbpath):
            rmtree(dbpath)
        self.db = Database(dbpath)
        self.db.create()
        key_ind = MavlinkIndex(self.db.path, 'key')
        self.db.add_index(key_ind)

    @dric.on('MAVLINK')
    def mavlink_message_received(self, name, id, message):
        # statistics 
        self.messages_count += 1
        if name not in self.messages_stats:
            self.messages_stats[name] = 0
        self.messages_stats[name] += 1
        
        # add message to database
        i = self.messages_stats[name]
        self.db.insert(dict(name=name, n=i, message=str(message)[len(name):]))

        # keep messages in memory
        #try:
        #    if name not in self.messages:
        #        self.messages[name] = {}
        #    self.messages[name][i] = message
        #except Exception as e:
        #    print (e)

    @dric.route('mavlink_message', '/mavlink/message/<name>/<int:n>')
    def get_mavlink_message(self, name, n, request=None):
        try:
            return dric.Response(self.db.get('key', dict(name=name, n=n))['message'])
        except KeyError:
            raise NotFound()

    @dric.datasource('mavlink/messages_count')
    def message_count(self):
        while True:
            yield self.messages_count
            sleep(1)
    message_count.isTimeSerie = True

    @dric.datasource('mavlink/messages_count_per_second')
    def message_count_fq(self):
        old = 0
        while True:
            yield self.messages_count - old
            old = self.messages_count
            sleep(1)
    message_count_fq.isTimeSerie = True

    @dric.datasource('mavlink/messages_stats')
    def message_stats(self):
        while True:
            json_text = (dumps(self.messages_stats, separators=(',',':')));
            yield pack('!d', time()) + json_text
            sleep(1)

    


dric.register('MAVLINK/listener', MavlinkListener())