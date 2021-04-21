from analysis_utils import convertTile, discards, GetPreviousRealTag, GetNextRealTag, GetRoundName, CheckSeat, getTilesFromCall, draws, convertHai, convertHandToTenhouString
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from lxml import etree
from ukeire import calculateUkeire
from shanten import calculateMinimumShanten

class WaitsByTile(LogAnalyzer):
    def __init__(self):
        self.counts = defaultdict(Counter)

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
            held = [0] * 38
            held[riichi_tile] -= 1
            first_draw = -1
            abort = False
            chasing = False

            # gather the visible tiles and what their hand is
            while previous is not None:
                if previous.tag == "DORA":
                    previous = GetPreviousRealTag(previous)
                    continue
                elif previous.tag[0] == riichi_discard:
                    tile = convertTile(previous.tag[1:])
                    held[tile] -= 1
                elif previous.tag[0] == riichi_draw:
                    tile = convertTile(previous.tag[1:])
                    if first_draw == -1:
                        first_draw = tile
                    held[tile] += 1
                elif previous.tag == "N":
                    if int(previous.attrib["who"]) == riichi_player:
                        abort = True
                        break # closed kans are too hard
                elif previous.tag == "REACH":
                    chasing = True
                elif previous.tag == "INIT":
                    starting_hand = convertHai(previous.attrib["hai%d" % riichi_player])
                    for i in range(38):
                        held[i] += starting_hand[i]
                    break
                previous = GetPreviousRealTag(previous)
            
            if abort:
                continue

            # check the wait
            remaining_tiles = [4] * 38
            for i in range(38):
                remaining_tiles[i] -= held[i]
            ukeire = calculateUkeire(held, remaining_tiles, calculateMinimumShanten, 0)

            types = ukeire[1]
            suji_shape = True

            for tile in types:
                if tile > 30:
                    suji_shape = False
                    break

                if tile % 10 < 7:
                    if tile + 3 in types:
                        continue

                if tile % 10 > 3:
                    if tile - 3 in types:
                        continue
                    
                suji_shape = False
                break

            key = riichi_tile % 10
            if riichi_tile > 30:
                key = 0

            if first_draw == riichi_tile:
                key = "Tsumogiri %d" % key
            else:
                key = "Tedashi %d" % key

            if chasing:
                key = "Chasing %s" % key
            else:
                key = "First to Riichi %s" % key

            self.counts[key]["Total"] += 1
            self.counts[key][ukeire[0]] += 1
            if suji_shape:
                self.counts[key]["Suji Shapes"] += 1

    def PrintResults(self):
        with open("./results/RiichiWaitsByTile.csv", "w") as c:
            c.write("Riichi Tile,Counts,Suji Shapes,Average,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,etc\n")

            for i in self.counts:
                c.write("%s,%d,%d,," % (i, self.counts[i]["Total"], self.counts[i]["Suji Shapes"]))
                for j in range(1,40):
                    c.write("%d," % self.counts[i][j])
                c.write("\n")