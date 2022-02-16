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
    tilesInRow1Calls = 0
    tilesInRow2Calls = 0
    for call in tileCalls:
        if len(call) > 7 and tilesInRow1Calls < 6:
            tilesInRow1Calls += 4
        elif tilesInRow1Calls < 6:
            tilesInRow1Calls += 3
        elif len(call) > 7:
            tilesInRow2Calls += 4
        else:
            tilesInRow2Calls += 3

    callImage = Image.new("RGBA", (max([tilesInRow1Calls, tilesInRow2Calls]) * tile_width + 2 * (tile_height - tile_width), tile_width * 4), (0, 0, 0, 0))

    leftSide = 0
    topSide = 0
    callIndex = 0
    for call in tileCalls:
        index = 0
        if callIndex == 2:
            topSide = tile_width * 2
            leftSide = 0
        while index < len(call):
            if call[index] in ["a", "c", "m", "k", "p"]:
                if call[index] == "a": # shouminkan (2 sideways tiles stacked vertically)
                    tile = tileDict[call[index+1:index+3]]
                    rotatedTile = tile.rotate(270,expand=True)
                    addedKan = Image.new("RGBA", (tile_height, tile_width * 2), (0, 0, 0, 0))
                    addedKan.paste(rotatedTile, (0, 0, tile_height, tile_width))
                    addedKan.paste(rotatedTile, (0, tile_width, tile_height, tile_width * 2))
                    callImage.paste(addedKan, (leftSide, topSide, leftSide + tile_height, topSide + tile_width * 2))
                    index = index + 5
                    leftSide = leftSide + tile_height
                elif call[index] in ["c", "m", "p"] and not index == 6: # pon, chii, daiminkan
                    tile = tileDict[call[index+1:index+3]]
                    rotatedTile = tile.rotate(270,expand=True)
                    callImage.paste(rotatedTile, (leftSide, topSide + tile_width, leftSide + tile_height, topSide + tile_width * 2))
                    index = index + 3
                    leftSide = leftSide + tile_height
                elif call[index] == "k" and index == 6: # ankan
                    callImage.paste(tileDict["ct"], (leftSide, topSide + tile_width * 2 - tile_height, leftSide + tile_width, topSide + tile_width * 2))
                    callImage.paste(tileDict["ct"], (0, topSide + tile_height, tile_width, topSide + tile_height * 2))
                    index = index + 3
                    leftSide = leftSide + tile_width
            else: # noncalled tile
                callImage.paste(tileDict[call[index:index+2]], (leftSide, topSide + tile_width * 2 - tile_height, leftSide + tile_width, topSide + tile_width * 2))
                index = index + 2
                leftSide = leftSide + tile_width
        callIndex = callIndex + 1

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

def createGameStatePictureFunc(game):
    tilePadding = math.floor(tile_height*0.2)
    boardImage = Image.new("RGBA", (8*tile_height + 11*tile_width + 3*tilePadding, 8*tile_height + 11*tile_width + 3*tilePadding), (0, 0, 0, 0))

    winds = ["east", "south", "west", "north"]

    handImage = createTileGroup(game["hand"], len(game["hand"]))

    discardImages = {}
    callImages = {}
    for wind in winds:
        discardImages[wind] = createTileGroup(game[wind + "Discards"], 6)
        callImages[wind] = createTileCalls(game[wind + "Calls"])

    discardsLeftSide = 4*tile_width + 4*tile_height + 2*tilePadding
    discardsTopSide = 7*tile_width + 4*tile_height + 2*tilePadding
    for wind in winds:
        boardImage.paste(discardImages[wind], (discardsLeftSide, discardsTopSide, discardsLeftSide+discardImages[wind].size[0], discardsTopSide+discardImages[wind].size[1]))
        numOfRows = max([-(len(game[wind + "Discards"]) // -6), 2])
        boardImage.paste(callImages[wind], (math.floor((boardImage.size[0] - callImages[wind].size[0])/2), discardsTopSide + numOfRows*tile_height + tilePadding, math.floor((boardImage.size[0] - callImages[wind].size[0])/2) + callImages[wind].size[0], discardsTopSide + numOfRows*tile_height + tilePadding + callImages[wind].size[1]))
        boardImage = boardImage.rotate(270)

    boardLeft = ((4-(max([-(len(game["northDiscards"]) // -6), 2]))) * tile_height) + ((2-(-(len(game["northCalls"]) // -2))) * (tile_width * 2))
    boardBottom = boardImage.size[1] - ((4-(max([-(len(game["eastDiscards"]) // -6), 2]))) * tile_height) - ((2-(-(len(game["eastCalls"]) // -2))) * (tile_width * 2))
    boardRight = boardImage.size[0] - ((4-(max([-(len(game["southDiscards"]) // -6), 2]))) * tile_height) - ((2-(-(len(game["southCalls"]) // -2))) * (tile_width * 2))
    boardTop = ((4-(max([-(len(game["westDiscards"]) // -6), 2]))) * tile_height) + ((2-(-(len(game["westCalls"]) // -2))) * (tile_width * 2))

    boardLeft = min([boardLeft, (boardImage.size[0] - callImages["east"].size[0])/2, (boardImage.size[0] - callImages["west"].size[0])/2])
    boardRight = max([boardRight, (boardImage.size[0] + callImages["east"].size[0])/2, (boardImage.size[0] + callImages["west"].size[0])/2])
    boardBottom = max([boardBottom, (boardImage.size[1] + callImages["south"].size[0])/2, (boardImage.size[1] + callImages["north"].size[0])/2])
    boardTop = min([boardTop, (boardImage.size[1] - callImages["south"].size[0])/2, (boardImage.size[1] - callImages["north"].size[0])/2])

    boardImage = boardImage.crop((boardLeft, boardTop, boardRight , boardBottom))

    if game["seat"] == "south":
        boardImage = boardImage.rotate(270,expand=True)
    elif game["seat"] == "west":
        boardImage = boardImage.rotate(180,expand=True)
    elif game["seat"] == "north":
        boardImage = boardImage.rotate(90,expand=True)

    gameImage = Image.new("RGBA", (max([boardImage.size[0], handImage.size[0]]), boardImage.size[1]+tile_height+tilePadding), (0, 0, 0, 0))
    gameImage.paste(boardImage, (math.floor((gameImage.size[0]-boardImage.size[0])/2), 0, math.floor((gameImage.size[0]+boardImage.size[0])/2), boardImage.size[1]))
    gameImage.paste(handImage, (math.floor((gameImage.size[0] - handImage.size[0])/2), gameImage.size[1]-handImage.size[1], math.floor((gameImage.size[0] - handImage.size[0])/2) + handImage.size[0], gameImage.size[1]))
    base64image = convertToBase64(gameImage)
    return base64image

if __name__ == "__main__":

    test = 0

    filePath = 0
    stringOrFilepath = 'filepath'

    if test == 0:
        try:
            filePath = sys.argv[1]
        except:
            print("MISSING_FILE! mark for testing?")
        try:
            stringOrFilepath = sys.argv[2]
        except:
            print("String/filepath marker not set!")
    else:
        filePath = 'akochans/lol.json' #testing line

    game = {}
    if stringOrFilepath == 'filepath':
        gameFile = open(filePath)
        game = json.load(gameFile)
    else:
        game = filePath

    base64image = createGameStatePicture(game)

    print(base64image)
    sys.stdout.flush()