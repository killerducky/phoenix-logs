from analysis_utils import convertTile, discards, GetPreviousRealTag, GetNextRealTag, GetRoundName, CheckSeat, getTilesFromCall, draws, convertHai, convertHandToTenhouString
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from lxml import etree
from ukeire import calculateUkeire
from shanten import calculateMinimumShanten

class Duplicates(LogAnalyzer):
    def __init__(self):
        self.counts = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        starts = log.findall("INIT")

        for start in starts:
            early_discards = [[],[],[],[]]
            late_discards = [[],[],[],[]]
            total_discards = 0
            next_element = GetNextRealTag(start)

            # gather the visible tiles and what their hand is
            while next_element is not None:
                if next_element.tag == "DORA":
                    pass
                elif next_element.tag[0] in discards:
                    tile = convertTile(next_element.tag[1:])
                    player = discards.index(next_element.tag[0])

                    if len(early_discards[player]) < 6:
                        early_discards[player].append(tile)
                    else:
                        late_discards[player].append(tile)
                    total_discards += 1
                elif next_element.tag == "INIT":
                    break

                next_element = GetNextRealTag(next_element)
            
            if total_discards < 48:
                continue

            for i in range(4):
                no_duplicates = list(set(early_discards[i]))

                for tile in no_duplicates:
                    tile_key = tile
                    if tile_key < 30:
                        tile_key = tile % 10

                    self.counts[tile_key]["Count"] += 1
                    
                    if tile in late_discards[i]:
                        self.counts[tile_key]["Again"] += 1
                    if early_discards[i].count(tile) > 1:
                        self.counts[tile_key]["Twice"] += 1
            

    def PrintResults(self):
        with open("./results/Duplicates.csv", "w") as c:
            c.write("Tile,Count First Row,Again Later,Twice in First Row\n")
            for tile in self.counts:
                c.write("%d,%d,%d,%d\n" % (
                    tile, 
                    self.counts[tile]["Count"], 
                    self.counts[tile]["Again"], 
                    self.counts[tile]["Twice"]
                    )
                )

