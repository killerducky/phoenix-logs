from analysis_utils import convertTile, discards, GetPreviousRealTag, GetNextRealTag, GetRoundName, CheckSeat, getTilesFromCall, draws, convertHai, convertHandToTenhouString
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from lxml import etree
from ukeire import calculateUkeire
from shanten import calculateMinimumShanten

class LastTwoAll(LogAnalyzer):
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

            riichi_tile = convertTile(previous.tag[1:])
            if riichi_tile > 30:
                continue

            riichi_player = int(riichi.attrib["who"])
            riichi_discard = discards[riichi_player]
            riichi_draw = draws[riichi_player]
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

            riichi_suit = riichi_tile - riichi_tile % 10

            last_tile_in_suit = "None"

            for tile in discarded_tiles:
                if tile - tile % 10 == riichi_suit:
                    last_tile_in_suit = str(tile % 10)
                    break
            
            key = "%s->%d" % (last_tile_in_suit, riichi_tile % 10)

            # check the wait
            remaining_tiles = [4] * 38
            ukeire = calculateUkeire(held, remaining_tiles, calculateMinimumShanten, 0)
            types = ukeire[1]

            if len(types) == 0:
                continue

            self.counts[key]["Instances"] += 1
            self.counts["Total"]["Instances"] += 1

            for tile in types:
                wait = str(tile % 10)
                wait_suit = tile - tile % 10
                if wait_suit == 0:
                    self.counts["Total"][wait] += 1
                else:
                    if tile > 30:
                        self.counts["Total"]["Z"] += 1
                    else: 
                        self.counts["Total"]["Other Suit"] += 1

                if riichi_tile - riichi_tile % 10 == wait_suit:
                    self.counts[key][wait] += 1
                else:
                    if tile > 30:
                        self.counts[key]["Z"] += 1
                    else:
                        self.counts[key]["Other Suit"] += 1

    def PrintResults(self):
        waits = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "Z", "Other Suit", "Instances"]

        with open("./results/LastTwoOverall.csv", "w") as c:
            c.write("Pattern,1,2,3,4,5,6,7,8,9,Z,Other Suit,Instances\n")
            for tile in self.counts:
                c.write("%s," % tile)
                for wait in waits:
                    c.write("%d," % self.counts[tile][wait])
                c.write("\n")
