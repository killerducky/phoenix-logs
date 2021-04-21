from log_analyzer import LogAnalyzer
from analysis_utils import draws, discards, GetNextRealTag, getTilesFromCall, convertTile, convertHai
from collections import Counter, defaultdict

class HonorsAfterPass(LogAnalyzer):
    def __init__(self):
        self.discarded = defaultdict(Counter)
        self.not_discarded = defaultdict(Counter)
    
    def ParseLog(self, log, log_id):
        starts = log.findall("INIT")

        for start in starts:
            visible = [0] * 38
            present = [0] * 38
            drawn = [False] * 38
            total_discards = 0

            for i in range(4):
                hai = convertHai(start.attrib["hai%d" %i])
                for j in range(38):
                    present[j] += hai[j]

            next_element = GetNextRealTag(start)

            while next_element is not None:
                if total_discards < 25:
                    if next_element.tag == "DORA":
                        pass
                    elif next_element.tag[0] in discards:
                        total_discards += 1
                        
                        tile = convertTile(next_element.tag[1:])
                        visible[tile] += 1

                        if visible[tile] == 1 and tile > 30:
                            possible_call = GetNextRealTag(next_element)
                            if possible_call.tag != "N":
                                self.discarded[tile]["Turn %d" % int(total_discards / 4)] += 1
                                self.discarded[tile]["In Wall %d" % int(total_discards / 4)] += 4 - present[tile]
                    elif next_element.tag == "N":
                        tiles = getTilesFromCall(next_element.attrib["m"])
                        if len(tiles) == 3:
                            visible[tiles[1]] += 1
                            visible[tiles[2]] += 1
                        elif len(tiles) == 4:
                            visible[tiles[0]] = 4
                        else:
                            visible[tiles[0]] += 1
                    elif next_element.tag[0] in draws:
                        tile = convertTile(next_element.tag[1:])
                        present[tile] += 1
                else:
                    break
                if total_discards % 4 == 0:
                    for i in range(31,38):
                        if visible[i] == 0:
                            self.not_discarded[i]["Turn %d" % int(total_discards / 4)] += 1
                            self.not_discarded[i]["In Wall %d" % int(total_discards / 4)] += 4 - present[i]
                if next_element.tag == "INIT":
                    break
                next_element = GetNextRealTag(next_element)
            
    def PrintResults(self):
        with open("./results/HonorDiscards.csv", "w") as f:
            f.write("Tile,")
            for i in range(7):
                f.write("Turn %d,In Wall %d," % (i,i))
            f.write("\n")
            for i in range(31,38):
                f.write("%d," % i)
                for j in range(7):
                    f.write("%d,%d," % (self.discarded[i]["Turn %d" % j], self.discarded[i]["In Wall %d" % j]))
                f.write("\n")
        with open("./results/HonorNotDiscards.csv", "w") as f:
            f.write("Tile,")
            for i in range(7):
                f.write("Turn %d,In Wall %d," % (i,i))
            f.write("\n")
            for i in range(31,38):
                f.write("%d," % i)
                for j in range(7):
                    f.write("%d,%d," % (self.not_discarded[i]["Turn %d" % j], self.not_discarded[i]["In Wall %d" % j]))
                f.write("\n")