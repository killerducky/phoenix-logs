from log_analyzer import LogAnalyzer
from analysis_utils import draws, discards, GetNextRealTag, getTilesFromCall, convertTile, convertHai
from collections import Counter, defaultdict

class VisibleHonors(LogAnalyzer):
    def __init__(self):
        self.counts = defaultdict(Counter)
        self.in_wall = defaultdict(Counter)
    
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
                if next_element.tag == "INIT":
                    break
                next_element = GetNextRealTag(next_element)
            
            if total_discards > 24:
                for i in range(38):
                    if i < 30:
                        self.counts[i % 10][visible[i]] += 1
                        self.in_wall[i % 10][visible[i]] += 4 - present[i]
                    else:
                        self.counts[i][visible[i]] += 1
                        self.in_wall[i][visible[i]] += 4 - present[i]
    
    def PrintResults(self):
        with open("./results/VisibleHonorCounts.csv", "w") as f:
            f.write("Tile,0,1,2,3,4\n")
            for i in range(1,10):
                f.write("%d,%d,%d,%d,%d,%d\n" % (
                    i,
                    self.counts[i][0],
                    self.counts[i][1],
                    self.counts[i][2],
                    self.counts[i][3],
                    self.counts[i][4]
                ))
            for i in range(31,38):
                f.write("%d,%d,%d,%d,%d,%d\n" % (
                    i,
                    self.counts[i][0],
                    self.counts[i][1],
                    self.counts[i][2],
                    self.counts[i][3],
                    self.counts[i][4]
                ))
        with open("./results/VisibleHonorDraws.csv", "w") as f:
            f.write("Tile,0,1,2,3,4\n")
            for i in range(1,10):
                f.write("%d,%d,%d,%d,%d,%d\n" % (
                    i,
                    self.in_wall[i][0],
                    self.in_wall[i][1],
                    self.in_wall[i][2],
                    self.in_wall[i][3],
                    self.in_wall[i][4]
                ))
            for i in range(31,38):
                f.write("%d,%d,%d,%d,%d,%d\n" % (
                    i,
                    self.in_wall[i][0],
                    self.in_wall[i][1],
                    self.in_wall[i][2],
                    self.in_wall[i][3],
                    self.in_wall[i][4]
                ))