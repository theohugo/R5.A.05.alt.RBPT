from enum import Enum

class ACTION(Enum):
    HIT = 0
    BLOCK = 1
    DODGE = 2
    FLY = 3

def actionToStr(action):
    r = None
    if action == ACTION.HIT:
        r = 0
    elif action == ACTION.BLOCK:
        r = 1
    elif action == ACTION.DODGE:
        r = 2
    elif action == ACTION.FLY:
        r = 3
    return str(r)