import random
import createGameStateFromAkochan
import createGameStatePicture
import json
import sys

test = 1

filePath = 0

if test == 0:
    try:
        filePath = sys.argv[1]
    except:
        print("MISSING_FILE! mark for testing?")
else:
    filePath = './2_2_2022_Silver_Room_East_akochan.json' #testing line

dataFile = open(filePath,encoding='utf-8')
akochanData = json.load(dataFile)

numOfRounds = createGameStateFromAkochan.getNumOfRounds(akochanData)
round = random.randint(0, numOfRounds)
numOfTurns = createGameStateFromAkochan.getNumOfTurns(akochanData, round)
turn = random.randint(3, numOfTurns)

gameStateData = createGameStateFromAkochan.writeWWYDBotJson(akochanData, round, turn, "rand-akochan-wwyd")
jsonLine = ""
for line in gameStateData:
    jsonLine = jsonLine + line
game = json.loads(jsonLine)

name = str(random.randint(1000000000, 9999999999))
writeFile = open(name + ".json", "w")
writeFile.write(jsonLine)
print(name + " round:" + str(round) + " turn:" + str(turn))

base64image = createGameStatePicture.createGameStatePictureFunc(game)

print("ok")
#print(base64image)
sys.stdout.flush()