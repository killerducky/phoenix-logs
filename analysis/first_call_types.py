from analysis_utils import convertTile, discards, GetNextRealTag, getTilesFromCall, draws, GetWhoTileWasCalledFrom
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from lxml import etree
from urllib.parse import unquote

class FirstCallTypes(LogAnalyzer):
    def __init__(self):
        self.turn = defaultdict(Counter)
        self.type = defaultdict(Counter)
        self.count = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        rounds = log.findall("INIT")
        
        data = log.find("UN")
        tori = -1

        for i in range(4):
            name = unquote(data.attrib["n%d" % i])
            if name == "tori0612":
                tori = i
                break
        
        for start in rounds:
            calls = [0, 0, 0, 0]
            discarded_tiles = 0
            next_element = GetNextRealTag(start)

            while next_element is not None:
                if next_element.tag == "DORA":
                    pass
                elif next_element.tag[0] in discards:
                    discarded_tiles += 1
                elif next_element.tag == "N":
                    call_type = ""
                    player = int(next_element.attrib["who"])

                    tiles = getTilesFromCall(next_element.attrib["m"])
                    if len(tiles) == 1:
                        pass
                    else:
                        if len(tiles) == 4:
                            if GetWhoTileWasCalledFrom(next_element) != 0:
                                call_type = "Open Kan Middle"
                                if tiles[0] > 30:
                                    call_type = "Open Kan Honor"
                                elif tiles[0] % 10 == 1 or tiles[0] % 10 == 9:
                                    call_type = "Open Kan Terminal"
                        else:
                            if tiles[1] == tiles[2]:
                                call_type = "Pon Middle"
                                if tiles[0] > 30:
                                    call_type = "Pon Honor"
                                elif tiles[0] % 10 == 1 or tiles[0] % 10 == 9:
                                    call_type = "Pon Terminal"
                            else:
                                call_type = "Kanchan"
                                if tiles[1] - 1 == tiles[2] or tiles[1] + 1 == tiles[2]:
                                    if tiles[1] % 10 == 1 or tiles[2] % 10 == 1 or tiles[1] % 10 == 9 or tiles[2] % 10 == 9:
                                        call_type = "Penchan"
                                    else:
                                        call_type = "Ryanmen"
                        if call_type != "":
                            calls[player] += 1
                            if calls[player] == 1:
                                if tori == player:
                                    self.type["Tori"][call_type] += 1
                                    self.turn["Tori"][int(discarded_tiles / 4)] += 1
                                else:
                                    self.type["Average"][call_type] += 1
                                    self.turn["Average"][int(discarded_tiles / 4)] += 1
                elif next_element.tag == "INIT":
                    break
                next_element = GetNextRealTag(next_element)
            
            for i in range(4):
                if i == tori:
                    self.count["Tori"][calls[i]] += 1
                else:
                    self.count["Average"][calls[i]] += 1

    def PrintResults(self):
        with open("./results/ToriFirstCallTurn.csv", "w") as f:
            f.write("Who,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18\n")
            for i in self.turn:
                f.write("%s," % i)
                for j in range(19):
                    f.write("%d," % self.turn[i][j])
                f.write("\n")
                
        with open("./results/ToriFirstCallType.csv", "w") as f:
            f.write("Who,")
            for call_type in self.type["Average"]:
                f.write("%s," % call_type)
            f.write("\n")

            for i in self.type:
                f.write("%s," % i)
                for j in self.type["Average"]:
                    f.write("%d," % self.type[i][j])
                f.write("\n")

        with open("./results/ToriNumberOfCalls.csv", "w") as f:
            f.write("Who,0 Calls,1 Call,2 Calls,3 Calls,4 Calls\n")
            for i in self.count:
                f.write("%s," % i)
                for j in range(5):
                    f.write("%d," % self.count[i][j])
                f.write("\n")