import queue
import serial
import logging
import threading
import serial.threaded


class ATProtocol(serial.threaded.Protocol):

    SEND_TERMINATOR = b'\r'
    REVC_TERMINATOR = b'\r\n'
    ENCODING = 'latin-1'
    _logger = logging.getLogger('at_protocol')

    def __init__(self):
        serial.threaded.Protocol.__init__(self)
        self.response_lock = threading.Lock()
        self.buffer = bytearray()
        self.transport = None
        self.events = queue.Queue()
        self.responses = queue.Queue()
        self._event_thread = threading.Thread(target=self._run_event, name='at_protocol_event', daemon=True)
        self._event_thread.start()

    def _run_event(self):
        while True:
            try:
                self._logger.debug('_run_event: start')
                self._handle_event(self.events.get())
                self._logger.debug('_run_event: end')
            except:
                self._logger.exception('_run_event')

    def connection_made(self, transport):
        self.transport = transport
        self.transport.serial.reset_input_buffer()

    def connection_lost(self, exc):
        self._logger.warning('connection_lost: %s', exc)
        self.transport = None
        serial.threaded.Protocol.connection_lost(self, exc)

    def data_received(self, data):
        self.buffer.extend(data)
        while self.REVC_TERMINATOR in self.buffer:
            packet, self.buffer = self.buffer.split(self.REVC_TERMINATOR, 1)
            if packet:
                self._logger.debug('packet_received: %r', packet)
                self.packet_received(packet.decode(self.ENCODING))

    def packet_received(self, packet):
        if self.response_lock.locked():
            self.responses.put(packet)
        else:
            self.events.put(packet)

    def send_packet(self, packet):
        if self.transport is not None:
            self.transport.write(packet.encode(self.ENCODING) + self.SEND_TERMINATOR)

    def _handle_event(self, event):
        self._logger.debug('event received: %s', event)

    def send_command(self, command, response='OK', timeout=1):
        with self.response_lock:
            self._logger.debug('%s ->', command)
            self.send_packet(command)
            lines = []
            while True:
                try:
                    line = self.responses.get(timeout=timeout)
                    self._logger.debug('-> %r', line)
                    if line == response:
                        return lines
                    else:
                        lines.append(line)
                except queue.Empty:
                    raise TimeoutError(command)
