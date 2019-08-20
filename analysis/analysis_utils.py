import math
import re

tenhou_tile_to_array_index_lookup = [
     1,  2,  3,  4,  5,  6,  7,  8,  9,
    11, 12, 13, 14, 15, 16, 17, 18, 19,
    21, 22, 23, 24, 25, 26, 27, 28, 29,
    31, 32, 33, 34, 35, 36, 37
]

def convertTile(tile):
    return tenhou_tile_to_array_index_lookup[math.floor(int(tile) / 4)]

def convertHand(hand):
    convertedHand = []
    for i in range(38):
        convertedHand.append(hand.count(i))
    return convertedHand

def convertHai(hai):
    converted = list(map(convertTile, hai.split(',')))
    return convertHand(converted)

def getTilesFromCall(call):
    meldInt = int(call)
    meldBinary = format(meldInt, "016b")

    if meldBinary[len(meldBinary) - 3] == '1':
        # Chii
        tile = meldBinary[0:6]
        tile = int(tile, 2)
        order = tile % 3
        tile = math.floor(tile / 3)
        tile = 9 * math.floor(tile / 7) + (tile % 7)
        tile = convertTile(tile * 4)

        if order == 0:
            return [tile, tile + 1, tile + 2]
        
        if order == 1:
            return [tile + 1, tile, tile + 2]

        return [tile + 2, tile, tile + 1]
    
    elif meldBinary[len(meldBinary) - 4] == '1':
        # Pon
        tile = meldBinary[0:7]
        tile = int(tile, 2)
        tile = math.floor(tile / 3)
        tile = convertTile(tile * 4)

        return [tile, tile, tile]
    
    elif meldBinary[len(meldBinary) - 5] == '1':
        # Added kan
        tile = meldBinary[0:7]
        tile = int(tile, 2)
        tile = math.floor(tile / 3)
        tile = convertTile(tile * 4)

        return [tile]
    
    elif meldBinary[len(meldBinary) - 6] == '1':
        # Nuki
        return [34]
    
    else:
        # Kan
        tile = meldBinary[0:8]
        tile = int(tile, 2)
        tile = math.floor(tile / 4)
        tile = convertTile(tile * 4)
        return [tile, tile, tile, tile]

def GetWhoTileWasCalledFrom(call):
    meldInt = int(call.attrib["m"])
    meldBinary = format(meldInt, "016b")
    return int(meldBinary[-2:], 2)

round_names = [
    "East 1", "East 2", "East 3", "East 4",
    "South 1", "South 2", "South 3", "South 4",
    "West 1", "West 2", "West 3", "West 4",
    "North 1", "North 2", "North 3", "North 4"
]

def GetRoundName(init):
    seed = init.attrib["seed"].split(",")
    return "%s-%s" % (round_names[int(seed[0])], seed[1])

seats_by_oya = [
    [ "East", "South", "West", "North" ],
    [ "North", "East", "South", "West" ],
    [ "West", "North", "East", "South" ],
    [ "South", "West", "North", "East" ]
]

def CheckSeat(who, oya):
    return seats_by_oya[int(oya)][int(who)]

def GetPlacements(ten, starting_oya):
    points = list(map(int, ten.split(",")))
    # For tiebreaking
    points[0] -= (4 - starting_oya) % 4
    points[1] -= (5 - starting_oya) % 4
    points[2] -= (6 - starting_oya) % 4
    points[3] -= (7 - starting_oya) % 4
    ordered_points = points.copy()
    ordered_points.sort(reverse=True)

    return [
        ordered_points.index(points[0]),
        ordered_points.index(points[1]),
        ordered_points.index(points[2]),
        ordered_points.index(points[3])
    ]