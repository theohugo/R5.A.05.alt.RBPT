from action import *
from random import randint

class CharacterProxy:
    def __init__(self, name :str, life :int, strength :int, armor :int, speed :int):
        self._name = name
        self._life = life
        self._strength = strength
        self._armor = armor
        self._speed = speed
        self._action = None
        self._target = None
        self._id = self._name + str(randint(0, 1000))
        self._dead = False

    def isDead(self):
        return self._dead

    def isId(self, id):
        return self._id == id

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

    def __str__(self):
        s = "------------\n"
        s += "name : " + self._name + "\n"
        s += "life : " + str(self._life) + "\n"
        s += "------------\n"
        return s
