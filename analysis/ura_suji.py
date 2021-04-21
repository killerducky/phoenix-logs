from analysis_utils import convertTile, discards, GetPreviousRealTag, GetNextRealTag, GetRoundName, CheckSeat, getTilesFromCall, draws, convertHai, convertHandToTenhouString
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from lxml import etree
from ukeire import calculateUkeire
from shanten import calculateMinimumShanten

class UraSuji(LogAnalyzer):
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
            discarded_tiles = []
            held = [0] * 38
            held[riichi_tile] -= 1
            abort = False
            discards_pre_riichi = 0

            # gather the visible tiles and what their hand is
            while previous is not None:
                if previous.tag == "DORA":
                    previous = GetPreviousRealTag(previous)
                    continue
                elif previous.tag[0] == riichi_discard:
                    tile = convertTile(previous.tag[1:])
                    discarded_tiles.append(tile)
                    held[tile] -= 1
                    discards_pre_riichi += 1
                elif previous.tag[0] == riichi_draw:
                    tile = convertTile(previous.tag[1:])
                    held[tile] += 1
                elif previous.tag == "N":
                    if int(previous.attrib["who"]) == riichi_player:
                        abort = True
                        break # closed kans are too hard
                elif previous.tag == "INIT":
                    starting_hand = convertHai(previous.attrib["hai%d" % riichi_player])
                    for i in range(38):
                        held[i] += starting_hand[i]
                    break
                previous = GetPreviousRealTag(previous)
            
            if abort or discards_pre_riichi < 3:
                continue

            # check the wait
            remaining_tiles = [4] * 38
            ukeire = calculateUkeire(held, remaining_tiles, calculateMinimumShanten, 0)
            types = ukeire[1]

            if len(types) != 2:
                continue

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

            if not suji_shape:
                continue

            types.sort()
            wait = "%d-%d" % (types[0] % 10, types[1] % 10)
            wait_suit = types[0] - types[0] % 10
            self.counts["Total"][wait] += 1
            unique_discards = list(dict.fromkeys(discarded_tiles))

            for tile in unique_discards:
                if tile > 30:
                    continue

                if tile - tile % 10 == wait_suit:
                    self.counts[tile % 10][wait] += 1
                else:
                    self.counts[tile % 10]["Other"] += 1
            
            if riichi_tile < 30:
                if riichi_tile - riichi_tile % 10 == wait_suit:
                    self.counts["Riichi %d" % (riichi_tile % 10)][wait] += 1
                else:
                    self.counts["Riichi %d" % (riichi_tile % 10)]["Other"] += 1

    def PrintResults(self):
        waits = ["1-4", "2-5", "3-6", "4-7", "5-8", "6-9", "Other"]

        with open("./results/UraSuji.csv", "w") as c:
            c.write("Discard,1-4,2-5,3-6,4-7,5-8,6-9,Other\n")
            for tile in self.counts:
                c.write("%s," % tile)
                for wait in waits:
                    c.write("%d," % self.counts[tile][wait])
                c.write("\n")
