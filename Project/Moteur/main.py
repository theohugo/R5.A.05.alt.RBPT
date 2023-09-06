from character import *
from engine import *

if __name__ == '__main__':
    engine = Engine()
    a = CharacterProxy("A", 10, 8, 3, 2)
    a.setAction(ACTION.HIT)
    b = CharacterProxy("B", 7, 8, 1, 4)
    b.setAction(ACTION.HIT)
    b.setTarget(a.getId())
    a.setTarget(b.getId())
    engine.addPlayer(a)
    engine.addPlayer(b)
    print(a, b)
    engine.single_run()
    print(a, b)