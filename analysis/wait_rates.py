from analysis_utils import convertTile, discards, GetPreviousRealTag, GetNextRealTag, GetRoundName, CheckSeat, getTilesFromCall, draws, convertHai, convertHandToTenhouString
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from lxml import etree
from ukeire import calculateUkeire
from shanten import calculateMinimumShanten

class WaitRates(LogAnalyzer):
    def __init__(self):
        self.counts = Counter()
        self.discard_patterns = defaultdict(Counter)

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
            abort = False
            discards_pre_riichi = 0

            # gather the visible tiles and what their hand is
            while previous is not None:
                if previous.tag == "DORA":
                    previous = GetPreviousRealTag(previous)
                    continue
                elif previous.tag[0] == riichi_discard:
                    tile = convertTile(previous.tag[1:])
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
                elif previous.tag == "INIT":
                    starting_hand = convertHai(previous.attrib["hai%d" % riichi_player])
                    for i in range(38):
                        held[i] += starting_hand[i]
                    break
                previous = GetPreviousRealTag(previous)
            
            if abort or discards_pre_riichi < 2:
                continue

            # check the wait
            remaining_tiles = [4] * 38
            ukeire = calculateUkeire(held, remaining_tiles, calculateMinimumShanten, 0)
            types = ukeire[1]

            for tile in types:
                self.counts[tile] += 1
            
            self.CountDiscardPatterns(types, discarded_tiles)

    def PrintResults(self):
        with open("./results/WaitCounts.csv", "w") as c:
            c.write("Wait,Count\n")
            for tile in self.counts:
                c.write("%d,%d\n" % (tile, self.counts[tile]))
        with open("./results/DiscardPatternCounts.csv", "w") as d:
            d.write("Suited Discards,Total,1,2,3,4,5,6,7,8,9,Other\n")
            for pattern in self.discard_patterns:
                d.write("%s, ,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n" % (
                        pattern,
                        self.discard_patterns[pattern][1],
                        self.discard_patterns[pattern][2],
                        self.discard_patterns[pattern][3],
                        self.discard_patterns[pattern][4],
                        self.discard_patterns[pattern][5],
                        self.discard_patterns[pattern][6],
                        self.discard_patterns[pattern][7],
                        self.discard_patterns[pattern][8],
                        self.discard_patterns[pattern][9],
                        self.discard_patterns[pattern][10]
                    )
                )

    def CountDiscardPatterns(self, ukeire_types, discards):
        for suit in range(3):
            discard_string = ""
            for tile in range((suit * 10) + 1, (suit * 10) + 10):
                if discards[tile]:
                    discard_string += str(tile % 10)
            if discard_string == "":
                discard_string = "None"
            for wait in ukeire_types:
                if int(wait / 10) == suit:
                    self.discard_patterns[discard_string][wait % 10] += 1
                else:
                    self.discard_patterns[discard_string][10] += 1

