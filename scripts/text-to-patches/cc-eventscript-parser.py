import json
import os
import re
import sys

# ~ crosscode eventscript v1.2.0 parser, by EL ~
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

debug = False

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
messageRegex = re.compile(r"^(?:message|event) (\d+):?$", flags=re.I)
# matches strings of the form "== title =="
titleRegex = re.compile(r"^== (.+) ==$")
# matches strings of the form "(key): (value)"
propertyRegex = re.compile(r"^(\w+)\s*:\s*(.+)$")
# matches "set (varname) (true/false)"
setVarBoolRegex = re.compile(r"^set\s+([\w\.]+)(?:\s+|(?:\s*=\s*))(true|false)$", flags=re.I)
# matches "set (varname) (+/-/=) (number)"
setVarNumRegex = re.compile(r"^set\s+([\w\.]+)\s*(=|\+|-)\s*(\d+)$", flags=re.I)

# matches "if (condition)", "else", and  "endif" respectively
ifRegex = re.compile(r"^if (.+)$")
elseRegex = re.compile(r"^else$")
endifRegex = re.compile(r"^endif$")
#endregion regex

genIfSkeleton = lambda condition: {"withElse": False, "type": "IF", "condition": condition, "thenStep": []}
genMessageSetSkeleton = lambda num: genIfSkeleton(f"call.runCount == {num}")
genChangeBoolSkeleton = lambda var, value: {"changeType": "set","type": "CHANGE_VAR_BOOL","varName": var, "value": value}
genChangeNumSkeleton = lambda var, type, value: {"changeType": type,"type": "CHANGE_VAR_BOOL","varName": var, "value": value}


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

def handleEvent(eventStr: str) -> dict:

    def processEvents(eventStr: str, isIf: bool = False) -> list[dict]:
        workingList: list[dict] = []
        ifCount: int = 0
        ifCondition: str = ""
        stringBuffer: str = ""
        ifEventList = []
        hasElse = False

        for line in eventStr.splitlines():
            line = line.strip()
            if match := re.match(ifRegex, line):
                if ifCount == 0:
                    ifCondition = match.group(1)
                else:
                    stringBuffer += line + "\n"
                ifCount += 1

            elif re.match(endifRegex, line):
                if ifCount > 1:
                    stringBuffer += line + "\n"
                    ifCount -= 1
                elif ifCount < 1:
                    raise Exception("Error: 'endif' found outside of if block")
                else:
                    ifBlock = genIfSkeleton(ifCondition)
                    ifBlock["thenStep"], ifBlock["elseStep"] = processEvents(stringBuffer, True)
                    if ifBlock["elseStep"] is not None: ifBlock["withElse"] = True
                    else: del ifBlock["elseStep"]
                    ifCount = 0
                    workingList.append(ifBlock)

            # adds to string buffer for later processing
            elif ifCount > 0:
                stringBuffer += line + "\n"

            elif re.match(elseRegex, line):
                if (not isIf):
                    raise Exception("Error: 'else' statement found outside of if block.")
                elif hasElse:
                    raise Exception("Error: Multiple 'else' statements found inside of if block.")
                else:
                    hasElse = True
                    ifEventList = workingList.copy()
                    workingList = []

            elif match := re.match(dialogueRegex, line):
                workingList.append(processDialogue(line))

            elif match := re.match(setVarBoolRegex, line):
                workingList.append(genChangeBoolSkeleton(match.group(1),bool(match.group(2))))

            elif match := re.match(setVarNumRegex, line):
                varName, sign, number = match.groups()
                if sign == "=":
                    newEvent = genChangeNumSkeleton(varName, "set", int(number))
                elif sign in ["+", "-"]:
                    newEvent = genChangeNumSkeleton(varName, "add", int(f"{sign}{number}"))
                workingList.append(newEvent)

        if isIf: 
            if not hasElse:
                return workingList, None
            else:
                return ifEventList, workingList

        return workingList

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
    stringBuffer = ""
    trackMessages = False

    for line in eventStr.splitlines():
        line = line.strip()
        # skip blank lines and comments
        if (not line) or re.match(commentRegex, line): continue

        if match := re.match(messageRegex, line):
            if trackMessages:
                workingEvent = genMessageSetSkeleton(messageNumber)
                workingEvent["thenStep"] = processEvents(stringBuffer)
                event["event"].append(workingEvent)
                stringBuffer = ""

            messageNumber += 1
            trackMessages = True
            event["runOnTrigger"].append(int(match.group(1)))

        elif trackMessages:
            stringBuffer += line + "\n"

        elif match := re.match(propertyRegex, line):
            propertyName, value = match.groups()
            if propertyName in ["frequency", "repeat", "condition", "eventType", "loopCount"]:
                event[propertyName] = value
            else: 
                print(f"Unrecognized property \"{propertyName}\", skipping...", file = sys.stderr)

        else:
            print(f"Unrecognized line \"{line}\", ignoring...", file = sys.stderr)
        
    workingEvent = genMessageSetSkeleton(messageNumber)
    workingEvent["thenStep"] = processEvents(stringBuffer)
    event["event"].append(workingEvent)

    return event

eventDict = {}
currentEvent: str = ""
bufferString = ""
inputFilename = sys.argv[1] if not debug else "example.txt"

if __name__ == "__main__":
    with open(inputFilename, "r") as inputFile:
        for line in inputFile:
            if re.match(commentRegex, line): continue

            if match := re.match(titleRegex, line):
                if currentEvent != "": # check that the event isn't empty so it only runs if there's actually something there
                    eventDict[currentEvent] = handleEvent(bufferString)
                # set the current event and clear the buffer
                currentEvent = match.group(1)
                if currentEvent in eventDict:
                    raise KeyError("Duplicate event name found in input file.")
                bufferString = ""
            else:
                bufferString += line + "\n"
        eventDict[currentEvent] = handleEvent(bufferString)

    os.makedirs("./patches/", exist_ok = True)
    os.makedirs("./assets/data/", exist_ok = True)

    with open("./assets/data/database.json.patch", "w+") as patchFile:
        patchDict: list[dict] = []
        patchDict.append({"type": "ENTER", "index": "commonEvents"})
        for key, value in eventDict.items():
            with open(f"./patches/{key}.json", "w+") as jsonFile:
                json.dump({key: value}, jsonFile, indent = 2 if debug else 0)
            patchDict.append(
                {
                    "type": "IMPORT",
                    "src": f"mod:patches/{key}.json"
                }
            ),
        patchDict.append({"type": "EXIT"})
        json.dump(patchDict, patchFile, indent = 2 if debug else 0)
