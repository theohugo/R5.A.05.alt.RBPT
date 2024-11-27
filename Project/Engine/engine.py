# engine.py

from random import randint
from Project.Engine.character import *
from Project.Engine.action import *
from Project.Engine.arena import *
from Project.Engine.data import *
import time
import json
import threading

class Engine:
    def __init__(self, minPlayersToStart: int = 2, characterTimeout: int = 5):
        self._lock = threading.Lock()  # Initialization of the lock
        self._turnId = 0
        # Data about the game
        self._data = Data()
        # State of the arena and characters' characteristics at each round
        self._history = {}
        self._arena = Arena(self._data, self._turnId)
        self._run = False
        self._goldBook = {}
        self._ipMap = {}
        #### parameters ####
        self._minPlayersToStart = minPlayersToStart
        self._characterTimeout = characterTimeout

    def setActionTo(self, cid, action):
        with self._lock:
            return self._arena.setActionTo(cid, action)

    def setTargetTo(self, cid, target):
        with self._lock:
            return self._arena.setTargetTo(cid, target)

    def getPlayerByName(self, cid):
        with self._lock:
            return self._arena.getPlayerByName(cid)

    def addPlayer(self, character, ip):
        with self._lock:
            self._arena.addPlayer(character)
            cId = character.getId()
            self._ipMap[cId] = ip
            if not cId in self._goldBook:
                self._goldBook[cId] = 0

            # Ajout du turnId dans les données de l'entrée dans l'arène
            enter_arena_data = character.toDict()
            enter_arena_data["turn_id"] = self._turnId
            
            # Ajout des données au journal
            self._data.addData("enter_arena", enter_arena_data)
            self._data.addData("gold", {cId: self._goldBook[cId]})

    def getIP(self, cid):
        with self._lock:
            if cid in self._ipMap:
                return self._ipMap[cid]
            return None  

    def isReadyToStart(self):
        with self._lock:
            flag = self._arena.getActiveNbPlayer() >= self._minPlayersToStart
            flag &= self._arena.everyoneHasAnAction()
            return flag

    def isReady(self):
        with self._lock:
            flag = self._arena.getActiveNbPlayer() >= 2
            flag &= self._arena.everyoneHasAnAction()
            return flag

    def stop(self):
        with self._lock:
            self._data.addData("stop_game", "")
            self._run = False

    def single_run(self):
        with self._lock:
            # Execution of each character's action
            leavers = []
            # Sort the players by speed
            self._arena._playersList.sort(key=lambda x: x.getSpeed(), reverse=True)
            for i in range(self._arena.getTotalNbPlayer()):
                # Process damage
                character = self._arena.getPlayerByIndex(i)
                # If the character is dead, we do not need to play with him
                if not character.isDead():
                    statistics = {}
                    action, targetId = character.getAction()
                    target = self._arena.getPlayerByName(targetId)
                    if action == ACTION.HIT and not target.isDead():
                        statistics["character"] = character.getId()
                        statistics["target"] = target.getId()
                        tLife = target.getLife()
                        tArmor = target.getArmor()
                        cStrength = character.getStrength()
                        tAction, _ = target.getAction()
                        if tAction == ACTION.BLOCK:
                            # We use a logarithmic function to compute the reduced damages
                            reducedDamages = (1 - (tArmor / (tArmor + 8))) * cStrength
                            target.setLife(tLife - reducedDamages)
                            statistics["damage"] = reducedDamages
                            statistics["reduced"] = cStrength - reducedDamages
                            statistics["dodged"] = 0

                        elif tAction == ACTION.DODGE:
                            # There is a speed/25 chance to dodge an attack (means that there is 80% dodge chance at 20 speed)
                            tSpeed = target.getSpeed()
                            r = randint(0, 25)
                            statistics["damage"] = 0
                            statistics["reduced"] = 0
                            statistics["dodged"] = 0
                            if r <= tSpeed:
                                statistics["dodged"] = cStrength
                            else:
                                target.setLife(tLife - cStrength)
                                statistics["damage"] = cStrength

                        else:
                            target.setLife(tLife - cStrength)
                            statistics["damage"] = cStrength
                            statistics["reduced"] = 0
                            statistics["dodged"] = 0
                        self._data.addData("damage", statistics)

                        # Earn gold if the character killed someone
                        if target.isDead():
                            cId = character.getId()
                            self._data.addData("death", {"character": targetId, "killer": character.getId()})
                            self._goldBook[cId] += 10
                            self._data.addData("gold", {cId: self._goldBook[cId]})
                        # Update the target (actually not necessary!)
                        self._arena.updatePlayer(target)
                        
                        # Move to another arena
                    elif action == ACTION.FLY:
                        leavers.append(character)
                # Reset the character's action and target
                character.setAction(None)
                character.setTarget(None)
            for leaver in leavers:
                self._arena.removePlayer(leaver)
            self._turnId += 1
            self._arena._turnId += 1
            self._data.addData("turn_id", self._turnId)

    def run(self):
        with self._lock:
            if not self._run:
                self._run = True
                self._data.addData("start_game", "")
        # Battle Royale: continue the fight until there is only 1 character left
        while self._run:
            self.single_run()
            # Save logs
            self._data.save()
            # Wait until all players have set their actions or the game is stopping
            while not self.isReady() and self._run:
                time.sleep(0.1)  # Sleep to prevent a busy-wait loop
        # After exiting the loop, ensure that the final state is saved
        with self._lock:
            # Optionally, you can process a final run or ensure data consistency here
            self._data.save()

    def isRunning(self):
        with self._lock:
            return self._run
    
    # Get an observation of the arena that will be sent to every agent
    def getState(self):
        with self._lock:
            arena_data = self._arena.toDict()
            arena_data["round"] = self._turnId
            self._history[self._turnId] = arena_data
            return json.dumps(arena_data)

    def getStates(self):
        with self._lock:
            return json.dumps(self._history)
