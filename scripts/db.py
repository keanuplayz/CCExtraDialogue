# crosscode database.json text-extraction script.
# solely created for parsing side messages during the game,
# while also ignoring other events in commonEvents.
# it does the job, at least.
# by EL2020#0503
#
# changelog:
# v1.1.0
# fixes some issues regarding not fully extracting data.
# also, slightly improved output formatting! :)

import json
from typing import Union

# points to database.json.
databaseFilePath: str = "database.json"
# file that script will write data to.
exportFilePath: str = "export.txt"

def handleMessage(messageBody: dict, lang: str = "en_US") -> str:
    #converts internal names to actual names.
    characterLookup: dict = {
        "main.lea": "Lea",
        "main.emilie": "Emilie",
        "main.glasses": "C'tron",
        "antagonists.fancyguy": "Apollo",
        "antagonists.sidekick": "Joern",
        "main.shizuka": "Shizuka",
        "main.schneider": "Lukas",
        "main.luke": "Luke",
        "main.sergey": "Sergey",
        "main.sergey-av": "Sergey (Avatar)"
    }

    messageText: dict = messageBody["message"]
    messagePerson: dict = messageBody["person"]
    person: str = ""
    text: str = ""
    #handles names and expressions
    if messagePerson["person"] in characterLookup:
        person = f"{characterLookup[messagePerson['person']]} > {messagePerson['expression']}"
    else: #in case there is an unknown character
        person = f"messagePerson['person'] > {messagePerson['expression']}"
    
    #only returns one language's text. rstrip to remove any trailing \n's.
    text = messageText[lang].rstrip()

    return f"{person}: {text}"

def processEvent(eventData: Union[dict, list]) -> str:
    processString: str = ""
    if "message" in eventData:
        processString += handleMessage(eventData) + "\n"
    else: 
        if type(eventData) is dict:
            for key, item in eventData.items():
                if type(item) in [list, dict]:
                    processString += f"{key}:\n{processEvent(item)}\n"
                else:
                    processString += f"{key}: {item}\n"
        elif type(eventData) is list:
            for i in range(len(eventData)):
                if type(eventData[i]) in [list, dict]:
                    processString += processEvent(eventData[i])
                else:
                    processString += f"{eventData[i]}\n"
    return processString


with open(databaseFilePath, "r") as databaseFile, \
     open(exportFilePath, "w", encoding="utf-8") as exportFile:
    commonEventData: dict = json.load(databaseFile)["commonEvents"] #grabs just the common event dialog data.
    
    for eventName, eventValue in commonEventData.items():
        if "SHOW_SIDE_MSG" not in str(eventValue): continue #only extract dialogue
        dataString: str = ""
        
        dataString += eventName + "\n" + ("-" * 25) + "\n"
        if "condition" in eventValue: dataString += f"Condition: {eventValue['condition']}\n\n"
        dataString += "Event type:\n"
        for key, value in eventValue["type"].items():
            dataString += f"{key}: {value}\n"
        dataString += "\n"
        print(eventName)

        #actual event data
        eventData = eventValue["event"]
        for i in range(len(eventData)):
            if len(eventData) > 1: 
                dataString += f"Event {i}:\n"
            else:
                dataString += "Event:\n"
            dataString += processEvent(eventData[i])

        dataString += "\n"

        exportFile.write(dataString)