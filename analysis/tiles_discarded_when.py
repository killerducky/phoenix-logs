from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from analysis_utils import convertTile, GetNextRealTag, discards, GetRoundNameWithoutRepeats, CheckSeat

class TilesDiscardedWhen(LogAnalyzer):
    def __init__(self):
        self.counts = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        starts = log.findall('INIT')

        for start in starts:
            discarded_tiles = 0
            round_wind = GetRoundNameWithoutRepeats(start).split(" ")[0]
            dealer = start.attrib["oya"]

            next_element = GetNextRealTag(start)
            while next_element is not None:
                if next_element.tag == "DORA":
                    pass
                elif next_element.tag[0] in discards:
                    discarded_tiles += 1
                    seat_wind = CheckSeat(discards.index(next_element.tag[0]), dealer)

                    tile = convertTile(next_element.tag[1:])
                    tile_key = str(tile % 10)
                    if tile > 30:
                        if tile == 31:
                            if round_wind == "East":
                                if seat_wind == "East":
                                    tile_key = "Double Wind"
                                else:
                                    tile_key = "Round Wind"
                            elif seat_wind == "East":
                                tile_key = "Seat Wind"
                            else:
                                tile_key = "Guest Wind"
                        elif tile == 32:
                            if round_wind == "South":
                                if seat_wind == "South":
                                    tile_key = "Double Wind"
                                else:
                                    tile_key = "Round Wind"
                            elif seat_wind == "South":
                                tile_key = "Seat Wind"
                            else:
                                tile_key = "Guest Wind"
                        elif tile == 33:
                            if round_wind == "West":
                                if seat_wind == "West":
                                    tile_key = "Double Wind"
                                else:
                                    tile_key = "Round Wind"
                            elif seat_wind == "West":
                                tile_key = "Seat Wind"
                            else:
                                tile_key = "Guest Wind"
                        elif tile == 34:
                            if seat_wind == "North":
                                tile_key = "Seat Wind"
                            else:
                                tile_key = "Guest Wind"
                        else:
                            tile_key = "Dragon"
                        
                    self.counts[int(discarded_tiles / 4)][tile_key] += 1
                elif next_element.tag == "REACH":
                    if int(next_element.attrib["step"]) == 2:
                        break
                elif next_element.tag == "INIT":
                    break
                next_element = GetNextRealTag(next_element)

    def PrintResults(self):
        with open("./results/TilesDiscardedWhen.csv", "w", encoding="utf8") as f:
            f.write("Turn,1,2,3,4,5,6,7,8,9,Double Wind,Round Wind,Seat Wind,Guest Wind,Dragon\n")

            order = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "Double Wind", "Round Wind", "Seat Wind", "Guest Wind", "Dragon"]
            for turn in self.counts:
                f.write("%d," % turn)
                for tile in order:
                    f.write("%d," % self.counts[turn][tile])
                f.write("\n")