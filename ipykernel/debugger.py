import logging
from traitlets import Instance

class Debugger:

    # Requests that requires that the debugger has started
    started_debug_msg_types = [
        'dumpCell', 'setBreakpoints',
        'source', 'stackTrace',
        'variables', 'attach',
        'configurationDone'
    ]
    
    # Requests that can be handled even if the debugger is not running
    static_debug_msg_types = [
        'debugInfo', 'inspectVariables'
    ]

    log = Instance(logging.Logger, allow_none=True)

    def __init__(self):
        self.is_started = False

        self.header = ''
        
        self.started_debug_handlers = {}
        for msg_type in started_debug_msg_types:
            self.started_debug_handlers[msg_type] = getattr(self, msg_type)

        self.static_debug_handlers = {}
        for msg_type in static_debug_msg_types:
            self.static_debug_handlers[msg_type] = getattr(self, msg_type)

        self.breakpoint_list = {}
        self.stopped_threads = []

    def start(self):
        return False

    def stop(self):
        pass

    def dumpCell(self, message):
        return {}

    def setBreakpoints(self, message):
        return {}

    def source(self, message):
        return {}

    def stackTrace(self, message):
        return {}

    def variables(self, message):
        return {}

    def attach(self, message):
        return {}

    def configurationDone(self, message):
        return {}

    def debugInfo(self, message):
        reply = {
            {'type', 'response'},
            {'request_seq', message['seq']},
            {'success', True},
            {'command', message['command']},
            {'body', {
                {'isStarted', self.is_started},
                {'hashMethod', 'Murmur2'},
                {"hashSeed", 0},
                {"tmpFilePrefix", 'coincoin'},
                {"tmpFileSuffix", '.py'},
                {"breakpoints", self.breakpoint_list},
                {"stoppedThreads", self.stopped_threads}
            }}
        }
        return reply

    def inspectVariables(self, message):
        return {}

    def forward_message(self, message):
        return {}

    def process_request(self, header, message):
        reply = {}

        if message['command'] == 'initialize':
            if self.is_started:
                self.log.info('The debugger has already started')
            else:
                self.is_started = self.start()
                if self.is_started:
                    self.log.info('The debugger has started')
                else:
                    reply = {
                        {'command', 'initialize'},
                        {'request_seq', message['seq']},
                        {'seq', 3},
                        {'success', False},
                        {'type', 'response'}
                    }

        handler = self.static_debug_handlers.get(message['command'], None)
        if handler is not None:
            reply = handler(message)
        elif self.is_started:
            self.header = header
            handler = self.started_debug_handlers.get(message['command'], None)
            if handler is not None:
                reply = handler(message)
            else
                reply = self.forward_message(message)

        if message['command'] == 'disconnect':
            self.stop()
            self.breakpoint_list = {}
            self.stopped_threads = []
            self.is_started = False
            self.log.info('The debugger has stopped')

        return reply

