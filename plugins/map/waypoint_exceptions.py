import json

class CannotParseMessageWsError(object):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return json.dumps({
            'error': 'Cannot parse json message: "{}".'.format(self.msg),
            'message': self.msg,
            'status': 1
        })

class MissingParameterWsError(object):
    def __init__(self, param, msg):
        self.msg = msg
        self.param  = param
    def __str__(self):
        return json.dumps({
            'error': 'Parameter {} is missing in message: "{}".'.format(self.param, self.msg),
            'message': self.msg,
            'param': self.param,
            'status': 2
        })

class NoStateTransitionErrorWsError(object):
    def __init__(self, msg, source):
        self.source = source
        self.msg = msg
    def __str__(self):
        return json.dumps({
            'error': self.source.message,
            'message': self.msg,
            'state': self.source.state.name,
            'event': str(self.source.event),
            'status': 3
        })

class StateInitializationErrorWsError(object):
    def __init__(self, msg, source):
        self.source = source
        self.msg = msg
    def __str__(self):
        return json.dumps({
            'error': self.source.message,
            'message': self.msg,
            'state': self.source.state.name,
            'status': 4
        })

class NoStateTransitionError(Exception):
    def __init__(self, state, event):
        message = 'No transition from state {} for event {}.'.format(state.name, event)
        self.state = state
        self.event = event
        super(NoStateTransitionError, self).__init__(message)

class StateInitializationError(Exception):
    def __init__(self, state, msg):
        message = 'Error in initilization of state {}: {}'.format(state.name, msg)
        self.state = state
        self.message = msg
        super(StateInitializationError, self).__init__(message)
