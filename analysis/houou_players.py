from log_analyzer import LogAnalyzer
from collections import Counter, defaultdict
from analysis_utils import GetWhoTileWasCalledFrom
from urllib.parse import unquote

class HououPlayers(LogAnalyzer):
    def __init__(self):
        self.player_data = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        names = ["", "", "", ""]
        
        data = log.find("UN")
        genders = data.attrib["sx"].split(",")

        for i in range(4):
            names[i] = unquote(data.attrib["n%d" % i])
            self.player_data[names[i]]["games"] += 1
            
            if genders[i] == "M":
                self.player_data[names[i]]["male"] += 1
            
        has_called = [False, False, False, False]
        has_riichi = [False, False, False, False]

        next_element = data.getnext()

        while next_element is not None:
            if next_element.tag == "N":
                if GetWhoTileWasCalledFrom(next_element) != 0:
                    has_called[int(next_element.attrib["who"])] = True
            
            if next_element.tag == "REACH":
                has_riichi[int(next_element.attrib["who"])] = True
            
            if next_element.tag == "AGARI":
                who = int(next_element.attrib["who"])
                fromWho = int(next_element.attrib["fromWho"])

                self.player_data[names[who]]["won"] += 1
                value = int(next_element.attrib["ten"].split(",")[1])
                self.player_data[names[who]]["total_value"] += value

                if who != fromWho:
                    self.player_data[names[who]]["ron"] += 1
                    self.player_data[names[fromWho]]["dealt_in"] += 1

                if int(next_element.attrib['ten'].split(',')[2]) >= 5:
                    self.player_data[names[who]]["yakuman"] += 1
            
            if next_element.tag == "INIT":
                for i in range(4):
                    if has_called[i]:
                        self.player_data[names[i]]["opened"] += 1
                        has_called[i] = False
                    if has_riichi[i]:
                        self.player_data[names[i]]["riichi"] += 1
                        has_riichi[i] = False
                    self.player_data[names[i]]["rounds"] += 1
            
            next_element = next_element.getnext()
        
        # The final round isn't followed by an init so we do this again
        for i in range(4):
            if has_called[i]:
                self.player_data[names[i]]["opened"] += 1
            if has_riichi[i]:
                self.player_data[names[i]]["riichi"] += 1
            self.player_data[names[i]]["rounds"] += 1
    
    def PrintResults(self):
        print("Name,Games,Rounds,Opened,Dealt In,Won,Riichi,Ron,Total Value,Yakuman,Male")
        
        with open("./results/HououPlayers.csv", "w", encoding="utf8") as f:
            f.write("Name,Games,Rounds,Opened,Dealt In,Won,Riichi,Ron,Total Value,Yakuman,Male\n")

            for player in self.player_data:
                print("%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (
                    player,
                    self.player_data[player]["games"],
                    self.player_data[player]["rounds"],
                    self.player_data[player]["opened"],
                    self.player_data[player]["dealt_in"],
                    self.player_data[player]["won"],
                    self.player_data[player]["riichi"],
                    self.player_data[player]["ron"],
                    self.player_data[player]["total_value"],
                    self.player_data[player]["yakuman"],
                    self.player_data[player]["male"],
                    )
                )
                f.write("%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n" % (
                    player,
                    self.player_data[player]["games"],
                    self.player_data[player]["rounds"],
                    self.player_data[player]["opened"],
                    self.player_data[player]["dealt_in"],
                    self.player_data[player]["won"],
                    self.player_data[player]["riichi"],
                    self.player_data[player]["ron"],
                    self.player_data[player]["total_value"],
                    self.player_data[player]["yakuman"],
                    self.player_data[player]["male"],
                    )
                )