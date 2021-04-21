from log_analyzer import LogAnalyzer
from collections import Counter, defaultdict
from analysis_utils import GetWhoTileWasCalledFrom
from urllib.parse import unquote

NUM_PLAYERS = 4

class HououStreaks(LogAnalyzer):
    def __init__(self):
        self.player_data = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        names = ["", "", "", ""]
        won = [False, False, False, False]
        dealt_in = [False, False, False, False]
        
        listTree = list(log)
        lastElement = listTree[-1]
        if 'owari' not in lastElement.attrib:
            return

        data = log.find("UN")
        genders = data.attrib["sx"].split(",")

        for i in range(NUM_PLAYERS):
            names[i] = unquote(data.attrib["n%d" % i])
            self.player_data[names[i]]["games"] += 1
        
        wins = log.findall("AGARI")

        for win in wins:
            who = int(win.attrib["who"])
            fromWho = int(win.attrib["fromWho"])
            won[who] = True

            if who != fromWho:
                dealt_in[fromWho] = True

        
        scores = list(map(int, lastElement.attrib["owari"].split(",")[0::2]))
        sorted_scores = scores.copy()
        sorted_scores.sort(reverse=True)
        
        for i in range(NUM_PLAYERS):
            placement = sorted_scores.index(scores[i]) + 1
            current_player = self.player_data[names[i]]
            last_placement = current_player["Last Placement"]

            if last_placement != placement:
                current_player["Last Placement"] = placement
                current_player["Current Streak"] = 1
                if current_player["Current Streak"] > current_player["Best %d Streak" % placement]:
                    current_player["Best %d Streak" % placement] = current_player["Current Streak"]
            else:
                current_player["Last Placement"] = placement
                current_player["Current Streak"] += 1
                if current_player["Current Streak"] > current_player["Best %d Streak" % placement]:
                    current_player["Best %d Streak" % placement] = current_player["Current Streak"]
            
            for j in range(1,5):
                if placement == j:
                    current_player["Current No %d Streak" % j] = 0
                else:
                    current_player["Current No %d Streak" % j] += 1
                    if current_player["Current No %d Streak" % j] > current_player["Longest No %d Streak" % j]:
                        current_player["Longest No %d Streak" % j] = current_player["Current No %d Streak" % j]
        
            if won[i]:
                current_player["Yakitori Streak"] = 0
            else:
                current_player["Yakitori Streak"] += 1
                if current_player["Yakitori Streak"] > current_player["Best Yakitori Streak"]:
                    current_player["Best Yakitori Streak"] = current_player["Yakitori Streak"]

            if dealt_in[i]:
                current_player["No Deal-In Streak"] = 0
            else:
                current_player["No Deal-In Streak"] += 1
                if current_player["No Deal-In Streak"] > current_player["Best No Deal-In Streak"]:
                    current_player["Best No Deal-In Streak"] = current_player["No Deal-In Streak"]
    
    def PrintResults(self):
        print("Name,Games,Yakitori,No Dealin,First,Second,Third,Fourth")
        
        with open("./results/HououStreaks.csv", "w", encoding="utf8") as f:
            f.write("Name,Games,Yakitori,No Deal-In,First,Second,Third,Fourth,No First,No Second,No Third,No Fourth\n")

            for player in self.player_data:
                #if self.player_data[player]["games"] < 100:
                    #continue
                print("%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (
                    player,
                    self.player_data[player]["games"],
                    self.player_data[player]["Best Yakitori Streak"],
                    self.player_data[player]["Best No Deal-In Streak"],
                    self.player_data[player]["Best 1 Streak"],
                    self.player_data[player]["Best 2 Streak"],
                    self.player_data[player]["Best 3 Streak"],
                    self.player_data[player]["Best 4 Streak"],
                    self.player_data[player]["Longest No 1 Streak"],
                    self.player_data[player]["Longest No 2 Streak"],
                    self.player_data[player]["Longest No 3 Streak"],
                    self.player_data[player]["Longest No 4 Streak"]
                    )
                )
                f.write("%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n" % (
                    player,
                    self.player_data[player]["games"],
                    self.player_data[player]["Best Yakitori Streak"],
                    self.player_data[player]["Best No Deal-In Streak"],
                    self.player_data[player]["Best 1 Streak"],
                    self.player_data[player]["Best 2 Streak"],
                    self.player_data[player]["Best 3 Streak"],
                    self.player_data[player]["Best 4 Streak"],
                    self.player_data[player]["Longest No 1 Streak"],
                    self.player_data[player]["Longest No 2 Streak"],
                    self.player_data[player]["Longest No 3 Streak"],
                    self.player_data[player]["Longest No 4 Streak"]
                    )
                )