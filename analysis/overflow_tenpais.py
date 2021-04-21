from log_analyzer import LogAnalyzer
from analysis_utils import convertHai, convertTile, GetNextRealTag, GetStartingHands, discards, draws, getTilesFromCall, GetWhoTileWasCalledFrom
from collections import defaultdict, Counter
from shanten import calculateMinimumShanten

class OverflowTenpais(LogAnalyzer):
    def __init__(self):
        self.counts = [defaultdict(Counter),defaultdict(Counter),defaultdict(Counter),defaultdict(Counter),defaultdict(Counter)]
        self.tenpais = [defaultdict(Counter),defaultdict(Counter),defaultdict(Counter),defaultdict(Counter),defaultdict(Counter)]

    def ParseLog(self, log, log_id):
        rounds = log.findall("INIT")

        for round_ in rounds:
            hands = GetStartingHands(round_)
            suit_tiles_discarded = [[0,0,0],[0,0,0],[0,0,0],[0,0,0]]
            calls = [0, 0, 0, 0]
            calls_suit = [-1, -1, -1, -1]
            total_discards = [0,0,0,0]
            shantens = [10,10,10,10]
            last_draw = [50,50,50,50]
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

                    suit = int(tile / 10)
                    if tile < 30:
                        suit_tiles_discarded[who][suit] += 1
                    
                    call_num = calls[who]
                    hand_suit = GetHandSuit(hands[who])

                    if calls_suit[who] > -1:
                        if suit_tiles_discarded[who][calls_suit[who]] > 1:
                            ignore[who] = True
                            continue

                        if suit == calls_suit[who]:
                            suited_tiles = suit_tiles_discarded[who][suit]
                            tedashi = 1

                            if last_draw[who] == tile:
                                tedashi = 2

                            self.counts[call_num][total_discards[who]][tedashi] += 1
                            self.tenpais[call_num][total_discards[who]][tedashi] += GetDistanceFromFlush(hands[who], calls_suit[who])
                            
                            ignore[who] = True
                        elif suit_tiles_discarded[who][calls_suit[who]] == 0:
                            self.counts[call_num][total_discards[who]][0] += 1
                            self.tenpais[call_num][total_discards[who]][0] += GetDistanceFromFlush(hands[who], calls_suit[who])

                elif next_element.tag[0] in draws:
                    who = draws.index(next_element.tag[0])
                    if ignore[who]:
                        next_element = GetNextRealTag(next_element)
                        continue
                    tile = convertTile(next_element.tag[1:])
                    hands[who][tile] += 1
                    last_draw[who] = tile

                elif next_element.tag == "N":
                    who = int(next_element.attrib["who"])
                    if ignore[who]:
                        next_element = GetNextRealTag(next_element)
                        continue

                    tiles = getTilesFromCall(next_element.attrib["m"])
                    
                    if len(tiles) > 1:
                        tile_suit = int(tiles[0] / 10)
                        calls[who] += 1

                        if calls_suit[who] == -1:
                            if tile_suit < 3:
                                calls_suit[who] = tile_suit
                        else:
                            if calls_suit[who] == tile_suit or tile_suit == 3:
                                pass
                            else:
                                ignore[who] = True
                        if len(tiles) == 4:
                            hands[who][tiles[0]] = 0
                        else:
                            hands[who][tiles[1]] -= 1
                            hands[who][tiles[2]] -= 1
                        hands[who][31] += 3
                    else:
                        hands[who][tiles[0]] -= 1
                
                elif next_element.tag == "REACH" and int(next_element.attrib["step"]) == 2:
                    break

                elif next_element.tag == "INIT":
                    break

                next_element = GetNextRealTag(next_element)
            
    def PrintResults(self):
        for calls in range(1,5):
            with open("./results/OverflowCounts%dCalls.csv" % calls, "w") as c:
                with open("./results/OverflowDistanceCounts%dCalls.csv" % calls, "w") as w:
                    c.write("Discard,None,Tedashi,Tsumogiri\n")
                    w.write("Discard,None,Tedashi,Tsumogiri\n")
                    for i in range(1,21):
                        c.write("%d," % i)
                        for j in range(3):
                            c.write("%d," % self.counts[calls][i][j])
                        c.write("\n")

                        w.write("%d," % i)
                        for j in range(3):
                            w.write("%d," % self.tenpais[calls][i][j])
                        w.write("\n")

def GetHandSuit(hand):
    suits_found = []

    i = 1
    while i < 30:
        if hand[i] > 0:
            suit = int(i / 10)
            suits_found.append(suit)
            if len(suits_found) > 1:
                return -1
            i = suit + 10
        i += 1
    
    if len(suits_found) == 0:
        return 3
    return suits_found[0]

def GetDistanceFromFlush(hand, suit):
    suit_counts = [sum(hand[1:9]), sum(hand[11:19]), sum(hand[21:29])]
    suit_counts.remove(suit_counts[suit])
    return sum(suit_counts)