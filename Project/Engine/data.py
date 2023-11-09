import time
import json

class Data:
    def __init__(self):
        self._history = {}
        self._filename = "data.json"

    def addData(self, key, value):
        if not key in self._history:
            self._history[key] = []    
        self._history[key].append((time.time(), value))

    def save(self):
        f = open(self._filename, "w")
        toWrite = json.dumps(self._history)
        f.write(toWrite)
        f.close()

    def getHistory(self):
        return self._history
