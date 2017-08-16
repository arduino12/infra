import time

from infra.old_modules.gsm.at_protocol import ATProtocol
from infra.old_modules.gsm.pdu import decodeSmsPdu


class A6Gsm(ATProtocol):
    """

    """
    CALL_RING_TIME = 3

    def __init__(self):
        ATProtocol.__init__(self)
        self._events_handlers = {
            '0791': self._sms_recived,
            '+CME ': self._handle_idle,
            '+CMT:': self._handle_idle,
            '+CIEV:': self._handle_idle,
            'RING': self._call_recived,
            'NO ANSWER': self._handle_idle,
            'ERROR': self._handle_idle,
            'connection_made': self._connection_made,
        }
        self._last_sms_concatenation = -1, {}
        self._last_call_time = 0
        self.status = 'DISCONNECTED'
        self.status_changed = lambda: None
        self.sms_recived = lambda number, send_time, text: None
        self.call_recived = lambda: None

    def connection_made(self, transport):
        ATProtocol.connection_made(self, transport)
        self.status = 'CONNECTED'
        self.status_changed()
        self.events.put('connection_made_0')

    def _connection_made(self, index):
        time.sleep(0.5)
        index = int(index.split('_')[-1])
        try:
            if index == 0:
                self.send_command('ATE0')
            elif index == 1:
                self.send_command('AT+CMGF=0')
            elif index == 2:
                self.status = 'ALIVE'
                self.status_changed()
                return
        except TimeoutError:
            self.status = 'TIMEOUT'
            self.status_changed()
        else:
            self.events.put('connection_made_%s' % (index + 1))

    def _handle_event(self, event):
        ATProtocol._handle_event(self, event)
        for event_start in self._events_handlers:
            if event.startswith(event_start):
                return self._events_handlers[event_start](event)
        
        self._logger.warning('unhandled event: %s', event)

    def dummy(self):
        self.send_command('AT')
    
    def get_sim_number(self):
        cnum = self.send_command('AT+CNUM')
        try:
            return cnum[0].split('"')[3]
        except:
            self._logger.error('empty CNUM, use self.set_sim_number first time before calling get_sim_number')
            return '0'
    
    def set_sim_number(self, number):
        self.send_command('AT+CUSD=1')
        self.send_command('AT+CPBS="ON"')
        self.send_command('AT+CPBR=1')
        self.send_command('AT+CPBW=1,"{}",129,"CNUM"'.format(number))

    def get_cpms(self):
        return self.send_command('AT+CPMS=?')

    def normalize_phone_number(self, number):
        return number.replace('+972', '0')

    def _sms_recived(self, event):
        sms = decodeSmsPdu(bytes(event, 'latin-1'))
        text = sms['text']
        send_time = sms['time']
        number = sms['number']
        self._logger.debug('_sms_recived: %s %s\n%s', number, send_time, text)
        
        if 'udh' in sms:
            udh = sms['udh'][0]
            self._logger.debug('_sms_recived: udh: %s %s %s', udh.reference, udh.number, udh.parts)
            if self._last_sms_concatenation[0] == udh.reference:
                if udh.number < udh.parts:
                    self._last_sms_concatenation[1][udh.number] = text
                elif len(self._last_sms_concatenation[1]) == udh.parts - 1:
                    for i in range(udh.parts - 1, 0, -1):
                        text = self._last_sms_concatenation[1][i] + text
                    self.sms_recived(number, send_time, text)
                else:
                    self._last_sms_concatenation = -1, {}
            elif udh.number == 1:
                self._last_sms_concatenation = udh.reference, {udh.number: text}
            else:
                self._last_sms_concatenation = -1, {}
        else:
            self.sms_recived(number, send_time, text)

    def _call_recived(self, event):
        cur_time = time.time()
        if (cur_time - self._last_call_time) > self.CALL_RING_TIME:
            self.call_recived()
        self._last_call_time = cur_time

    def _handle_idle(self, *args):
        pass
