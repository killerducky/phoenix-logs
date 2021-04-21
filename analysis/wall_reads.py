from log_analyzer import LogAnalyzer
from analysis_utils import draws, discards, GetNextRealTag, getTilesFromCall, convertTile, convertHai
from collections import Counter, defaultdict

class WallReads(LogAnalyzer):
    def __init__(self):
        self.first_three = defaultdict(Counter)
        self.second_three = defaultdict(Counter)
    
    def ParseLog(self, log, log_id):
        starts = log.findall("INIT")

        for start in starts:
            hands = []
            discard_count = [0, 0, 0, 0]

            for i in range(4):
                hai = convertHai(start.attrib["hai%d" %i])
                hands.append(hai)

            next_element = GetNextRealTag(start)

            while next_element is not None:
                if next_element.tag == "DORA":
                    pass
                elif next_element.tag[0] in discards:
                    player = discards.index(next_element.tag[0])
                    tile = convertTile(next_element.tag[1:])
                    discard_count[player] += 1
                    hands[player][tile] -= 1

                    if discard_count[player] < 7 and tile < 30:
                        nearby_tiles = hands[player][tile] + hands[player][tile - 1] + hands[player][tile + 1]
                        if tile % 10 < 8:
                            nearby_tiles += hands[player][tile + 2]
                        if tile % 10 > 2:
                            nearby_tiles += hands[player][tile - 2]

                        if discard_count[player] < 4:
                            self.first_three[tile % 10]["Count"] += 1
                            self.first_three[tile % 10]["Nearby"] += nearby_tiles
                        else:
                            self.second_three[tile % 10]["Count"] += 1
                            self.second_three[tile % 10]["Nearby"] += nearby_tiles

                        suit = tile - tile % 10
                        suit_tiles = 0
                        for i in range(suit, suit + 10):
                            suit_tiles += hands[player][i]

                        if discard_count[player] < 4:
                            self.first_three[tile % 10]["In Suit"] += suit_tiles
                        else:
                            self.second_three[tile % 10]["In Suit"] += suit_tiles
                elif next_element.tag[0] in draws:
                    player = draws.index(next_element.tag[0])
                    tile = convertTile(next_element.tag[1:])
                    hands[player][tile] += 1
                elif next_element.tag == "INIT" or next_element.tag == "REACH":
                    break
                if min(discard_count) > 6:
                    break
                next_element = GetNextRealTag(next_element)
    
    def PrintResults(self):
        with open("./results/WallFirstThree.csv", "w") as f:
            f.write("Tile,Count,Nearby Tiles,Tiles in Same Suit\n")
            for i in range(1,10):
                f.write("%d,%d,%d,%d\n" % (
                    i,
                    self.first_three[i]["Count"],
                    self.first_three[i]["Nearby"],
                    self.first_three[i]["In Suit"]
                ))
        with open("./results/WallSecondThree.csv", "w") as f:
            f.write("Tile,Count,Nearby Tiles,Tiles in Same Suit\n")
            for i in range(1,10):
                f.write("%d,%d,%d,%d\n" % (
                    i,
                    self.second_three[i]["Count"],
                    self.second_three[i]["Nearby"],
                    self.second_three[i]["In Suit"]
                ))