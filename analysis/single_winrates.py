from analysis_utils import convertTile, discards, GetPreviousRealTag, GetNextRealTag, GetRoundName, CheckSeat, getTilesFromCall, draws, convertHai, convertHandToTenhouString
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from lxml import etree
from ukeire import calculateUkeire
from tenpai_waits import calculateWaits
from shanten import calculateMinimumShanten

class SingleWinrates(LogAnalyzer):
    def __init__(self):
        self.counts = defaultdict(Counter)
        self.wins = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        riichis = log.findall("REACH")

        for riichi in riichis:
            if int(riichi.attrib["step"]) == 1:
                continue
            
            previous = GetPreviousRealTag(riichi)
            if previous.tag == "REACH":
                # there exists one broken replay in the dataset
                continue

            riichi_player = int(riichi.attrib["who"])
            riichi_discard = discards[riichi_player]
            riichi_draw = draws[riichi_player]

            riichi_tile = convertTile(previous.tag[1:])
            previous = GetPreviousRealTag(GetPreviousRealTag(previous))
            discarded_tiles = [False] * 38
            visible_tiles = [0] * 38
            held = [0] * 38
            held[riichi_tile] -= 1
            visible_tiles[riichi_tile] += 1
            abort = False
            discards_pre_riichi = 0

            # gather the visible tiles and what their hand is
            while previous is not None:
                if previous.tag == "DORA":
                    visible_tiles[convertTile(previous.attrib["hai"])] += 1
                    previous = GetPreviousRealTag(previous)
                    continue
                elif previous.tag[0] in discards:
                    tile = convertTile(previous.tag[1:])
                    visible_tiles[tile] += 1
                    if previous.tag[0] == riichi_discard:
                        discarded_tiles[tile] = True
                        held[tile] -= 1
                        discards_pre_riichi += 1
                elif previous.tag[0] == riichi_draw:
                    tile = convertTile(previous.tag[1:])
                    held[tile] += 1
                elif previous.tag == "N":
                    if int(previous.attrib["who"]) == riichi_player:
                        abort = True
                        break # closed kans are too hard

                    tiles = getTilesFromCall(previous.attrib["m"])
                    if len(tiles) == 3:
                        visible_tiles[tiles[1]] += 1
                        visible_tiles[tiles[2]] += 1
                    elif len(tiles) == 4:
                        visible_tiles[tiles[0]] = 4
                    elif len(tiles) == 1:
                        visible_tiles[tiles[0]] += 1
                elif previous.tag == "REACH":
                    abort = True
                    break
                elif previous.tag == "INIT":
                    indicator = convertTile(previous.attrib["seed"].split(",")[5])
                    visible_tiles[indicator] += 1
                    starting_hand = convertHai(previous.attrib["hai%d" % riichi_player])
                    for i in range(38):
                        held[i] += starting_hand[i]
                    break
                previous = GetPreviousRealTag(previous)
            
            if abort:
                continue

            if discards_pre_riichi < 3 or discards_pre_riichi > 15:
                continue

            # check the wait
            remaining_tiles = [4] * 38
            ukeire = calculateWaits(held, remaining_tiles)

            types = ukeire[1]

            if len(types) != 1:
                continue

            # check if they won
            next_element = GetNextRealTag(riichi)
            while next_element is not None:
                if next_element.tag == "AGARI" or next_element.tag == "RYUUKYOKU":
                    break
                next_element = GetNextRealTag(next_element)

            won = next_element.tag == "AGARI" and int(next_element.attrib["who"]) == riichi_player

            wait_string = "Honor"
            if types[0] < 30:
                wait_string = checkSuji(types[0], discarded_tiles, riichi_tile)

            visible_outs = 0
            furiten = False
            for i in types:
                visible_outs += min(visible_tiles[i] + held[i], 4)
                if discarded_tiles[i]:
                    furiten = True

            if furiten:
                continue
            
            self.counts[wait_string][visible_outs] += 1
            if won:
                self.wins[wait_string][visible_outs] += 1

    def PrintResults(self):
        with open("./results/SingleWaitCounts.csv", "w") as c:
            with open("./results/SingleWaitWins.csv", "w") as w:
                for i in self.counts:
                    c.write("%s,," % i)
                    w.write("%s,," % i)
                    for j in range(4):
                        c.write("%d," % self.counts[i][j])
                        w.write("%d," % self.wins[i][j])
                    c.write("\n")
                    w.write("\n")

def checkSuji(tile, discards, riichi_tile):
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