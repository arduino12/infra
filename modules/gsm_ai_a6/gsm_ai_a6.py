
import time
import logging
from gsm.at_protocol import ATProtocol
from gsm.pdu import decodeSmsPdu


class A6Gsm(ATProtocol):
    """

    """
    CALL_RING_TIME = 3

    def __init__(self):
        ATProtocol.__init__(self)
        self._events_handlers = {
            '0791': self._handle_sms,
            '+CMT:': self._handle_idle,
            '+CIEV:': self._handle_idle,
            'RING': self._handle_call,
            'NO ANSWER': self._handle_idle,
            'ERROR': self._handle_idle,
            'connection_made': self._connection_made,
        }
        self._last_sms_concatenation = -1, {}
        self._last_call_time = 0
        self.handle_sms = None
        self.handle_call = None

    def connection_made(self, transport):
        ATProtocol.connection_made(self, transport)
        self.events.put('connection_made_0')

    def _connection_made(self, index):
        time.sleep(0.5)
        index = int(index.split('_')[-1])
        if index == 0:
            self.send_command('ATE0')
        else:
            self.send_command('AT+CMGF=0')
            return
        self.events.put('connection_made_%s' % (index + 1))

    def _handle_event(self, event):
        for event_start in self._events_handlers:
            if event.startswith(event_start):
                return self._events_handlers[event_start](event)
        logging.warning('unhandled event: {!r}'.format(event))

    def dummy(self):
        self.send_command('AT')

    def get_cpms(self):
        return self.send_command('AT+CPMS=?')

    def _handle_sms(self, event):
        if self.handle_sms is not None:
            sms = decodeSmsPdu(bytes(event, 'latin-1'))
            text = sms['text']
            send_time = sms['time']
            number = sms['number']
            
            if 'udh' in sms:
                udh = sms['udh'][0]
                if self._last_sms_concatenation[0] == udh.reference:
                    if udh.number < udh.parts:
                        self._last_sms_concatenation[1][udh.number] = text
                    elif len(self._last_sms_concatenation[1]) == udh.parts - 1:
                        for i in range(udh.parts - 1, 0, -1):
                            text = self._last_sms_concatenation[1][i] + text
                        self.handle_sms(number, send_time, text)
                    else:
                        self._last_sms_concatenation = -1, {}
                elif udh.number == 1:
                    self._last_sms_concatenation = udh.reference, {udh.number: text}
                else:
                    self._last_sms_concatenation = -1, {}
            else:
                self.handle_sms(number, send_time, text)

    def _handle_call(self, event):
        if self.handle_call is not None:
            cur_time = time.time()
            if (cur_time - self._last_call_time) > self.CALL_RING_TIME:
                self.handle_call()
            self._last_call_time = cur_time

    def _handle_idle(self, *args):
        pass
