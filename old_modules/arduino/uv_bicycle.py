import logging


from infra.old_modules.arduino.arduino_protocol import ArduinoProtocol


class UvBicycle(ArduinoProtocol):

    def __init__(self):
        ArduinoProtocol.__init__(self)
        self._events_handlers = {

        }

    def _handle_event(self, event):
        for event_start in self._events_handlers:
            if event.startswith(event_start):
                return self._events_handlers[event_start](event)
        logging.warning('unhandled event: {!r}'.format(event))

    def set_slice_on_ms(self, ms):
        self.send_command('A %s' % (ms,), response=str(ms))

    def set_slice_off_ms(self, ms):
        self.send_command('B %s' % (ms,), response=str(ms))

    def set_char_off_ms(self, ms):
        self.send_command('C %s' % (ms,), response=str(ms))

    def set_right_to_left(self, rtl):
        self.send_command('D %s' % (rtl,), response='1' if rtl else '0')

    def draw_text(self, text):
        l = len(text)
        self.send_command('E %s' % (text,), response=str(l), timeout=1+l*2)
        # self.send_command('E %s' % (text,), response='@', timeout=1+l*2)
        # self.send_packet('E %s' % (text,))

    def draw_fix_text(self, index):
        self.send_command('F %s' % (index,), response=str(index), timeout=30)

    def set_screen_saver_sec(self, sec):
        self.send_command('G %s' % (sec,), response=str(sec))

    def set_leds_mask(self, mask):
        self.send_command('I %s' % (mask,), response=str(mask))

    def draw_text_rtl(self, text, rtl=True):
        text = text.strip()
        if text == "":
            return
        self.set_right_to_left(rtl)
        text = self.fix_text(text)
        if rtl:
            text = text[::-1]
        self.draw_text(text)
        
    def fix_text(self, text):
        text = text.strip()
        if text == "":
            return
        rtl = self.is_heb_char(text[0])
        
        tmp = []
        tmp2 = []
        last_pos = 0
        last_pos2 = 0
        last_dir = 0
        text2 = ""
        if rtl:
            for c in text:
                if self.is_eng_char_or_number(c):
                    if len(tmp2):
                        tmp = tmp2 + tmp
                    tmp2.clear()
                    last_pos2 = 0
                    tmp.insert(last_pos, c)
                    last_pos += 1
                    last_dir = 1
                elif self.is_heb_char(c):
                    if len(tmp2):
                        tmp = tmp2 + tmp
                    tmp2.clear()
                    last_pos2 = 0
                    if last_dir != 2:
                        last_pos = 0
                    tmp.insert(last_pos, c)
                    last_dir = 2
                else:
                    if last_dir == 1 or last_dir == 5:
                        tmp2.insert(last_pos2, c)
                        last_pos2 += 1
                        last_dir = 5
                    elif last_dir == 2 or last_dir == 6:
                        tmp2.insert(last_pos2, c)
                        last_dir = 6
        else:
            for c in text:
                if self.is_eng_char_or_number(c):
                    if last_dir != 1 or last_dir != 5:
                        last_pos = len(tmp)
                    ll = len(tmp2)
                    if ll:
                        # lstTmp.AddAllAt(lastPos, lstTmp2)
                        tmp = tmp[:last_pos] + tmp2 + tmp[last_pos:]
                        last_pos += ll
                    tmp2.clear()
                    last_pos2 = 0
                    tmp.insert(last_pos, c)
                    last_pos += 1
                    last_dir = 1
                elif self.is_heb_char(c):
                    ll = len(tmp2)
                    if ll:
                        # lstTmp.AddAllAt(lastPos, lstTmp2)
                        tmp = tmp[:last_pos] + tmp2 + tmp[last_pos:]
                        if last_dir != 2 or last_dir != 6:
                            last_pos += ll
                    tmp2.clear()
                    last_pos2 = 0
                    tmp.insert(last_pos, c)
                    last_dir = 2
                else:
                    if last_dir == 1 or last_dir == 5:
                        tmp2.insert(last_pos2, c)
                        last_pos2 += 1
                        last_dir = 5
                    elif last_dir == 2 or last_dir == 6:
                        tmp2.insert(last_pos2, c)
                        last_dir = 6

        if rtl:
            if last_dir == 2 or last_dir == 6:
                text2 += "".join(tmp2)
            else:
                text2 += "".join(tmp2[::-1])
        text2 += "".join(tmp)
        if rtl:
            for p in ['()', '[]', '{}', '<>']:
                text2 = text2.replace(p[0], '\0').replace(p[1], p[0]).replace('\0', p[1])
        else:
            if last_dir == 2 or last_dir == 6:
                text2 += "".join(tmp2[::-1])
            else:
                text2 += "".join(tmp2)
        
        
        return text2
        
    def is_heb_char(self, char):
        return 'א' <= char <= 'ת'
    
    def is_eng_char_or_number(self, char):
        return char.upper().isupper() or char.isnumeric()
