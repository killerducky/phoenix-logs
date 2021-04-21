from analysis_utils import convertTile, discards, GetPreviousRealTag, GetNextRealTag, GetRoundName, CheckSeat, getTilesFromCall, draws
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from lxml import etree

dora_indication = [
     6, 2, 3, 4, 5, 6, 7, 8, 9, 1,
    16,12,13,14,15,16,17,18,19,11,
    26,22,23,24,25,26,27,28,29,21,
    30,32,33,34,31,36,37,35
]

winds = [
    "East", "South", "West", "North"
]

class Honors(LogAnalyzer):
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
            dora = -1
            seat_wind = -1
            round_wind = -1
            held = [[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0],[0,0,0,0,0,0,0]]

            while previous is not None:
                if previous.tag == "DORA":
                    visible_tiles[convertTile(previous.attrib["hai"])] += 1
                    previous = GetPreviousRealTag(previous)
                    continue
                elif previous.tag[0] in discards:
                    tile = convertTile(previous.tag[1:])
                    visible_tiles[tile] += 1
                    if tile > 30:
                        held[discards.index(previous.tag[0])][tile - 31] -= 1
                    if previous.tag[0] == riichi_discard:
                        discarded_tiles[tile] = True
                elif previous.tag[0] in draws:
                    tile = convertTile(previous.tag[1:])
                    if tile > 30:
                        held[draws.index(previous.tag[0])][tile - 31] += 1
                elif previous.tag == "N":
                    tiles = getTilesFromCall(previous.attrib["m"])
                    if len(tiles) == 3:
                        visible_tiles[tiles[1]] += 1
                        visible_tiles[tiles[2]] += 1
                elif previous.tag == "INIT":
                    indicator = convertTile(previous.attrib["seed"].split(",")[5])
                    visible_tiles[indicator] += 1
                    dora = dora_indication[indicator]
                    round_wind = GetRoundName(previous).split(" ")[0]
                    seat_wind = CheckSeat(riichi.attrib["who"], previous.attrib["oya"])
                    break
                previous = GetPreviousRealTag(previous)
            
            next_element = GetNextRealTag(riichi)

            while next_element is not None:
                if next_element.tag == "DORA":
                    visible_tiles[convertTile(next_element.attrib["hai"])] += 1
                    next_element = GetNextRealTag(next_element)
                    continue
                elif next_element.tag[0] == riichi_discard:
                    tile = convertTile(next_element.tag[1:])
                    visible_tiles[tile] += 1
                    if tile != riichi_tile:
                        discarded_tiles[convertTile(next_element.tag[1:])] = True
                elif next_element.tag[0] in discards:
                    tile = convertTile(next_element.tag[1:])
                    # Genbutsu is obviously safe, and we're only looking at honors
                    if discarded_tiles[tile] or tile == riichi_tile or tile < 30:
                        visible_tiles[tile] += 1
                        discarded_tiles[tile] = True
                        next_element = GetNextRealTag(next_element)
                        continue

                    who = discards.index(next_element.tag[0])
                    held[who][tile - 31] -= 1
                    visible = visible_tiles[tile] + held[who][tile - 31]

                    key = ""
                    if tile == dora:
                        key = "Dora "
                    
                    if tile < 35:
                        tile_name = winds[tile - 31]
                        if tile_name == seat_wind:
                            if tile_name == round_wind:
                                key += "Double Wind with %d visible" % visible_tiles[tile]
                            else:
                                key += "Seat Wind with %d visible" % visible_tiles[tile]
                        elif tile_name == round_wind:
                            key += "Round Wind with %d visible" % visible_tiles[tile]
                        else:
                            key += "Guest Wind with %d visible" % visible_tiles[tile]
                    else:
                        key += "Dragon with %d visible" % visible_tiles[tile]
                    
                    live_suji = calculateLiveSuji(discarded_tiles, riichi_tile)
                    self.counts[key][live_suji] += 1

                    next_element = GetNextRealTag(next_element)
                    if next_element.tag == "AGARI":
                        if int(next_element.attrib["who"]) == riichi_player:
                            self.wins[key][live_suji] += 1
                        else:
                            next_element = GetNextRealTag(next_element)
                            if next_element is not None and next_element.tag == "AGARI":
                                if int(next_element.attrib["who"]) == riichi_player:
                                    self.wins[key][live_suji] += 1
                        break

                    discarded_tiles[tile] = True
                    visible_tiles[tile] += 1
                    continue
                elif next_element.tag[0] in draws:
                    tile = convertTile(next_element.tag[1:])
                    if tile > 30:
                        held[draws.index(next_element.tag[0])][tile - 31] += 1
                elif next_element.tag == "N":
                    tiles = getTilesFromCall(next_element.attrib["m"])
                    if len(tiles) == 3:
                        visible_tiles[tiles[1]] += 1
                        visible_tiles[tiles[2]] += 1
                elif next_element.tag == "AGARI" or next_element.tag == "RYUUKYOKU":
                    break
                next_element = GetNextRealTag(next_element)

    def PrintResults(self):
        with open("./results/HonorCounts.csv", "w") as c:
            with open("./results/HonorWins.csv", "w") as w:
                c.write("Type,Total,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0\n")
                w.write("Type,Total,18,17,16,15,14,13,12,11,10,9,8,7,6,5,4,3,2,1,0\n")
                for i in self.counts:
                    c.write("%s,," % i)
                    for j in range(18,-1,-1):
                        c.write("%d," % self.counts[i][j])
                    c.write("\n")
                    w.write("%s,," % i)
                    for j in range(18,-1,-1):
                        w.write("%d," % self.wins[i][j])
                    w.write("\n")

    
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