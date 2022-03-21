import random
import createGameStateFromAkochan
import createGameStatePicture
import json
import sys
import argparse

test = 0
noRoundOrTurnInput = 0
filePath = 0
kyoku = 0
turn = 0

parser = argparse.ArgumentParser()
parser.add_argument("filepath", type=str, help="filepath to akochan file")
parser.add_argument("kyoku", type=int, help="round/kyoku to use")
parser.add_argument("turn", type=int, help="turn to use")
args = parser.parse_args()

if test == 0:
    try:
        filePath = args.filepath
    except:
        print("MISSING_FILE! mark for testing?")
else:
    filePath = './2_2_2022_Silver_Room_East_akochan.json' #testing line

if noRoundOrTurnInput == 0:
    try:
        kyoku = args.kyoku
        turn = args.turn
    except:
        print("missing kyoku/turn numbers! turn off noRoundOrTurnInput?")

dataFile = open(filePath,encoding='utf-8')
akochanData = json.load(dataFile)

if noRoundOrTurnInput == 1:
    numOfRounds = createGameStateFromAkochan.getNumOfRounds(akochanData)
    kyoku = random.randint(0, numOfRounds)
    numOfTurns = createGameStateFromAkochan.getNumOfTurns(akochanData, kyoku)
    turn = random.randint(4, numOfTurns - 1)

#print("before: " + " round:" + str(kyoku) + " turn:" + str(turn))
gameStateData = createGameStateFromAkochan.writeWWYDBotJson(akochanData, kyoku, turn, "rand-akochan-wwyd")
jsonLine = ""
for line in gameStateData:
    jsonLine = jsonLine + line
game = json.loads(jsonLine)

writeToFile = 2

if writeToFile == 1:
    name = str(random.randint(1000000000, 9999999999))
    writeFile = open(name + ".json", "w")
    writeFile.write(jsonLine)
    print(name + " round:" + str(kyoku) + " turn:" + str(turn))
elif writeToFile == 2:
    writeFile = open("randWWYD.json", "w")
    writeFile.write(jsonLine)
base64image = createGameStatePicture.createGameStatePictureFunc(game)

printOut = 1
if printOut:
    print(base64image)
    sys.stdout.flush()
else:
    writeFile2 = open("picture.txt", "w")
    writeFile2.write(base64image)