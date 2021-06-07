import re
import json
import sys
import os

# ~ crosscode eventscript processor v1.1.0, by EL ~
# it should work, i'm pretty sure :) [famous last words?]
# to run:
#   python dialogue-converter.py <input text file>
#
# to make a text file:
#   == event title ==
#   property: value  # all modifiable properties have default values.
#   property: value  # that means you do not have to add them. Most cases do not need to.
#   property: value  # in fact, it is best to leave as is unless necessary. 
#   property: value  # frequency: REGULAR, repeat: ONCE, eventType: PARALLEL, loopCount: 3
#   condition: ""    # if not noted, event will always be able to run.
#   
#   message 1:
#   character > EXPRESSION: message
#   character > EXPRESSION: message
#   character > EXPRESSION: message
#
#   message 2:
#   character > EXPRESSION: message
#   character > EXPRESSION: message
#   character > EXPRESSION: message
#
#   == event title ==
#   property: value
#   ...
#
# (see example text file for a more clear example.)



# a handy dictionary for converting a character's readable name to their internal name.
# it's simple enough to add more characters (or even custom characters!) to this.
# just add a new key of the "readable" name (in lowercase), and the corresponding internal name.
characterLookup: dict = {
    'lea': 'main.lea',
    'emilie': 'main.emilie',
    'c\'tron': 'main.glasses',
    'apollo': 'antagonists.fancyguy',
    'joern': 'antagonists.sidekick',
    'shizuka': 'main.shizuka',
    'lukas': 'main.schneider',
    'schneider': 'main.schneider',
    'luke': 'main.luke',
    'sergey': 'main.sergey',
    'sergey (avatar)': 'main.sergey-av',
    'beowulf': 'main.grumpy',
    'buggy': 'main.buggy',
    'hlin': 'main.guild-leader'
}

#region regex

# matches lines that start with "#" or "//"
commentRegex = re.compile(r"^(?:#|\/\/).*")
# matches strings of the form "(character) > (expression): (message)" or "(character) > (expression) (message)"
dialogueRegex = re.compile(r"(.+)\s*>\s*([A-Z_]+)[\s:](.+)$")
# matches strings of the form "message (number)", insensitive search
messageRegex = re.compile(r"^message (\d+):?$", flags=re.I)
# matches strings of the form "== title =="
titleRegex = re.compile(r"^== (.+) ==$")
# matches strings of the form "(key): (value)"
propertyRegex = re.compile(r"^(\w+)\s*:\s*(.+)$")
# matches "set (varname) (true/false)"
setVarBoolRegex = re.compile(r"^set\s+([\w\.]+)\s+(true|false)$", flags=re.I)

# matches "if (condition)", "else", and  "endif" respectively
ifRegex = re.compile(r"^if (.+)$")
elseRegex = re.compile(r"^else$")
endifRegex = re.compile(r"^endif$")
#endregion regex

genMessageSetSkeleton = lambda num: {"withElse": False, "type": "IF", "condition": f"call.runCount == {num}", "thenStep": []}
genChangeBoolSkeleton = lambda var, value: {"changeType": "set","type": "CHANGE_VAR_BOOL","varName": var, "value": value}


def processDialogue(inputString: str) -> dict:
    messageMatch = re.match(dialogueRegex, inputString)
    readableCharName, expression, message = messageMatch.groups()
    charName: str = characterLookup[readableCharName.strip().lower()]

    messageEvent = {
        "message": {
            "en_US": message.strip()
        },
        "type": "SHOW_SIDE_MSG",
        "person": {
            "person": charName,
            "expression": expression.strip()
        }
    }
    return messageEvent

def processEvent(eventStr: str) -> dict:
    event = {
        "frequency": "REGULAR",
        "repeat": "ONCE",
        "condition": "true",
        "eventType": "PARALLEL",
        "runOnTrigger": [],
        "event": [],
        "overrideSideMessage": False,
        "loopCount": 3,
        "type": {
            "killCount": 0,
            "type": "BATTLE_OVER"
        }
    }
    
    messageNumber = 0
    for line in eventStr.splitlines():
        line = line.strip()

        if match := re.match(propertyRegex, line):
            propertyName, value = match.groups()
            if propertyName in ["frequency", "repeat", "condition", "eventType", "loopCount"]:
                event[propertyName] = value
            else: 
                print(f"Unrecognized property \"{propertyName}\", skipping...", file = sys.stderr)

        elif match := re.match(messageRegex, line):
            messageNumber += 1
            event["runOnTrigger"].append(int(match.group(1)))
            event["event"].append(genMessageSetSkeleton(messageNumber))

        elif match := re.match(dialogueRegex, line):
            if messageNumber == 0: continue
            # note to self - you're gonna have to re-write all of this event-adding.
            # have fun ;)
            event["event"][messageNumber - 1]["thenStep"].append(processDialogue(line))

        elif match := re.match(setVarBoolRegex, line):
            event["event"][messageNumber - 1]["thenStep"].append(genChangeBoolSkeleton(match.group(1),bool(match.group(2))))

        else:
            if(line): print(f"Unrecognized line \"{line}\", ignoring...", file = sys.stderr)
    return event

eventDict = {}
currentEvent: str = ""
bufferString = ""
inputFilename = sys.argv[1]

with open(inputFilename, "r") as inputFile:
    for line in inputFile:
        if re.match(commentRegex, line): continue
        
        if match := re.match(titleRegex, line):
            if currentEvent != "": # check that the event isn't empty so it only runs if there's actually something there
                eventDict[currentEvent] = processEvent(bufferString)
            # set the current event and clear the buffer
            currentEvent = match.group(1)
            if currentEvent in eventDict:
                raise KeyError("Duplicate event name found in input file.")
            bufferString = ""
        else:
            bufferString += line + "\n"
    eventDict[currentEvent] = processEvent(bufferString)

os.makedirs("./patches/", exist_ok = True)
os.makedirs("./assets/data/", exist_ok = True)

with open("./assets/data/database.json.patch", "w+") as patchFile:
    patchDict: list[dict] = []
    patchDict.append({"type": "ENTER", "index": "commonEvents"})
    for key, value in eventDict.items():
        with open(f"./patches/{key}.json", "w+") as jsonFile:
            json.dump({key: value}, jsonFile)
        patchDict.append(
            {
                "type": "IMPORT",
                "src": f"mod:patches/{key}.json"
            }
        ),
    patchDict.append({"type": "EXIT"})
    json.dump(patchDict, patchFile)