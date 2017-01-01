import dric
from eventlet import sleep
import json
import time

class ParapIncomingQueue(object):
    def __init__(self):
        self.running = False
        self.running_ids = 0
        self.ws = None
        self.esid = None
        self.param_count = 0
        self.one_shot = True

    def wait(self, ws, esid):
        """ Return False if timeout """
        tic = time.time()
        while self.running is not False: 
            if time.time() > tic + 30:  # 30s security timeout
                self.running = False
                ws.close()
                return False
            sleep(1)

        self.ws = ws
        self.esid = esid
        self.param_count = 0
        return True

    def wait_for_termination(self):
        self.running_ids = self.running_ids + 1 if self.running_ids < 10000 else 0
        my_running_id = self.running_ids
        self.running = my_running_id
        tic = time.time()
        while self.running == my_running_id: 
            if time.time() > tic + 30:  # 30s timeout
                self.ws.send(unicode('4:{}'))
                self.clean()
                return
            sleep(1)    # and wait
        self.clean()

    def clean(self):
        self.running = False
        self.param_count = 0
        self.esid = None
        self.ws.close()
        self.ws = None

class ParamProtocolPlugin(dric.Plugin):
    """ The PARAM_REQUEST_LIST plugin """
    def __init__(self, *args, **kwargs):
        self.piq = ParapIncomingQueue()

    @dric.on('MAVLINK')
    def param_value(self, esid, mav_message):
        name = mav_message.get_type()
        message = mav_message.to_dict()
        if name != 'PARAM_VALUE': return
        if esid != self.piq.esid: return
        if self.piq.ws is None: return

        message['srcSystem'] = mav_message.get_srcSystem()
        message['srcComponent'] = mav_message.get_srcComponent()

        # check end of param list
        self.piq.param_count = self.piq.param_count + 1
        status = 2 if self.piq.param_count < message['param_count'] and not self.piq.one_shot else 3
        
        self.piq.ws.send(unicode('{}:{}'.format(status, json.dumps(message))))

        # close connection
        if status == 3:
            self.piq.clean()

    @dric.websocket('parameter_request_read', '/mavlink/<esid>/parameters/<int:index>', ['ParaP'])
    def param_request_read(self, ws, esid, index, request):
        # wait for my turn
        if self.piq.wait(ws, esid) is False: return
        
        # action
        try:
            _, target_system = esid.split('-')
            target_system_id = int(target_system)
        except:
            raise dric.exceptions.BadRequest('Cannot extract target system from esid "{}".'.format(esid))

        try:
            index_int = int(index)
        except:
            raise dric.exceptions.BadRequest('Cannot extract index from "{}".'.format(index))

        fields = {
            'target_system': target_system_id,
            'target_component': 0,
            'param_id': '',
            'param_index': index_int
        }

        self.piq.one_shot = True
        dric.bus.publish('SEND_MAVLINK', esid, 'PARAM_REQUEST_READ', fields)
        ws.send(unicode('1:{}'))

        # wait for action termination
        self.piq.wait_for_termination()

    @dric.websocket('parameter_set', '/mavlink/<esid>/parameter/<string:paramid>', ['ParaP'])
    def param_set(self, ws, esid, paramid, request):
        # wait for my turn
        if self.piq.wait(ws, esid) is False: return
        
        # action
        try:
            _, target_system = esid.split('-')
            target_system_id = int(target_system)
        except:
            raise dric.exceptions.BadRequest('Cannot extract target system from esid "{}".'.format(esid))

        try: value = request.args.get('value', default=None, type=float)
        except: raise dric.exceptions.BadRequest('Wrong format for value: "{}". Expected float.'.format(index))
        if value is None: raise dric.exceptions.BadRequest('Parameter "value" required.')

        try: ptype = request.args.get('type', default=None, type=int)
        except: raise dric.exceptions.BadRequest('Wrong format for type: "{}". Expected int.'.format(index))
        if ptype is None: raise dric.exceptions.BadRequest('Parameter "type" required.')
        if ptype not in range(1,9+1): raise dric.exceptions.BadRequest('Parameter "type" must be in range [1,9].')

        try: tcomp = request.args.get('component', default=None, type=int)
        except: raise dric.exceptions.BadRequest('Wrong format for component: "{}". Expected int.'.format(index))
        if tcomp is None: raise dric.exceptions.BadRequest('Parameter "component" required.')

        fields = {
            'target_system': target_system_id,
            'target_component': tcomp,
            'param_id': str(paramid),
            'param_value': value,
            'param_type': ptype
        }

        print(str(paramid))

        self.piq.one_shot = True
        dric.bus.publish('SEND_MAVLINK', esid, 'PARAM_SET', fields)
        ws.send(unicode('1:{}'))

        # wait for action termination
        self.piq.wait_for_termination()


    @dric.websocket('parameters_request_list', '/mavlink/<esid>/parameters', ['ParaP'])
    def param_request_list(self, ws, esid, request):
        """
        The 'ParaP' subprotocol is a text based subprotocol. 
        Only the server may send messages. 
        Data are json formatted, prefixed with a status code followed by a colon ':'.
        If a PARAM_REQUEST_LIST has already been issued and the target system is still emitting PARAM_VALUE messages, 
        the client will be queued.
        When the PARAM_REQUEST_LIST message is emitted, the server send this message: "1:{}" (1 is the ok status code, {} is an empty json)
        When a PARAM_VALUE message is received, the server will send a JSON message. See https://pixhawk.ethz.ch/mavlink/#PARAM_VALUE for content of the message.
        In addition, the PARAM_VALUE will also contains two more fields: srcSystem and srcComponent.

        Status codes:
            1: Request message sent
            2: PARAM_VALUE message received
            3: last PARAM_VALUE message received, server will close the connection, and client should close the connection
            4: timeout
        """
        # Wait for end of previous connection.
        # We are asynchronous, so we do not need to worry about thread-safety here
        if self.piq.wait(ws, esid) is False: return

        # start the action
        try:
            _, target_system = esid.split('-')
            target_system_id = int(target_system)
        except:
            raise dric.exceptions.BadRequest('Cannot extract target system from esid "{}".'.format(esid))

        fields = {
            'target_system': target_system_id,
            'target_component': 0
        }
        
        self.piq.one_shot = False

        dric.bus.publish('SEND_MAVLINK', esid, 'PARAM_REQUEST_LIST', fields)
        ws.send(unicode('1:{}'))

        # wait for action to be terminated
        self.piq.wait_for_termination()

dric.register(__name__, ParamProtocolPlugin())