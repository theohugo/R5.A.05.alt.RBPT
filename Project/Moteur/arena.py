class Arena:
    def __init__(self):
        self._playersList = []

    def getNbPlayer(self):
        return len(self._playersList)

    def getPlayerByIndex(self, index):
        return self._playersList[index]

    def getPlayerByName(self, id):
        for character in self._playersList:
            if character.isId(id):
                return character
        return None

    def updatePlayer(self, character):
        for i in range(len(self._playersList)):
            if self._playersList[i].isId(character.getId()):
                self._playersList[i] = character

    def addPlayer(self, character):
        self._playersList.append(character)

    def removePlayer(self, character):
        for i in range(len(self._playersList)):
            del self._playersList[i]