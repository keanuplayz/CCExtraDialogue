# crosscode database.json text-extraction script.
# solely created for parsing side messages during the game,
# while also ignoring other events in commonEvents.
# it does the job, at least.
# by EL2020#0503

import json

# points to database.json.
databaseFilePath: str = "database.json"

# file that script will write data to.
exportFilePath: str = "export.txt"


def handleMessage(messageBody: dict, lang: str = "en_US") -> str:
    # converts internal names to actual names.
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
        "main.sergey-av": "Sergey (Avatar)",
    }

    messageText: dict = messageBody["message"]
    messagePerson: dict = messageBody["person"]
    person: str = ""
    text: str = ""
    # handles names and expressions
    if messagePerson["person"] in characterLookup:
        person = f"{characterLookup[messagePerson['person']]} > {messagePerson['expression']}"
    else:  # in case there is an unknown character
        person = f"messagePerson['person'] > {messagePerson['expression']}"

    # only returns one language's text. rstrip to remove any trailing \n's.
    text = messageText[lang].rstrip()

    return f"{person}: {text}"


with open(databaseFilePath, "r") as databaseFile, open(
    exportFilePath, "w", encoding="utf-8"
) as exportFile:
    commonEventData: dict = json.load(databaseFile)[
        "commonEvents"
    ]  # grabs just the common event dialog data.

    for eventName, eventValue in commonEventData.items():
        if "SHOW_SIDE_MSG" not in str(eventValue):
            continue  # only extract dialogue
        dataString: str = ""

        dataString += eventName + "\n" + ("-" * 25) + "\n"
        if "condition" in eventValue:
            dataString += f"Condition: {eventValue['condition']}\n\n"
        dataString += "Event type:\n"
        for key, value in eventValue["type"].items():
            dataString += f"{key}: {value}\n"
        dataString += "\n"

        # actual event data
        eventData = eventValue["event"][0]
        dataString += "Event data:\n"

        if "message" in eventData:
            dataString += handleMessage(eventData) + "\n"
        else:
            for eventKey, eventValue in eventData.items():
                if type(eventValue) is list:
                    dataString += eventKey + ":\n"
                    for value in eventValue:
                        if "message" in value:
                            dataString += handleMessage(value) + "\n"
                        elif type(value) is dict:
                            for key2, value2 in value.items():
                                if type(value2) is list:
                                    dataString += f"{key2}:\n"
                                    for value3 in value2:
                                        if "message" in value3:
                                            dataString += f"{handleMessage(value3)}\n"
                                        else:
                                            # heard you liked loops, so we put a for loop in your for loop in your for loop in your for loop in your...
                                            for key4, value4 in value3.items():
                                                dataString += f"{key4}: {value4}\n"
                                else:
                                    dataString += f"{key2}: {value2}\n"
                        else:
                            for key2, value2 in value.items():
                                dataString += f"{key2}: {value2}\n"
                    dataString += "\n"
                else:
                    dataString += f"{eventKey}: {eventValue}\n"
        dataString += "\n\n"
        exportFile.write(dataString)
