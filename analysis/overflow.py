from log_analyzer import LogAnalyzer
from analysis_utils import convertHai, convertTile, GetNextRealTag, GetStartingHands, discards, draws, getTilesFromCall, GetWhoTileWasCalledFrom
from collections import defaultdict, Counter

class Overflow(LogAnalyzer):
    def __init__(self):
        self.counts = [defaultdict(Counter),defaultdict(Counter),defaultdict(Counter),defaultdict(Counter),defaultdict(Counter)]
        self.flushes = [defaultdict(Counter),defaultdict(Counter),defaultdict(Counter),defaultdict(Counter),defaultdict(Counter)]

    def ParseLog(self, log, log_id):
        rounds = log.findall("INIT")

        for round_ in rounds:
            hands = GetStartingHands(round_)
            suit_tiles_discarded = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
            calls = [0, 0, 0, 0]
            calls_suit = [-1, -1, -1, -1]
            total_discards = [0,0,0,0]
            ignore = [False, False, False, False]

            next_element = GetNextRealTag(round_)

            while next_element is not None:
                if next_element.tag == "DORA":
                    pass

                elif next_element.tag[0] in discards:
                    who = discards.index(next_element.tag[0])
                    if ignore[who]:
                        next_element = GetNextRealTag(next_element)
                        continue
                    total_discards[who] += 1
                    tile = convertTile(next_element.tag[1:])
                    hands[who][tile] -= 1

                    suit = int((tile - tile % 10) / 10)
                    if tile < 30:
                        suit_tiles_discarded[who][suit] += 1
                    
                    call_num = calls[who]
                    hand_suit = GetHandSuit(hands[who])
                    if call_num == 0: 
                        fewest = min(suit_tiles_discarded[who])

                        if fewest == 0:
                            self.counts[call_num][total_discards[who]][0] += 1
                            if hand_suit >= 0:
                                self.flushes[call_num][total_discards[who]][0] += 1
                        elif suit < 3:
                            if fewest == suit_tiles_discarded[who][suit]:
                                self.counts[call_num][total_discards[who]][fewest] += 1
                                if hand_suit == suit:
                                    self.flushes[call_num][total_discards[who]][fewest] += 1
                    elif calls_suit[who] > -1:
                        if suit == calls_suit[who]:
                            suited_tiles = suit_tiles_discarded[who][suit]
                            self.counts[call_num][total_discards[who]][suited_tiles] += 1
                            if hand_suit >= 0:
                                self.flushes[call_num][total_discards[who]][suited_tiles] += 1
                        elif suit_tiles_discarded[who][calls_suit[who]] == 0:
                            self.counts[call_num][total_discards[who]][0] += 1
                            if hand_suit >= 0:
                                self.flushes[call_num][total_discards[who]][0] += 1
                    self.counts[call_num][total_discards[who]]["Total"] += 1
                    if hand_suit >= 0:
                        self.flushes[call_num][total_discards[who]]["Total"] += 1
                    
                elif next_element.tag[0] in draws:
                    who = draws.index(next_element.tag[0])
                    if ignore[who]:
                        next_element = GetNextRealTag(next_element)
                        continue
                    tile = convertTile(next_element.tag[1:])
                    hands[who][tile] += 1

                elif next_element.tag == "N":
                    who = int(next_element.attrib["who"])
                    if ignore[who]:
                        next_element = GetNextRealTag(next_element)
                        continue

                    tiles = getTilesFromCall(next_element.attrib["m"])
                    
                    if len(tiles) > 1:
                        hands[who][tiles[0]] += 1
                        tile_suit = int((tiles[0] - tiles[0] % 10) / 10)
                        calls[who] += 1

                        if calls[who] > 4:
                            print(log_id)

                        if calls_suit[who] == -1:
                            if tile_suit < 3:
                                calls_suit[who] = tile_suit
                        else:
                            if calls_suit[who] == tile_suit or tile_suit == 3:
                                pass
                            else:
                                ignore[who] = True
                
                elif next_element.tag == "REACH" and int(next_element.attrib["step"]) == 2:
                    break
                
                elif next_element.tag == "INIT":
                    break

                next_element = GetNextRealTag(next_element)
            
    def PrintResults(self):
        for calls in range(4):
            with open("./results/OverflowCounts%dCalls.csv" % calls, "w") as c:
                with open("./results/OverflowFlushes%dCalls.csv" % calls, "w") as w:
                    c.write("Discard,Total,None,1st,2nd,3rd,4th,5th,6th,7th\n")
                    w.write("Discard,Total,None,1st,2nd,3rd,4th,5th,6th,7th\n")
                    for i in range(1,21):
                        c.write("%d,%d," % (i, self.counts[calls][i]["Total"]))
                        for j in range(8):
                            c.write("%d," % self.counts[calls][i][j])
                        c.write("\n")

                        w.write("%d,%d," % (i, self.flushes[calls][i]["Total"]))
                        for j in range(8):
                            w.write("%d," % self.flushes[calls][i][j])
                        w.write("\n")

def GetHandSuit(hand):
    suits_found = []

    i = 1
    while i < 30:
        if hand[i] > 0:
            suit = i - i % 10
            suits_found.append(int(suit / 10))
            if len(suits_found) > 1:
                return -1
            i = suit + 10
        i += 1
    
    if len(suits_found) == 0:
        return 3
    return suits_found[0]
            