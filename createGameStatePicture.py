from PIL import Image, ImageDraw, ImageFont
import json
import base64
import math
from io import BytesIO
import sys

tile_images = Image.open('mahjong_tiles/tiles.png')
xsize, ysize = tile_images.size
tile_width = xsize // 10
tile_height = ysize // 4
tile_names = ['1m','2m','3m','4m','5m','6m','7m','8m','9m','0m',
              '1p','2p','3p','4p','5p','6p','7p','8p','9p','0p',
              '1s','2s','3s','4s','5s','6s','7s','8s','9s','0s',
              '1z','2z','3z','4z','5z','6z','7z','ct']

tileDict = {}
for index, name in enumerate(tile_names):
    tileDict[name] = tile_images.crop(((index % 10) * tile_width, (index // 10) * tile_height, 
                                      (index % 10 + 1) * tile_width, (index // 10 + 1) * tile_height))

def convertToBase64(image):
    outputBuffer = BytesIO()
    image.save(outputBuffer, format='PNG')
    bgBase64Data = outputBuffer.getvalue()
    
    return base64.b64encode(bgBase64Data).decode()

def createTileCalls(tileCalls):
    tilesInCalls = 0
    for call in tileCalls:
        if len(call) > 7:
            tilesInCalls += 4
        else:
            tilesInCalls += 3
    callImage = Image.new("RGBA", (tilesInCalls * tile_width + len(tileCalls) * (tile_height - tile_width), tile_width * 2), (0, 0, 0, 0))

    leftSide = 0
    for call in tileCalls:
        index = 0
        while index < len(call):
            if call[index] in ["a", "c", "k", "p"]:
                if call[index] == "a": # shouminkan (2 sideways tiles stacked vertically)
                    tile = tileDict[call[index+1:index+3]]
                    rotatedTile = tile.rotate(270,expand=True)
                    addedKan = Image.new("RGBA", (tile_height, tile_width * 2), (0, 0, 0, 0))
                    addedKan.paste(rotatedTile, (0, 0, tile_height, tile_width))
                    addedKan.paste(rotatedTile, (0, tile_width, tile_height, tile_width * 2))
                    callImage.paste(addedKan, (leftSide, 0, leftSide + tile_height, tile_width * 2))
                    index = index + 5
                    leftSide = leftSide + tile_height
                elif call[index] in ["c", "k", "p"] and not index == 6: # pon, chii, daiminkan
                    tile = tileDict[call[index+1:index+3]]
                    rotatedTile = tile.rotate(270,expand=True)
                    callImage.paste(rotatedTile, (leftSide, tile_width, leftSide + tile_height, tile_width * 2))
                    index = index + 3
                    leftSide = leftSide + tile_height
                elif call[index] == "k" and index == 6: # ankan
                    callImage.paste(tileDict["ct"], (leftSide, tile_width * 2 - tile_height, leftSide + tile_width, tile_width * 2))
                    callImage.paste(tileDict["ct"], (0, tile_height, tile_width, tile_height * 2))
                    index = index + 3
                    leftSide = leftSide + tile_width
            else: # noncalled tile
                callImage.paste(tileDict[call[index:index+2]], (leftSide, tile_width * 2 - tile_height, leftSide + tile_width, tile_width * 2))
                index = index + 2
                leftSide = leftSide + tile_width

    return callImage

def createTileGroup(tiles, rowSize):
    numOfRows = -(len(tiles) // -rowSize)
    tilePic = Image.new("RGBA", (tile_width * rowSize + (tile_height - tile_width), tile_height * numOfRows), (0, 0, 0, 0))
    
    riichiOffset = 0
    for index, tile in enumerate(tiles):
        if tile[0] == 'r':
            riichiTile = tileDict[tile[1:3]]
            rotatedTile = riichiTile.rotate(270,expand=True)
            tilePic.paste(rotatedTile, ((index % rowSize) * tile_width, (index // rowSize) * tile_height + (tile_height - tile_width), 
                                      (index % rowSize + 1) * tile_width + (tile_height - tile_width), (index // rowSize + 1) * tile_height))
            riichiOffset =  tile_height - tile_width
        else:
            if index % rowSize == 0:
                riichiOffset = 0
            tilePic.paste(tileDict[tile], ((index % rowSize) * tile_width + riichiOffset, (index // rowSize) * tile_height, 
                                      (index % rowSize + 1) * tile_width + riichiOffset, (index // rowSize + 1) * tile_height))
        
    return tilePic

filePath = 0
#filePath = 'akochans/akochan-1.json' #testing line
try:
    filePath = sys.argv[1]
except:
    print("MISSING_FILE")

gameFile = open(filePath)
game = json.load(gameFile)

tilePadding = math.floor(tile_height*0.2)
gameImage = Image.new("RGBA", (tilePadding+10*tile_height+6*tile_width, 2*tilePadding+11*tile_height+6*tile_width), (0, 0, 0, 0))
boardImage = Image.new("RGBA", (tilePadding+10*tile_height+6*tile_width, tilePadding+10*tile_height+6*tile_width), (0, 0, 0, 0))

handImage = createTileGroup(game["hand"], 14)
eastDiscardsImage = createTileGroup(game["eastDiscards"], 6)
eastCallsImage = createTileCalls(game["eastCalls"])
southDiscardsImage = createTileGroup(game["southDiscards"], 6)
southCallsImage = createTileCalls(game["southCalls"])
westDiscardsImage = createTileGroup(game["westDiscards"], 6)
westCallsImage = createTileCalls(game["westCalls"])
northDiscardsImage = createTileGroup(game["northDiscards"], 6)
northCallsImage = createTileCalls(game["northCalls"])

tilePadding = math.floor(tile_height*0.2)
boardImage.paste(eastDiscardsImage, (tilePadding+6*tile_height, tilePadding+4*tile_height+6*tile_width, tilePadding+6*tile_height+eastDiscardsImage.size[0], tilePadding+4*tile_height+6*tile_width+eastDiscardsImage.size[1]))
boardImage.paste(eastCallsImage, (math.floor((boardImage.size[0] - eastCallsImage.size[0])/2), 2*tilePadding+8*tile_height+6*tile_width, math.floor((boardImage.size[0] - eastCallsImage.size[0])/2) + eastCallsImage.size[0], 2*tilePadding+8*tile_height+6*tile_width + eastCallsImage.size[1]))
boardImage = boardImage.rotate(90)
boardImage.paste(southDiscardsImage, (tilePadding+6*tile_height, tilePadding+4*tile_height+6*tile_width, tilePadding+6*tile_height+southDiscardsImage.size[0], tilePadding+4*tile_height+6*tile_width+southDiscardsImage.size[1]))
boardImage.paste(southCallsImage, (math.floor((boardImage.size[0] - southCallsImage.size[0])/2), 2*tilePadding+8*tile_height+6*tile_width, math.floor((boardImage.size[0] - southCallsImage.size[0])/2) + southCallsImage.size[0], 2*tilePadding+8*tile_height+6*tile_width + southCallsImage.size[1]))
boardImage = boardImage.rotate(90)
boardImage.paste(westDiscardsImage, (tilePadding+6*tile_height, tilePadding+4*tile_height+6*tile_width, tilePadding+6*tile_height+westDiscardsImage.size[0], tilePadding+4*tile_height+6*tile_width+westDiscardsImage.size[1]))
boardImage.paste(westCallsImage, (math.floor((boardImage.size[0] - westCallsImage.size[0])/2), 2*tilePadding+8*tile_height+6*tile_width, math.floor((boardImage.size[0] - westCallsImage.size[0])/2) + westCallsImage.size[0], 2*tilePadding+8*tile_height+6*tile_width + westCallsImage.size[1]))
boardImage = boardImage.rotate(90)
boardImage.paste(northDiscardsImage, (tilePadding+6*tile_height, tilePadding+4*tile_height+6*tile_width, tilePadding+6*tile_height+northDiscardsImage.size[0], tilePadding+4*tile_height+6*tile_width+northDiscardsImage.size[1]))
boardImage.paste(northCallsImage, (math.floor((boardImage.size[0] - northCallsImage.size[0])/2), 2*tilePadding+8*tile_height+6*tile_width, math.floor((boardImage.size[0] - northCallsImage.size[0])/2) + northCallsImage.size[0], 2*tilePadding+8*tile_height+6*tile_width + northCallsImage.size[1]))

if game["seat"] == "east":
    boardImage = boardImage.rotate(90)
elif game["seat"] == "south":
    boardImage = boardImage.rotate(180)
elif game["seat"] == "west":
    boardImage = boardImage.rotate(270)

gameImage.paste(boardImage, (0, 0, boardImage.size[0], boardImage.size[1]))
gameImage.paste(handImage, (math.floor((boardImage.size[0] - handImage.size[0])/2), gameImage.size[1]-handImage.size[1], math.floor((boardImage.size[0] - handImage.size[0])/2) + handImage.size[0], gameImage.size[1]))
base64image = convertToBase64(gameImage)

print(base64image)
sys.stdout.flush()