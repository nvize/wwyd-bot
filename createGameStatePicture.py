from PIL import Image
import json
import os
import base64
from io import BytesIO
import sys

tile_images = 'mahjong_tiles/'

tileDict = {}
for filename in os.listdir(tile_images):
    tileDict[filename[0:2]] = Image.open('mahjong_tiles/' + filename)

def createGameStatePicture(filePath):
    gameFile = open(filePath)
    game = json.load(gameFile)
    
    #tileDict = {}
    #for filename in os.listdir(tile_images):
    #    tileDict[filename[0:2]] = Image.open('mahjong_tiles/' + filename)
    
    hand = game['hand']
    handPic = Image.new("RGBA", (500, 44), (0, 0, 0, 0))
    
    for index, tile in enumerate(hand):
        region = (index*30, 0, (index+1)*30, 44)
        handPic.paste(tileDict[tile], region)
        
    outputBuffer = BytesIO()
    handPic.save(outputBuffer, format='PNG')
    bgBase64Data = outputBuffer.getvalue()
    
    return base64.b64encode(bgBase64Data).decode()

#a = 0
a = 'akochans/akochan-1.json'
#try:
#  a = sys.argv[1]
#except:
#  print("DATA_MISSING")

base64image = createGameStatePicture(a)
    
#print(base64image)
print(base64image)
sys.stdout.flush()