import time
import logging
import datetime

from infra.run import common
from infra.old_modules.m590.at_protocol import ATProtocol


class M590(ATProtocol):
    """

    """
    CALL_RING_TIME = 3

    _logger = logging.getLogger('m590')

    def __init__(self):
        ATProtocol.__init__(self)
        self._events_handlers = {
            '+CMT:': self._sms_recived,
            'RING': self._call_recived,
            '+PBREADY': self._handle_idle,
            'NO CARRIER': self._handle_idle,
            'ERROR': self._handle_idle,
            'connection_made': self._connection_made,
        }
        self._last_call_time = 0
        self._last_sms = None
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
        time.sleep(0.4)
        index = int(index.split('_')[-1])
        try:
            if index == 0:
                self.send_packet('\x1a')
            elif index == 1:
                self.send_command('ATE0')
            elif index == 2:
                self.send_command('AT+CMGF=1')
            elif index == 3:
                self.send_command('AT+CNMI=2,2,0,0,0')
            elif index == 4:
                self.send_command('AT+CSCS="UCS2"')
            elif index == 5:
                self.send_command('AT+CSMP=1,167,0,8')
            elif index == 6:
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
        if self._last_sms is not None:
            args = self._last_sms
            self._last_sms = None
            self._logger.debug('_last_sms: %s event: %s', args, event)
            try:
                text = self.decode_ucs2(event)
            except Exception:
                pass
                self._logger.exception('_handle_event')
            else:
                self.sms_recived(args[0], args[1], text)
                return
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

    def get_csq(self):
        return self.send_command('AT+CSQ')

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

    def send_sms(self, number, text):
        self._logger.info('send_sms TEXT: %s TO: %s', text, number)
        self.send_packet('AT+CMGS="{}"'.format(number))
        time.sleep(0.4)
        self.send_command(self.encode_ucs2(text), timeout=10, terminator=b'\x1A')

    def normalize_phone_number(self, number):
        return number.replace('+972', '0')

    def _sms_recived(self, event):
        try:
            _, number, _, send_time, _ = event.split('"')
        except Exception:
            self._logger.warning('_sms_recived error: %s', event)
            return
        send_time = datetime.datetime.strptime(send_time.split('+')[0], '%y/%m/%d,%H:%M:%S')
        self._last_sms = (number, send_time)
        self._logger.debug('_sms_recived: %s %s', number, send_time)

    def _call_recived(self, event):
        cur_time = time.time()
        if (cur_time - self._last_call_time) > self.CALL_RING_TIME:
            self.call_recived()
        self._last_call_time = cur_time

    def _handle_idle(self, *args):
        pass

    def decode_ucs2(self, hexlify_text):
        return ''.join((b'\\u' + hexlify_text[i: i + 4].encode()).decode('unicode_escape') for i in range(0, len(hexlify_text), 4))
        # userData = []
        # i = 0
        # try:
            # while i < numBytes:
                # userData.append(chr((next(byteIter) << 8) | next(byteIter)))
                # i += 2
        # except StopIteration:
            # pass
        # return ''.join(userData)

    def encode_ucs2(self, text):
        return ''.join('%02x%02x' % (i >> 8, i & 0xFF) for i in map(ord, text))
