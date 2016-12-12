import struct
import sys
import time
import dric
import os
from os.path import join
import math
import binascii
import traceback

PACKET_SIZE = 18

class MavlinkRawDBPlugin(dric.Plugin):
    def __init__(self, *args, **kwargs):
        # remove all .index and .raw files
        self.channels_rootdir = join('data', 'mavlink', 'channels')
        [ os.remove(join(self.channels_rootdir, f)) for f in os.listdir(self.channels_rootdir) if f.endswith('.index') or f.endswith('.raw') ]
        self.__channels = {}
        self.__mavlinks = {}

    @dric.route('mavlink_download_message_timestamp', '/mavlink/downloadt/<name>')
    def mavlink_download_message_timestamp(self, name, request):
        esids = request.args.getlist('esid')
        params = request.args.getlist('param')
        range_from = request.args.get('from', 0, type=float)
        range_to = request.args.get('to', float('inf'), type=float)

        output = '% MAVLINK: {}\n'.format(name)
        for channel_name in [esid.split('-')[0] for esid in esids if esid.split('-')[0] in self.__channels]:
            output += '% Connection: {}\n'.format(channel_name)
            output += '%timestamp systemId '
            output += ' '.join(params)
            output += '\n'
            channel = self.__channels[channel_name]
            # go to end of file
            fi = channel.index
            fr = channel.raw
            fi.seek(-PACKET_SIZE, os.SEEK_END)
            packet_count = fi.tell() / PACKET_SIZE
            print('{} packets'.format(packet_count))

            # search for from_range
            m = self.find_start_packet(fi, packet_count, range_from)
            fi.seek(m * PACKET_SIZE)
            timestamp = range_from
            mavlink = channel.mavlink(None)
            while timestamp < range_to:
                try:
                    try:
                        timestamp, offset, length = struct.unpack('!dQh', fi.read(PACKET_SIZE))
                    except:
                        traceback.print_exc()
                        break
                    # print('{}: @{} len{}'.format(timestamp, offset, length))
                    fr.seek(offset)
                    data = fr.read(length)

                    messages = mavlink.parse_buffer(data)
                    # print(messages)
                    if messages is not None:
                        for message in messages:
                            message_esid = "{}-{}".format(channel_name, message.get_srcSystem())
                            if message_esid not in esids:
                                continue
                            if message.get_type() != name:
                                continue
                            output += str(timestamp)
                            output += ' '
                            output += str(message.get_srcSystem())
                            for param in params:
                                output += ' '
                                output += str(message.to_dict()[param])
                            output += '\n'

                except:
                    traceback.print_exc()
        return dric.Response(str(output), content_type="text/plain")

    @dric.route('mavlink_time', '/mavlink/time')
    def get_time(self, request):
        return dric.Response(str(self.time()))

    @dric.route('mavlink_message_timestamp', '/mavlink/messaget/<esid>/<name>/')
    def get_message(self, esid, name, request):
        try:
            range_from = request.args.get('from', 0, type=float)
            range_to = request.args.get('to', float('inf'), type=float)
            if range_from > range_to:
                raise dric.exceptions.BadRequest('from cannot be smaller than to')
            try:
                channel_name, system_id = esid.split('-')
            except ValueError:
                raise dric.exceptions.BadRequest('Malformed esid')
            if channel_name not in self.__channels:
                raise dric.exceptions.NotFound('Channel {} not found'.format(channel_name))
            channel = self.__channels[channel_name]
            fi = channel.index
            fr = channel.raw

            # go to end of file
            fi.seek(-PACKET_SIZE, os.SEEK_END)
            packet_count = fi.tell() / PACKET_SIZE
            print('{} packets'.format(packet_count))

            # read timestamp
            end_timestamp, = struct.unpack('!d', fi.read(8))
            if end_timestamp < range_from:
                raise dric.exceptions.NotFound('From is in the future')

            # search for from_range
            m = self.find_start_packet(fi, packet_count, range_from)
            fi.seek(m * PACKET_SIZE)
            timestamp = range_from
            mavlink = channel.mavlink(None)
            output = []
            while timestamp < range_to:
                try:
                    try:
                        timestamp, offset, length = struct.unpack('!dQh', fi.read(PACKET_SIZE))
                    except:
                        traceback.print_exc()
                        break
                    # print('{}: @{} len{}'.format(timestamp, offset, length))
                    fr.seek(offset)
                    data = fr.read(length)

                    # print(binascii.hexlify(data))

                    messages = mavlink.parse_buffer(data)
                    print(messages)
                    if messages is not None:
                        for message in messages:
                            message_esid = "{}-{}".format(channel_name, message.get_srcSystem())
                            if esid != message_esid:
                                continue
                            #if esid not in self.connection['systems']:
                            #    self.connection['systems'].append(esid)
                            #    self.update_driconxwsockets()
                            output.append({ 
                                'timestamp': timestamp, 
                                'esid': esid,
                                'type': message.get_type(),
                                'message': message.to_dict() 
                            })
                            # dric.bus.publish('MAVLINK', message.get_type(), esid, message.to_dict())

                except Exception as e:
                    traceback.print_exc()
            
            return dric.JSONResponse(output)
        except Exception as e:
            print(e)
            raise e
        raise dric.exceptions.InternalServerError()

    def find_start_packet(self, cf, packet_count, range_from):
        L = 0
        R = packet_count - 1
        timestamp = 0
        m = 0
        while abs(R - L) > 1 and L < R:
            m = math.floor((R + L) / 2)
            cf.seek(m * PACKET_SIZE)
            # read timestamp
            timestamp = struct.unpack('!d', cf.read(8))[0]
            # print('{} -> {} ({}, {}) {}'.format(timestamp, range_from, L, R,
            # timestamp > range_from))
            if timestamp < range_from:
                L = m + 1
            elif timestamp > range_from:
                R = m - 1        
        return m

    @dric.on('MAVLINK_RAW')
    def save_raw(self, channel_name, data, mavlink):
        try:
            if channel_name not in self.__channels:
                self.open_channel(channel_name, mavlink)
            channel = self.__channels[channel_name]
            
            channel.raw.write(data)
            channel.index.write(struct.pack('!dQh', self.time(), channel.raw.tell() - len(data), len(data)))
        except Exception as e:
            print(e)

    def open_channel(self, channel_name, mavlink):
        if channel_name in self.__channels:
            return
        dbpath = join(self.channels_rootdir, channel_name)
        file_raw = open(dbpath + '.raw', 'a+b', 0)
        file_index = open(dbpath + '.index', 'a+b', 0)
        self.__channels[channel_name] = Channel(file_raw, file_index, type(mavlink))
        
        
    def time(self):
        if sys.platform == "win32":
            mytime = time.clock()
        else:
            mytime = time.time()
        return mytime



dric.register(__name__, MavlinkRawDBPlugin())

class Channel(object):
    def __init__(self, file_raw, file_index, mavlink):
        self.raw = file_raw
        self.index = file_index
        self.mavlink = mavlink