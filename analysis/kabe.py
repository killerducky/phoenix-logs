from analysis_utils import convertTile, convertHai, getTilesFromCall, discards, draws, GetPreviousRealTag, GetNextRealTag
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter

class Kabe(LogAnalyzer):
    def __init__(self):
        self.counts = defaultdict(Counter)
        self.wins = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        riichis = log.findall("REACH")

        for riichi in riichis:
            if int(riichi.attrib["step"]) == 1:
                continue
            
            riichi_player = int(riichi.attrib["who"])
            riichi_discard = discards[riichi_player]
            discarded_tiles = [False] * 38
            visible_tiles = [0] * 38
            hands = [[0] * 38, [0] * 38, [0] * 38, [0] * 38]

            previous = GetPreviousRealTag(riichi)
            if previous.tag == "REACH":
                # there exists one broken replay in the dataset
                continue
            riichi_tile = convertTile(previous.tag[1:])
            visible_tiles[riichi_tile] += 1
            previous = GetPreviousRealTag(previous)

            # Calculate hands pre-riichi and visible tiles
            while previous is not None:
                if previous.tag == "DORA":
                    visible_tiles[convertTile(previous.attrib["hai"])] += 1
                    previous = GetPreviousRealTag(previous)
                    continue
                elif previous.tag[0] in discards:
                    tile = convertTile(previous.tag[1:])
                    visible_tiles[tile] += 1
                    hands[discards.index(previous.tag[0])][tile] -= 1
                    if previous.tag[0] == riichi_discard:
                        discarded_tiles[tile] = True
                elif previous.tag == "INIT":
                    indicator = convertTile(previous.attrib["seed"].split(",")[5])
                    visible_tiles[indicator] += 1
                    for i in range(4):
                        starting_hand = convertHai(previous.attrib["hai%d" % i])
                        for j in range(38):
                            hands[i][j] += starting_hand[j]
                    break
                elif previous.tag[0] in draws:
                    hands[draws.index(previous.tag[0])][convertTile(previous.tag[1:])] += 1
                elif previous.tag == "N":
                    who = int(previous.attrib["who"])
                    tiles = getTilesFromCall(previous.attrib["m"])
                    if len(tiles) == 3:
                        visible_tiles[tiles[1]] += 1
                        visible_tiles[tiles[2]] += 1
                        hands[who][tiles[1]] -= 1
                        hands[who][tiles[2]] -= 1
                    elif len(tiles) == 4:
                        visible_tiles[tiles[0]] = 4
                        hands[who][tiles[0]] = 0
                    elif len(tiles) == 1:
                        visible_tiles[tiles[0]] += 1
                        hands[who][tiles[0]] -= 1
                previous = GetPreviousRealTag(previous)
            
            # Look at post-riichi discards for danger
            next_element = GetNextRealTag(riichi)
            while next_element is not None:
                if next_element.tag == "DORA":
                    visible_tiles[convertTile(next_element.attrib["hai"])] += 1
                elif next_element.tag[0] == riichi_discard:
                    tile = convertTile(next_element.tag[1:])
                    visible_tiles[tile] += 1
                    if tile != riichi_tile:
                        discarded_tiles[tile] = True
                elif next_element.tag[0] in discards:
                    who = discards.index(next_element.tag[0])
                    tile = convertTile(next_element.tag[1:])
                    # Genbutsu is obviously safe and we're not worrying about honors
                    if discarded_tiles[tile] or tile > 30 or tile == riichi_tile:
                        visible_tiles[tile] += 1
                        hands[who][tile] -= 1
                        next_element = GetNextRealTag(next_element)
                        continue

                    suji_type = checkSuji(tile, discarded_tiles, riichi_tile)
                    visible = calculateVisibleTiles(tile, hands[who], visible_tiles, log_id)
                    key = "%s | %s" % (suji_type, visible)
                    live_suji = calculateLiveSuji(discarded_tiles, riichi_tile)
                    self.counts[key][live_suji] += 1

                    next_element = GetNextRealTag(next_element)
                    if next_element.tag == "AGARI":
                        if int(next_element.attrib["who"]) == riichi_player:
                            self.wins[key][live_suji] += 1
                        # check for double ron
                        else:
                            next_element = GetNextRealTag(next_element)
                            if next_element is not None and next_element.tag == "AGARI":
                                if int(next_element.attrib["who"]) == riichi_player:
                                    self.wins[key][live_suji] += 1
                        break

                    discarded_tiles[tile] = True
                    visible_tiles[tile] += 1
                    hands[who][tile] -= 1
                    continue
                elif next_element.tag[0] in draws:
                    tile = convertTile(next_element.tag[1:])
                    hands[draws.index(next_element.tag[0])][tile] += 1
                elif next_element.tag == "AGARI" or next_element.tag == "RYUUKYOKU":
                    break
                elif next_element.tag == "N":
                    who = int(next_element.attrib["who"])
                    tiles = getTilesFromCall(next_element.attrib["m"])
                    if len(tiles) == 3:
                        visible_tiles[tiles[1]] += 1
                        visible_tiles[tiles[2]] += 1
                        hands[who][tiles[1]] -= 1
                        hands[who][tiles[2]] -= 1
                    elif len(tiles) == 4:
                        visible_tiles[tiles[0]] = 4
                        hands[who][tiles[0]] = 0
                    elif len(tiles) == 1:
                        visible_tiles[tiles[0]] += 1
                        hands[who][tiles[0]] -= 1
                next_element = GetNextRealTag(next_element)

    def PrintResults(self):
        with open("./results/KabeCounts.csv", "w") as f:
            with open("./results/KabeWins.csv", "w") as w:
                f.write("Type,Total,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0\n")
                w.write("Type,Total,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0\n")
                for i in self.counts:
                    f.write("%s,," % i)
                    for j in range(18,-1,-1):
                        f.write("%d," % self.counts[i][j])
                    f.write("\n")

                    w.write("%s,," % i)
                    for j in range(18,-1,-1):
                        w.write("%d," % self.wins[i][j])
                    w.write("\n")


def checkSuji(tile, discards, riichi_tile, _print=False):
    tile_value = tile % 10

    is_suji_below = True
    is_suji_above = True

    if tile_value > 3:
        is_suji_below = discards[tile - 3]

    if tile_value < 7:
        is_suji_above = discards[tile + 3]

    if is_suji_above and is_suji_below:
        return "Suji %d" % tile_value
    
    if tile_value > 3 and tile_value < 7:
        if is_suji_above:
            if riichi_tile == tile - 3:
                return "Nakasuji with riichi tile %d" % tile_value
            else:
                return "Half suji %d" % tile_value
        elif is_suji_below:
            if riichi_tile == tile + 3:
                return "Nakasuji with riichi tile %d" % tile_value
            else:
                return "Half suji %d" % tile_value
        else:
            if riichi_tile == tile - 3:
                return "Half suji via riichi tile %d" % tile_value
            if riichi_tile == tile + 3:
                return "Half suji via riichi tile %d" % tile_value
    else:
        if tile_value > 6:
            if riichi_tile == tile - 3:
                return "Riichi suji %d" % tile_value
        if tile_value < 4:
            if riichi_tile == tile + 3:
                return "Riichi suji %d" % tile_value
    
    return "Non-suji %d" % tile_value
    
def calculateLiveSuji(discards, riichi_tile):
    # 1-4 2-5 3-6 4-7 5-8 6-9
    live_suji = 18

    for i in range(1,7):
        if discards[i] or discards[i + 3] or riichi_tile == i or riichi_tile == i + 3:
            live_suji -= 1
        if discards[i + 10] or discards[i + 13] or riichi_tile == i + 10 or riichi_tile == i + 13:
            live_suji -= 1
        if discards[i + 20] or discards[i + 23] or riichi_tile == i + 20 or riichi_tile == i + 23:
            live_suji -= 1
    
    return live_suji

def calculateVisibleTiles(discard, hand, visible_tiles, log_id):
    tile_value = discard % 10
    visible = [0, 0, 0, 0, 0]

    visible[2] = hand[discard] + visible_tiles[discard]
    if visible[2] == 0:
        print(log_id)
        print(discard)
        print(hand)
        print(visible_tiles)

    if tile_value > 1:
        visible[1] = min(hand[discard - 1] + visible_tiles[discard - 1], 4)
    if tile_value > 2:
        visible[0] = min(hand[discard - 2] + visible_tiles[discard - 2], 4)
    if tile_value < 9:
        visible[3] = min(hand[discard + 1] + visible_tiles[discard + 1], 4)
    if tile_value < 8:
        visible[4] = min(hand[discard + 2] + visible_tiles[discard + 2], 4)

    return "%d%d%d%d%d" % (visible[0], visible[1], visible[2], visible[3], visible[4])