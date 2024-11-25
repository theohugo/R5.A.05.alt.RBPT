from random import randint
from Project.Engine.action import *

class CharacterProxy:
    def __init__(self, cid: str, teamid: str, life: int, strength: int, armor: int, speed: int, arena_id: int, name: str = None):
        self._id = cid
        self._teamid = teamid
        self._name = name if name else cid 
        self._life = life
        self._strength = strength
        self._armor = armor
        self._speed = speed
        self._arena_id = arena_id
        self._action = None
        self._target = None
        self._dead = False

    def getName(self):
        return self._name

    def isDead(self):
        return self._dead

    def isId(self, cid):
        return self._id == cid

    def getId(self):
        return self._id

    def getLife(self):
        return self._life

    def getStrength(self):
        return self._strength

    def getArmor(self):
        return self._armor

    def getSpeed(self):
        return self._speed
    
    def getArenaId(self):
        return self._arena_id

    def getAction(self):
        if self._action == ACTION.HIT or self._action == ACTION.FLY:
            return self._action, self._target
        return self._action, None

    def setLife(self, value):
        self._life = value
        if self._life <= 0:
            self._dead = True

    def setStrength(self, value):
        self._strength = value

    def setArmor(self, value):
        self._armor = value

    def setSpeed(self, value):
        self._speed = value

    def setAction(self, value):
        self._action = value
    
    def setTarget(self, value):
        self._target = value
        
    def setArena(self, value):
        self._arena_id = value

    def __str__(self):
        s = "------------\n"
        s += "cid : " + self._id + ",\n"
        s += "name : " + self._name + ",\n"
        s += "life : " + str(self._life) + "\n"
        s += "strength : " + str(self._strength) + "\n"
        s += "armor : " + str(self._armor) + "\n"
        s += "speed : " + str(self._speed) + "\n"
        s += "arena : " + str(self._arena_id) + "\n"
        s += "------------\n"
        return s

    def toDict(self):
        cDict = {
            "cid": self._id,
            "teamid": self._teamid,
            "name": self._name,
            "life": self._life,
            "strength": self._strength,
            "armor": self._armor,
            "speed": self._speed,
            "action": actionToStr(self._action),
            "target": str(self._target),
            "dead": self._dead,
            "arena_id": self._arena_id
        }
        return cDict

