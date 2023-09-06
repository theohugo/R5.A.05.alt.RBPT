from random import randint
from character import *
from action import *
from arena import *

class Engine:
    def __init__(self, minPlayers: int = 2):
        self._turnId = 0
        self._arena = Arena()
        
        #### parameters ####
        self._minPlayers = minPlayers
        pass


    def addPlayer(self, character):
        self._arena.addPlayer(character)

    def single_run(self):
        # battleroyal, we continue the fight until there is only 1 character left
        if self._arena.getNbPlayer() <= self._minPlayers:
            # execution of each character's action
            leavers = []
            for i in range(self._arena.getNbPlayer()):
                # process damage
                character = self._arena.getPlayerByIndex(i)
                # if the character is dead, we do not need to play with him
                if not character.isDead():
                    action, targetId = character.getAction()
                    if action == ACTION.HIT:
                        target = self._arena.getPlayerByName(targetId)
                        tLife = target.getLife()
                        tArmor = target.getArmor()
                        cStrength = character.getStrength()
                        if target.getAction() == ACTION.BLOCK:
                            target.setLife(tLife - abs(tArmor - cStrength))
                        elif target.getAction() == ACTION.DODGE:
                            r = randint(1, 10)
                            tSpeed = target.getSpeed()
                            if tSpeed <= r:
                                target.setLife(tLife - cStrength)
                        else:
                            target.setLife(tLife - cStrength)
                        # update the target
                        self._arena.updatePlayer(target)
                        # move to another arena
                    elif action == ACTION.FLY:
                        leavers.append(character)
            for leaver in leavers:
                self._arena.removePlayer(leaver)