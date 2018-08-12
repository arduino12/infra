from pygame.locals import USEREVENT


_next_event_id = USEREVENT
def get_next_event_id():
    _next_event_id += 1
    return _next_event_id
