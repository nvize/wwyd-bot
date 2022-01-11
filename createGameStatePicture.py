from PIL import Image
import json
import os
import base64
from io import BytesIO
import sys

tile_images = Image.open('mahjong_tiles/tiles.png')
xsize, ysize = tile_images.size
tile_width = xsize // 10
tile_height = ysize // 4
tile_names = ['1m','2m','3m','4m','5m','6m','7m','8m','9m','0m',
              '1p','2p','3p','4p','5p','6p','7p','8p','9p','0p',
              '1s','2s','3s','4s','5s','6s','7s','8s','9s','0s',
              '1z','2z','3z','4z','5z','6z','7z']

tileDict = {}
for index, name in enumerate(tile_names):
    tileDict[name] = tile_images.crop(((index % 10) * tile_width, (index // 10) * tile_height, 
                                      (index % 10 + 1) * tile_width, (index // 10 + 1) * tile_height))

def createGameStatePicture(filePath):
    gameFile = open(filePath)
    game = json.load(gameFile)
    
    hand = game['hand']
    handPic = Image.new("RGBA", (tile_width * 14, tile_height), (0, 0, 0, 0))
    
    for index, tile in enumerate(hand):
        region = (index*tile_width, 0, (index+1)*tile_width, tile_height)
        handPic.paste(tileDict[tile], region)
        
    outputBuffer = BytesIO()
    handPic.save(outputBuffer, format='PNG')
    bgBase64Data = outputBuffer.getvalue()
    
    return base64.b64encode(bgBase64Data).decode()

a = 0
#a = 'akochans/akochan-1.json' #testing line
try:
  a = sys.argv[1]
except:
  print("DATA_MISSING")

base64image = createGameStatePicture(a)
    
print(base64image)
sys.stdout.flush()