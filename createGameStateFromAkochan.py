# implelemt skipping logic

import argparse
import json
from operator import contains
import sys

# these arrays are used to translate from tenhou / mjai format to 'standard' format
tenhouTiles = [11, 12, 13, 14, 15, 16, 17, 18, 19, 51, 
               21, 22, 23, 24, 25, 26, 27, 28, 29, 52, 
               31, 32, 33, 34, 35, 36, 37, 38, 39, 53, 
               41, 42, 43, 44, 45, 46, 47, 
               "E", "S", "W", "N", "P", "F", "C",
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

    # determine point values at a round
    startingPoints = [25000, 25000, 25000, 25000]
    roundPointsIndex = 0
    while roundPointsIndex < kyoku:
        player = 0
        for delta in data['kyokus'][roundPointsIndex]['end_status'][0]['deltas']:
            startingPoints[player] = startingPoints[player] + delta
            player = player + 1
        roundPointsIndex = roundPointsIndex + 1
    jsonString.append("\t\"points\": "  + str(startingPoints) + ",\n")

    # determine entry number in json file. if target player chi/pon this turn, take highest turn less than target turn
    found = False
    entryNum = -1
    for index, entry in enumerate(data['kyokus'][kyoku]['entries']):
        if int(entry['junme']) < turn:
            entryNum = index
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

    numOfKans = 0 # determines number of dora indicators
    numOfKansOfPersonBefore = 0 # current logic stops based on number of discards of wind before. ankan counts as a discard, but doesn't advance the wind
    currDiscardWindNum = 0
    posOffset = 0
    if playerWind == "east":
        posOffset = -1 # because east goes first
    while numOfDiscards[winds[(playerWindNum - 1) % 4]] < turn + posOffset + numOfKansOfPersonBefore:

        currDiscardWind = winds[currDiscardWindNum]
        currDiscard = discards[currDiscardWind][numOfDiscards[currDiscardWind]]

        isRiichi = False
        if isinstance(currDiscard, str) and currDiscard.startswith("r"):
            isRiichi = True
            currDiscard = int(currDiscard[1:])

        if currDiscard == 60: # tsumogiri
            currDiscard = draws[currDiscardWind][numOfDiscards[currDiscardWind]]

        # check draw arrays for other winds to determine if tile was called
        discardWasCalled = False
        for wind in winds:
            if not wind == currDiscardWind and isinstance(draws[wind][numOfDiscards[wind]],str) and str(currDiscard) in draws[wind][numOfDiscards[wind]]:
                replacedTileCall = draws[wind][numOfDiscards[wind]]
                if(replacedTileCall[0] == "c"):
                    chiiTileCall = "c"
                    for i in range(1, len(replacedTileCall), 2):
                        chiiTileCall = chiiTileCall + tileDict[int(replacedTileCall[i] + replacedTileCall[i + 1])]
                    replacedTileCall = chiiTileCall
                else:
                    #replacedTileCall = draws[wind][numOfDiscards[wind]].replace(draws[wind][numOfDiscards[wind]][-2:], tileDict[int(draws[wind][numOfDiscards[wind]][-2:])])

                    #following code cuts call in half at alpha char indicating type of call, replacing both halves with 'standard' formatting for tiles
                    #you'll see this reused in other parts of this file, consider functionizing it
                    callTypeIndex = replacedTileCall.find(next(filter(str.isalpha, replacedTileCall)))
                    firstHalf = replacedTileCall[0:callTypeIndex]
                    secondHalf = replacedTileCall[callTypeIndex+1:]
                    firstHalfReplaced = ""
                    secondHalfReplaced = ""
                    for i in range(0, len(firstHalf), 2):
                        firstHalfReplaced = firstHalfReplaced + tileDict[int(firstHalf[i] + firstHalf[i + 1])]
                    for i in range(0, len(secondHalf), 2):
                        secondHalfReplaced = secondHalfReplaced + tileDict[int(secondHalf[i] + secondHalf[i + 1])]
                    finalTileCall = firstHalfReplaced + replacedTileCall[callTypeIndex] + secondHalfReplaced
                    replacedTileCall = finalTileCall
                    #??? how do i do this (ponning counts as a turn if east??? idk)
                    if wind == playerWind:
                        numOfKansOfPersonBefore = numOfKansOfPersonBefore-1
                finalCalls[wind].append(replacedTileCall)
                discardWasCalled = True
                currDiscardWindNum = winds.index(wind)
                if len(draws[wind][numOfDiscards[wind]]) > 8: # called kan (daiminkan)
                    numOfKans = numOfKans + 1
                    numOfDiscards[wind] = numOfDiscards[wind] + 1
                    
        # added kan logic (shouminkan)
        if isinstance(currDiscard,str) and len(currDiscard) > 8 and contains(currDiscard, 'k'):
            discardWasCalled = True
            kanTile = tileDict[int(currDiscard[-2:])]
            kanTiles = kanTile
            if kanTile[0] == '5': # need this since red 5's and normal 5's are functionally the same
                kanTiles = [kanTile, '0' + kanTile[1]]
            if kanTile[0] == '0':
                kanTiles = [kanTile, '5' + kanTile[1]]
            
            # turn this into a function!
            callTypeIndex = currDiscard.find(next(filter(str.isalpha, currDiscard)))
            firstHalf = currDiscard[0:callTypeIndex]
            secondHalf = currDiscard[callTypeIndex+1:]
            firstHalfReplaced = ""
            secondHalfReplaced = ""
            for i in range(0, len(firstHalf), 2):
                firstHalfReplaced = firstHalfReplaced + tileDict[int(firstHalf[i] + firstHalf[i + 1])]
            for i in range(0, len(secondHalf), 2):
                secondHalfReplaced = secondHalfReplaced + tileDict[int(secondHalf[i] + secondHalf[i + 1])]
            finalTileCall = firstHalfReplaced + currDiscard[callTypeIndex] + secondHalfReplaced
            replacedTileCall = finalTileCall
            
            addedKanFinalCalls = []
            for tileCall in finalCalls[currDiscardWind]:
                if any(kTile in tileCall for kTile in kanTiles):
                    addedKanFinalCalls.append(replacedTileCall)
                else:
                    addedKanFinalCalls.append(tileCall)
            finalCalls[currDiscardWind] = addedKanFinalCalls
            if currDiscardWind != playerWind: # added kan in player turn doesn't flip dora indicator until discard occurs
                numOfKans = numOfKans + 1

        #closed kan logic
        if isinstance(currDiscard,str) and len(currDiscard) > 8 and contains(currDiscard, 'a'):
            discardWasCalled = True

            #functionalize!
            callTypeIndex = currDiscard.find(next(filter(str.isalpha, currDiscard)))
            firstHalf = currDiscard[0:callTypeIndex]
            secondHalf = currDiscard[callTypeIndex+1:]
            firstHalfReplaced = ""
            secondHalfReplaced = ""
            for i in range(0, len(firstHalf), 2):
                firstHalfReplaced = firstHalfReplaced + tileDict[int(firstHalf[i] + firstHalf[i + 1])]
            for i in range(0, len(secondHalf), 2):
                secondHalfReplaced = secondHalfReplaced + tileDict[int(secondHalf[i] + secondHalf[i + 1])]
            finalTileCall = firstHalfReplaced + currDiscard[callTypeIndex] + secondHalfReplaced
            
            finalCalls[currDiscardWind].append(finalTileCall)
            numOfKans = numOfKans + 1
            if (winds.index(currDiscardWind) + 1) % 4 == playerWindNum:
                numOfKansOfPersonBefore = numOfKansOfPersonBefore + 1
            if currDiscardWind == playerWind:
                numOfKansOfPersonBefore = numOfKansOfPersonBefore - 1

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

    playerHandBefore = data['kyokus'][kyoku]['entries'][entryNum]['state']['tehai'] # tiles in hand
    playerHandAfter = []
    if data['kyokus'][kyoku]['entries'][entryNum]['junme'] == turn:
        for tile in playerHandBefore:
            if tile in tileDict.keys():
                newTile = tileDict[tile]
                playerHandAfter.append(newTile)
            else:
                playerHandAfter.append(tile)
    else: # need to remove tiles from hand if the player made a call this turn
        for tile in playerHandBefore:
            if tile not in data['kyokus'][kyoku]['entries'][entryNum]['actual'][0]['consumed']:
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

    potentialDiscards = []
    skipped = False
    potentialDiscardsFromEntry = data['kyokus'][kyoku]['entries'][entryNum]['details'] # potential discards
    for potentialDiscard in potentialDiscardsFromEntry:
        skipped = False
        actualPotentialDiscard = 0
        if potentialDiscard['moves'][0]['type'] == "ankan":
            discardTile = potentialDiscard['moves'][0]['consumed'][0]
            if discardTile in tileDict.keys():
                discardTile = tileDict[discardTile]
            actualPotentialDiscard = "k" + discardTile
        elif potentialDiscard['moves'][0]['type'] == "reach":
            discardTile = potentialDiscard['moves'][1]['pai']
            if discardTile in tileDict.keys():
                discardTile = tileDict[discardTile]
            actualPotentialDiscard = "r" + discardTile
        elif potentialDiscard['moves'][0]['type'] == "chi" or potentialDiscard['moves'][0]['type'] == "pon":
            discardTile = potentialDiscard['moves'][1]['pai']
            if discardTile in tileDict.keys():
                discardTile = tileDict[discardTile]
            actualPotentialDiscard = discardTile
        elif potentialDiscard['moves'][0]['type'] == "none":
            skipped = True
        else:
            discardTile = potentialDiscard['moves'][0]['pai']
            if discardTile in tileDict.keys():
                discardTile = tileDict[discardTile]
            actualPotentialDiscard = discardTile
        if not skipped:
            potentialDiscards.append(actualPotentialDiscard)

    potentialDiscards.sort(key=lambda x: x[-2])
    potentialDiscards.sort(key=lambda x: x[-1])
    jsonString.append("\t\"potentialDiscards\": "  + json.dumps(potentialDiscards) + ",\n")

    bestDiscards = []
    bestDiscardsEV = []
    skipped = False
    bestDiscardsFromEntry = data['kyokus'][kyoku]['entries'][entryNum]['details'][0:5] # top 5 discards
    for bestDiscard in bestDiscardsFromEntry:
        skipped = False
        actualDiscard = 0
        if bestDiscard['moves'][0]['type'] == "ankan":
            discardTile = bestDiscard['moves'][0]['consumed'][0]
            if discardTile in tileDict.keys():
                discardTile = tileDict[discardTile]
            actualDiscard = "k" + discardTile
        elif bestDiscard['moves'][0]['type'] == "reach":
            discardTile = bestDiscard['moves'][1]['pai']
            if discardTile in tileDict.keys():
                discardTile = tileDict[discardTile]
            actualDiscard = "r" + discardTile
        elif bestDiscard['moves'][0]['type'] == "chi" or bestDiscard['moves'][0]['type'] == "pon":
            discardTile = bestDiscard['moves'][1]['pai']
            if discardTile in tileDict.keys():
                discardTile = tileDict[discardTile]
            actualDiscard = discardTile
        elif bestDiscard['moves'][0]['type'] == "none":
            skipped = True
        else:
            discardTile = bestDiscard['moves'][0]['pai']
            if discardTile in tileDict.keys():
                discardTile = tileDict[discardTile]
            actualDiscard = discardTile
        if not skipped:
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

