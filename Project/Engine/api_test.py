from random import randint
from action import *
import requests
import time

url = "http://127.0.0.1:5000/"

def action_selection():
    r = randint(0, 2)
    action = None
    if r == 0:
        action = ACTION.HIT
    elif r == 1:
        action = ACTION.BLOCK
    elif r == 2:
        action = ACTION.DODGE
    elif r == 3:
        action = ACTION.FLY
    return r

def cid_selection():
    return str(randint(10, 1000))

def target_selection(cids):
    r = randint(0, len(cids) - 1)
    return cids[r]

teamA = "A"
teamB = "B"

# add new characters
a = cid_selection()
b = cid_selection()
c = cid_selection()
d = cid_selection()
print("Création des cid " + str(a) + " et " + str(b))
x = requests.get(url + "enterArena/" + str(b) + "/" + teamB + "/14/1/5/0")
x = requests.get(url + "enterArena/" + str(d) + "/" + teamB + "/3/15/5/2")
x = requests.get(url + "enterArena/" + str(a) + "/" + teamA + "/10/4/4/2")
x = requests.get(url + "enterArena/" + str(c) + "/" + teamA + "/8/4/4/4")
print(x.text)

print(x.text)
# process a single run
x = requests.get(url + "run")
print(x.text)

for j in range(5):
    # add actions
    for i in range(5):
        x = requests.get(url + "setAction/" + str(a) + "/" + str(action_selection()))
        x = requests.get(url + "setAction/" + str(b) + "/" + str(action_selection()))
        x = requests.get(url + "setAction/" + str(c) + "/" + str(action_selection()))
        x = requests.get(url + "setAction/" + str(d) + "/" + str(action_selection()))
        print(x.text)
        # add targets
        x = requests.get(url + "setTarget/" + str(a) + "/" + str(target_selection([b, d])))
        x = requests.get(url + "setTarget/" + str(c) + "/" + str(target_selection([b, d])))
        x = requests.get(url + "setTarget/" + str(b) + "/" + str(target_selection([a, c])))
        x = requests.get(url + "setTarget/" + str(d) + "/" + str(target_selection([a, c])))
        print(x.text)
        time.sleep(5)

