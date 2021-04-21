from analysis_utils import convertTile, discards, GetPreviousRealTag, GetNextRealTag
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter

class Suji(LogAnalyzer):
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
                elif previous.tag[0] in discards:
                    tile = convertTile(previous.tag[1:])
                    visible_tiles[tile] += 1
                    if previous.tag[0] == riichi_discard:
                        discarded_tiles[tile] = True
                elif previous.tag == "INIT":
                    break
                previous = GetPreviousRealTag(previous)
            
            next_element = GetNextRealTag(riichi)

            while next_element is not None:
                if next_element.tag == "DORA":
                    next_element = GetNextRealTag(next_element)
                elif next_element.tag[0] == riichi_discard:
                    tile = convertTile(next_element.tag[1:])
                    visible_tiles[tile] += 1
                    if tile != riichi_tile:
                        discarded_tiles[convertTile(next_element.tag[1:])] = True
                elif next_element.tag[0] in discards:
                    tile = convertTile(next_element.tag[1:])
                    visible_tiles[tile] += 1
                    # Genbutsu is obviously safe and we're not worrying about honors
                    if discarded_tiles[tile] or tile > 30 or tile == riichi_tile:
                        next_element = GetNextRealTag(next_element)
                        continue

                    suji_type = checkSuji(tile, discarded_tiles, riichi_tile)

                    if suji_type != "Suji 1" and suji_type != "Suji 9":
                        next_element = GetNextRealTag(next_element)
                        continue

                    live_suji = calculateLiveSuji(discarded_tiles, riichi_tile)
                    suji_type = "%s #%d" % (suji_type, visible_tiles[tile])
                    self.counts[suji_type][live_suji] += 1

                    next_element = GetNextRealTag(next_element)
                    if next_element.tag == "AGARI":
                        if int(next_element.attrib["who"]) == riichi_player:
                            self.wins[suji_type][live_suji] += 1
                        # check for double ron
                        else:
                            next_element = GetNextRealTag(next_element)
                            if next_element is not None and next_element.tag == "AGARI":
                                if int(next_element.attrib["who"]) == riichi_player:
                                    self.wins[suji_type][live_suji] += 1
                        break

                    discarded_tiles[tile] = True
                    continue
                elif next_element.tag == "AGARI" or next_element.tag == "RYUUKYOKU":
                    break
                next_element = GetNextRealTag(next_element)

    def PrintResults(self):
        with open("./results/SujiCounts.csv", "w") as f:
            f.write("Type,Total,18,17,16,etc\n")
            for i in self.counts:
                f.write("%s,," % i)
                for j in range(18,-1,-1):
                    f.write("%d," % self.counts[i][j])
                f.write("\n")

        with open("./results/SujiWins.csv", "w") as f:
            f.write("Type,Total,18,17,16,etc\n")
            for i in self.wins:
                f.write("%s,," % i)
                for j in range(18,-1,-1):
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