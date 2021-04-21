from log_analyzer import LogAnalyzer
from collections import Counter, defaultdict
from analysis_utils import CheckDoubleRon, convertTile, convertHai, GetNextRealTag
import math

dragons = [ 35, 36, 37 ]
draws = ['T', 'U', 'V', 'W']
discards = ['D', 'E', 'F', 'G']
NUM_PLAYERS = 4

class DragonPair(LogAnalyzer):
    def __init__(self):
        self.results = defaultdict(Counter)
        self.total_hands = 0
        self.pair = 0
        self.two_pairs = 0
        self.three_pairs = 0

    def ParseLog(self, log, log_id):
        rounds = log.findall('INIT')

        for round_ in rounds:
            dora_ind = convertTile(round_.attrib["seed"].split(",")[5])
            if dora_ind in dragons:
                continue

            player_hands = [[], [], [], []]
            for i in range(NUM_PLAYERS):
                player_hands[i] = convertHai(round_.attrib['hai%d' % i])
            self.total_hands += NUM_PLAYERS

            for player in range(NUM_PLAYERS):
                pairs = 0
                for dragon in range(35, 38):
                    if player_hands[player][dragon] >= 2:
                        self.Search(player, dragon, round_, player_hands)
                        pairs += 1
                
                if pairs == 1:
                    self.pair += 1
                if pairs == 2:
                    self.two_pairs += 1
                if pairs == 3:
                    self.three_pairs += 1
    
    def Search(self, player, dragon, init, player_hands):
        next_element = GetNextRealTag(init)
        discard_count = 0
        drawn = False
        pair_locked = False

        for i in range(NUM_PLAYERS):
            if i == player:
                continue
            if player_hands[i][dragon] == 1:
                drawn = True
            elif player_hands[i][dragon] == 2:
                pair_locked = True

        while next_element is not None:
            name = next_element.tag

            if name == "UN" or name == "DORA":
                next_element = next_element.getnext()
                continue

            if name[0] in draws:
                tile = convertTile(name[1:])
                if tile == dragon:
                    if name[0] == draws[player]:
                        self.results[self.GetTurn(discard_count)]["Drew Third Dragon"] += 1
                        return
                    else:
                        drawn = True
                        player_hands[draws.index(name[0])][tile] += 1
                        if player_hands[draws.index(name[0])][tile] == 2:
                            pair_locked = True

            elif name[0] in discards:
                discard_count += 1
                self.results[self.GetTurn(discard_count)]["Discards Made"] += 1
                if convertTile(name[1:]) == dragon:
                    if name[0] == discards[player]:
                        self.results[self.GetTurn(discard_count)]["Discarded From Pair"] += 1
                        return
                    else:
                        self.results[self.GetTurn(discard_count)]["Third Dragon Discarded"] += 1
                        next_real = GetNextRealTag(next_element)
                        if next_real.tag == "N":
                            self.results[self.GetTurn(discard_count)]["Dragon Called"] += 1
                        elif next_real.tag == "AGARI":
                            self.results[self.GetTurn(discard_count)]["Dragon Ronned"] += 1
                        else:
                            self.results[self.GetTurn(discard_count)]["Dragon Passed"] += 1
                        return

            elif name == "REACH":
                if next_element.attrib["who"]:
                    self.results[self.GetTurn(discard_count)]["Called Riichi Before Calling"] += 1
                    if pair_locked:
                        self.results[self.GetTurn(discard_count)]["Pair Locked"] += 1
                    elif drawn:
                        self.results[self.GetTurn(discard_count)]["Third Never Discarded"] += 1
                    else:
                        self.results[self.GetTurn(discard_count)]["Third Never Drawn"] += 1
                    return

            elif name == "AGARI" or name == "RYUUKYOKU":
                if pair_locked:
                    self.results[self.GetTurn(discard_count)]["Pair Locked"] += 1
                elif drawn:
                    self.results[self.GetTurn(discard_count)]["Third Never Discarded"] += 1
                else:
                    self.results[self.GetTurn(discard_count)]["Third Never Drawn"] += 1
                return

            next_element = GetNextRealTag(next_element)
        return
    
    def GetTurn(self, discard_count):
        return "Turn %d" % math.ceil(discard_count / 4)

    def PrintResults(self):
        with open("./results/%s.csv" % self.GetName(), "w") as f:
            print("Turn,Self Drawn,Self Discarded,Discarded,Called,Ronned,Passed,Pair Locked,Never Discarded,Never Drawn,Riichi,Discards Total")
            f.write("Turn,Self Drawn,Self Discarded,Discarded,Called,Ronned,Passed,Pair Locked,Never Discarded,Never Drawn,Riichi,Discards Total\n")
            for i in self.results:
                print("%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d" % (
                    i,
                    self.results[i]["Drew Third Dragon"],
                    self.results[i]["Discarded From Pair"],
                    self.results[i]["Third Dragon Discarded"],
                    self.results[i]["Dragon Called"],
                    self.results[i]["Dragon Ronned"],
                    self.results[i]["Dragon Passed"],
                    self.results[i]["Pair Locked"],
                    self.results[i]["Third Never Discarded"],
                    self.results[i]["Third Never Drawn"],
                    self.results[i]["Called Riichi Before Calling"],
                    self.results[i]["Discards Made"]
                ))
                f.write("%s,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d,%d\n" % (
                    i,
                    self.results[i]["Drew Third Dragon"],
                    self.results[i]["Discarded From Pair"],
                    self.results[i]["Third Dragon Discarded"],
                    self.results[i]["Dragon Called"],
                    self.results[i]["Dragon Ronned"],
                    self.results[i]["Dragon Passed"],
                    self.results[i]["Pair Locked"],
                    self.results[i]["Third Never Discarded"],
                    self.results[i]["Third Never Drawn"],
                    self.results[i]["Called Riichi Before Calling"],
                    self.results[i]["Discards Made"]
                ))
        
        print("Hands: %d" % self.total_hands)
        print("Pair: %d" % self.pair)
        print("Two Pairs: %d" % self.two_pairs)
        print("Three Pairs: %d" % self.three_pairs)

    def GetName(self):
        return "Dragon Pair Call"