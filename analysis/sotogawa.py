from analysis_utils import convertTile, discards, GetPreviousRealTag, GetNextRealTag
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter

class Sotogawa(LogAnalyzer):
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
            discard_list = []

            previous = GetPreviousRealTag(riichi)
            if previous.tag == "REACH":
                # there exists one broken replay in the dataset
                continue
            riichi_tile = convertTile(previous.tag[1:])
            previous = GetPreviousRealTag(previous)

            while previous is not None:
                if previous.tag == "DORA":
                    previous = GetPreviousRealTag(previous)
                    continue
                elif previous.tag[0] == riichi_discard:
                    tile = convertTile(previous.tag[1:])
                    discarded_tiles[tile] = True
                    discard_list.insert(0, tile)
                elif previous.tag == "INIT":
                    break
                previous = GetPreviousRealTag(previous)
            
            next_element = GetNextRealTag(riichi)

            while next_element is not None:
                if next_element.tag == "DORA":
                    next_element = GetNextRealTag(next_element)
                elif next_element.tag[0] == riichi_discard:
                    tile = convertTile(next_element.tag[1:])
                    if tile != riichi_tile:
                        discarded_tiles[convertTile(next_element.tag[1:])] = True
                elif next_element.tag[0] in discards:
                    tile = convertTile(next_element.tag[1:])
                    # Genbutsu is obviously safe and we're not worrying about honors
                    if discarded_tiles[tile] or tile > 30 or tile == riichi_tile:
                        next_element = GetNextRealTag(next_element)
                        continue

                    suji_type = checkSuji(tile, discarded_tiles, riichi_tile)
                    sotogawas = checkSotogawa(tile, discard_list)

                    for sotogawa in sotogawas:
                        self.counts[sotogawa[0] + suji_type][sotogawa[1]] += 1

                    next_element = GetNextRealTag(next_element)
                    if next_element.tag == "AGARI":
                        if int(next_element.attrib["who"]) == riichi_player:
                            for sotogawa in sotogawas:
                                self.wins[sotogawa[0] + suji_type][sotogawa[1]] += 1
                        # check for double ron
                        else:
                            next_element = GetNextRealTag(next_element)
                            if next_element is not None and next_element.tag == "AGARI":
                                if int(next_element.attrib["who"]) == riichi_player:
                                    for sotogawa in sotogawas:
                                        self.wins[sotogawa[0] + suji_type][sotogawa[1]] += 1
                        break

                    discarded_tiles[tile] = True
                    continue
                elif next_element.tag == "AGARI" or next_element.tag == "RYUUKYOKU":
                    break
                next_element = GetNextRealTag(next_element)

    def PrintResults(self):
        with open("./results/SotogawaCounts.csv", "w") as f:
            f.write("Type,Total,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20\n")
            for i in self.counts:
                f.write("%s,," % i)
                for j in range(21):
                    f.write("%d," % self.counts[i][j])
                f.write("\n")

        with open("./results/SotogawaWins.csv", "w") as f:
            f.write("Type,Total,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20\n")
            for i in self.wins:
                f.write("%s,," % i)
                for j in range(21):
                    f.write("%d," % self.wins[i][j])
                f.write("\n")

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

def checkSotogawa(tile, discard_list):
    sotogawas = []
    tile_value = tile % 10
    tile_suit = tile - tile_value
    middle = tile_suit + 5

    for toCheck in range(1,5):
        if tile_value < 5:
            tile_to_check = tile + toCheck
            if tile_to_check <= middle and tile_to_check in discard_list:
                sotogawas.append(("Sotogawa by %d " % (tile_value + toCheck), discard_list.index(tile_to_check)))
        else:
            tile_to_check = tile - toCheck
            if tile_to_check >= middle and tile_to_check in discard_list:
                sotogawas.append(("Sotogawa by %d " % (tile_value - toCheck), discard_list.index(tile_to_check)))
    
    if len(sotogawas) == 0:
        sotogawas.append(("Non-sotogawa ", len(discard_list)))
    
    return sotogawas
