# implelemt skipping logic

import argparse
import json
import sys

tenhouTiles = [11, 12, 13, 14, 15, 16, 17, 18, 19, 51, 
               21, 22, 23, 24, 25, 26, 27, 28, 29, 52, 
               31, 32, 33, 34, 35, 36, 37, 38, 39, 53, 
               41, 42, 43, 44, 45, 46, 47, 
               "E", "S", "W", "N", "P", "F", "C"
               "5mr", "5pr", "5sr"]

tileStrings = ["1m", "2m", "3m", "4m", "5m", "6m", "7m", "8m", "9m", "0m",
               "1p", "2p", "3p", "4p", "5p", "6p", "7p", "8p", "9p", "0p",
               "1s", "2s", "3s", "4s", "5s", "6s", "7s", "8s", "9s", "0s",
               "1z", "2z", "3z", "4z", "5z", "6z", "7z",
               "1z", "2z", "3z", "4z", "5z", "6z", "7z",
               "0m", "0p", "0s"]

tileDict = dict(zip(tenhouTiles, tileStrings))

def writeWWYDBotJson(data, kyoku, turn, name):

    jsonString = []
    jsonString.append("{\n\t\"name\": \"" + name + "\",\n")

    rotations = int(data['kyokus'][kyoku]['kyoku'])
    repeats = int(data['kyokus'][kyoku]['honba'])

    winds = ["east", "south", "west", "north"]
    playerWindNum = (int(data['target_actor']) - rotations) % 4
    playerWind = winds[playerWindNum]
    jsonString.append("\t\"seat\": \"" + playerWind + "\",\n")

    jsonString.append("\t\"round\": " + str(rotations) + ",\n")
    jsonString.append("\t\"repeats\": " + str(repeats) + ",\n")
    jsonString.append("\t\"honba\": " + str(0) + ",\n") #???

    startingPoints = [25000, 25000, 25000, 25000]
    roundPointsIndex = 0
    while roundPointsIndex < kyoku:
        player = 0
        for delta in data['kyokus'][roundPointsIndex]['end_status'][0]['deltas']:
            startingPoints[player] = startingPoints[player] + delta
            player = player + 1
        roundPointsIndex = roundPointsIndex + 1
    jsonString.append("\t\"points\": "  + str(startingPoints) + ",\n")

    found = False
    entryNum = -1
    for index, entry in enumerate(data['kyokus'][kyoku]['entries']):
        if int(entry['junme']) == turn and not found:
            entryNum = index
            found = True

    log = data['splited_logs'][kyoku]['log'][0]

    draws = {}
    discards = {}
    numOfDiscards = {}
    finalDiscards = {}
    finalCalls = {}
    initWindIndex = 0
    if playerWind == "east":
        initWindIndex = int(data['target_actor'])
    elif playerWind == "south":
        initWindIndex = (int(data['target_actor']) + 3) % 4
    elif playerWind == "west":
        initWindIndex = (int(data['target_actor']) + 2) % 4
    elif playerWind == "north":
        initWindIndex = (int(data['target_actor']) + 1) % 4
    addWindIndex = 0
    while addWindIndex < 4:
        windIndex = (initWindIndex + addWindIndex) % 4
        draws[winds[addWindIndex]] = log[5 + (windIndex * 3)]
        discards[winds[addWindIndex]] = log[6 + (windIndex * 3)]
        numOfDiscards[winds[addWindIndex]] = 0
        finalDiscards[winds[addWindIndex]] = []
        finalCalls[winds[addWindIndex]] = []
        addWindIndex = addWindIndex + 1

    numOfKans = 0
    currDiscardWindNum = 0
    notDealer = 1
    if playerWind == "east":
        notDealer = 0
    while numOfDiscards[winds[(playerWindNum - 1) % 4]] < turn + notDealer:

        currDiscardWind = winds[currDiscardWindNum]
        currDiscard = discards[currDiscardWind][numOfDiscards[currDiscardWind]]

        isRiichi = False
        if isinstance(currDiscard, str) and currDiscard.startswith("r"):
            isRiichi = True
            currDiscard = int(currDiscard[1:])

        if currDiscard == 60:
            currDiscard = draws[currDiscardWind][numOfDiscards[currDiscardWind]]

        discardWasCalled = False
        for wind in winds:
            if isinstance(draws[wind][numOfDiscards[wind]],str) and str(currDiscard) in draws[wind][numOfDiscards[wind]]:
                replacedTileCall = draws[wind][numOfDiscards[wind]]
                if(replacedTileCall[0] == "c"):
                    chiiTileCall = "c"
                    for i in range(1, len(replacedTileCall), 2):
                        chiiTileCall = chiiTileCall + tileDict[int(replacedTileCall[i] + replacedTileCall[i + 1])]
                    replacedTileCall = chiiTileCall
                else:
                    replacedTileCall = draws[wind][numOfDiscards[wind]].replace(draws[wind][numOfDiscards[wind]][-2:], tileDict[int(draws[wind][numOfDiscards[wind]][-2:])])
                finalCalls[wind].append(replacedTileCall)
                discardWasCalled = True
                currDiscardWindNum = winds.index(wind)
                if len(draws[wind][numOfDiscards[wind]]) > 8:
                    numOfKans = numOfKans + 1
                    numOfDiscards[wind] = numOfDiscards[wind] + 1
        # added kan logic
        if isinstance(currDiscard,str) and len(currDiscard) > 8:
            discardWasCalled = True
            kanTile = tileDict[int(currDiscard[-2:])]
            addedKan = currDiscard.replace(currDiscard[-2:], kanTile)
            addedKanFinalCalls = []
            for tileCall in finalCalls[currDiscardWind]:
                if kanTile in tileCall:
                    addedKanFinalCalls.append(addedKan)
                else:
                    addedKanFinalCalls.append(tileCall)
            finalCalls[currDiscardWind] = addedKanFinalCalls

        if not discardWasCalled:
            if isRiichi:
                finalDiscards[currDiscardWind].append("r" + tileDict[currDiscard])
            else:
                finalDiscards[currDiscardWind].append(tileDict[currDiscard])
            currDiscardWindNum = (currDiscardWindNum + 1) % 4
        numOfDiscards[currDiscardWind] = numOfDiscards[currDiscardWind] + 1

    tilesLeft = 70
    for wind in winds:
        tilesLeft = tilesLeft - len(finalDiscards[wind])
    tilesLeft = tilesLeft - numOfKans
    jsonString.append("\t\"tilesLeft\": " + str(tilesLeft) + ",\n")

    playerHandBefore = data['kyokus'][kyoku]['entries'][entryNum]['state']['tehai']
    playerHandAfter = []
    for tile in playerHandBefore:
        if tile in tileDict.keys():
            newTile = tileDict[tile]
            playerHandAfter.append(newTile)
        else:
            playerHandAfter.append(tile)
    jsonString.append("\t\"hand\": " + json.dumps(playerHandAfter) + ",\n")

    for wind in winds:
        jsonString.append("\t\"" + wind + "Discards\": "  + json.dumps(finalDiscards[wind]) + ",\n")
        jsonString.append("\t\"" + wind + "Calls\": "  + json.dumps(finalCalls[wind]) + ",\n")

    doraInd = [tileDict[x] for x in log[2][0:(1+numOfKans)]]
    jsonString.append("\t\"doraInd\": "  + json.dumps(doraInd) + ",\n")

    bestDiscards = []
    bestDiscardsEV = []
    bestDiscardsFromEntry = data['kyokus'][kyoku]['entries'][entryNum]['details'][0:5]
    for bestDiscard in bestDiscardsFromEntry:
        actualDiscard = 0
        if bestDiscard['moves'][0]['type'] == "reach":
            discardTile = bestDiscard['moves'][1]['pai']
            if discardTile in tileDict.keys():
                discardTile = tileDict[discardTile]
            actualDiscard = "r" + discardTile
        else:
            discardTile = bestDiscard['moves'][0]['pai']
            if discardTile in tileDict.keys():
                discardTile = tileDict[discardTile]
            actualDiscard = discardTile
        bestDiscards.append(actualDiscard)
        bestDiscardsEV.append(round(bestDiscard['review']['pt_exp_total'], 4))

    jsonString.append("\t\"bestDiscards\": "  + json.dumps(bestDiscards) + ",\n")
    jsonString.append("\t\"evs\": "  + str(bestDiscardsEV) + "\n")
    jsonString.append("}")

    return jsonString

def getNumOfRounds(data):
    return len(data['kyokus']) - 1

def getNumOfTurns(data, kyoku):
    return data['kyokus'][kyoku]['entries'][-1]['junme']

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("filepath", type=str, help="filepath to akochan file")
    args = parser.parse_args()
    filepath = args.filepath
    data = 0
    try:
        file = open(filepath,encoding='utf-8')
        data = json.load(file)
    except:
        sys.exit("Process exited with error code 1: file not loaded")
    finally:
        file.close()

    #print(data)
    numOfRounds = getNumOfRounds(data)
    kyoku = input("Enter round number (0 - " + str(numOfRounds) + "): ")
    try:
        kyoku = int(kyoku)
    except:
        kyoku = -1
    while kyoku < 0 or kyoku > numOfRounds:
        kyoku = input("Please enter round number (0 - " + str(numOfRounds) + "): ")
        try:
            kyoku = int(kyoku)
        except:
            kyoku = -1

    numOfTurns = getNumOfTurns(data, kyoku)
    turn = input("Enter turn number (4 - " + str(numOfTurns) + "): ")
    try:
        turn = int(turn)
    except:
        turn = -1
    while turn < 4 or turn > numOfTurns:
        turn = input("Please enter turn number (4 - " + str(numOfTurns) + "): ")
        try:
            turn = int(turn)
        except:
            turn = -1

    name = input("Enter wwyd puzzle name: ")

    jsonFileContents = writeWWYDBotJson(data, kyoku, turn, name)
    writeFile = open(name + ".json", "w")
    for line in jsonFileContents:
        writeFile.write(line)

