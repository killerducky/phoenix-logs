from analysis_utils import convertTile, discards, GetPreviousRealTag, GetNextRealTag, GetRoundName, CheckSeat, getTilesFromCall, draws, convertHai, convertHandToTenhouString
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from lxml import etree
from tenpai_waits import calculateWaits
from shanten import calculateMinimumShanten
import math
import copy

class WaitWinratesDama(LogAnalyzer):
    def __init__(self):
        self.wait_counts = [defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)]
        self.wins = [defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)]

        self.damas = defaultdict(Counter)
        self.dama_counts = defaultdict(Counter)
        self.dama_outcomes = [defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)]

    def ParseLog(self, log, log_id):
        rounds = log.findall("INIT")

        for round_ in rounds:
            held = [[0] * 38, [0] * 38, [0] * 38, [0] * 38]

            for i in range(4):
                hand = convertHai(round_.attrib['hai%d' % i])
                for tile in range(38):
                    held[i][tile] = hand[tile]

            discarded_tiles = [[False] * 38, [False] * 38, [False] * 38, [False] * 38]
            dont_calculate = [False] * 4
            visible_tiles = [0] * 38
            discard_count = 0
            indicator = convertTile(round_.attrib["seed"].split(",")[5])
            visible_tiles[indicator] += 1
            next_element = GetNextRealTag(round_)
            abort = False
            winner = -1
            events = [[],[],[],[]]

            while next_element is not None:
                if next_element.tag == "DORA":
                    visible_tiles[convertTile(next_element.attrib["hai"])] += 1
                    next_element = GetNextRealTag(next_element)
                    continue
                elif next_element.tag[0] in discards:
                    tile = convertTile(next_element.tag[1:])
                    visible_tiles[tile] += 1
                    player = discards.index(next_element.tag[0])
                    discarded_tiles[player][tile] = True
                    held[player][tile] -= 1
                    discard_count += 1

                    if not dont_calculate[player]:
                        peek = GetPreviousRealTag(next_element)
                        if peek.tag[0] == draws[player] and peek.tag[1:] == next_element.tag[1:]:
                            # Tsumogiri
                            next_element = GetNextRealTag(next_element)
                            continue
                        shanten = calculateMinimumShanten(held[player])
                        if shanten == 0:
                            decision = "DAMA"
                            if peek.tag == "REACH":
                                decision = "RIICHI"
                            wait = calculate_wait(held[player])
                            events[player].append([decision, wait, copy.deepcopy(held[player]), discard_count])
                            if peek.tag == "REACH":
                                break
                elif next_element.tag[0] in draws:
                    tile = convertTile(next_element.tag[1:])
                    player = draws.index(next_element.tag[0])
                    held[player][tile] += 1
                elif next_element.tag == "N":
                    player = int(next_element.attrib["who"])
                    dont_calculate[player] = True
                    tiles = getTilesFromCall(next_element.attrib["m"])
                    if len(tiles) == 3:
                        visible_tiles[tiles[1]] += 1
                        visible_tiles[tiles[2]] += 1
                    elif len(tiles) == 4:
                        visible_tiles[tiles[0]] = 4
                    elif len(tiles) == 1:
                        visible_tiles[tiles[0]] += 1
                elif next_element.tag == "AGARI" or next_element.tag == "RYUUKYOKU":
                    break
                next_element = GetNextRealTag(next_element)
            
            if len(events[0]) == 0 and len(events[1]) == 0 and len(events[2]) == 0 and len(events[3]) == 0:
                continue

            # check who won
            while next_element is not None:
                if next_element.tag == "AGARI" or next_element.tag == "RYUUKYOKU":
                    break
                next_element = GetNextRealTag(next_element)

            if next_element.tag == "AGARI":
                winner = int(next_element.attrib["who"])

            for i in range(4):
                if len(events[i]) == 0:
                    continue
                # Event format: Decision / Wait / Hand / Discards
                first = events[i][0]
                discards_ = first[3]
                row = min(2, int((discards_ / 4) / 6))
                self.dama_counts[first[1][0]][int(discards_ / 4)] += 1
                if first[0] == "DAMA":
                    self.damas[first[1][0]][int(discards_ / 4)] += 1
                    
                    if i == winner:
                        self.dama_outcomes[row][first[1][0]]["Won"] += 1
                    
                    if len(events[i]) > 1:
                        next_event = events[i][1]
                        if next_event[0] == "FURITEN RIICHI":
                            self.dama_outcomes[row][first[1][0]]["Furiten Riichi"] += 1
                        elif next_event[0] == "DAMA" and first[1][0] != next_event[1][0]:
                            self.dama_outcomes[row][first[1][0]]["Changed Wait > Stayed Dama"] += 1
                        elif next_event[0] == "RIICHI" and first[1][0] != next_event[1][0]:
                            self.dama_outcomes[row][first[1][0]]["Changed Wait > Riichi"] += 1
                        elif next_event[0] == "RIICHI":
                            self.dama_outcomes[row][first[1][0]]["Riichi Later"] += 1
                
                for event in events[i]:
                    if event[0] == "DAMA":
                        wait_string = event[1][0]
                        ukeire = event[1][1]
                        types = ukeire[1]
                        row = min(2, int((event[3] / 4) / 6))

                        visible_outs = 0
                        for tile in types:
                            visible_outs += min(visible_tiles[tile] + event[2][tile], 4)

                        self.wait_counts[row][wait_string][visible_outs] += 1
                        if i == winner:
                            self.wins[row][wait_string][visible_outs] += 1

    def PrintResults(self):
        for row in range(3):
            with open("./results/DamaWaitCountsR%d.csv" % row, "w") as c:
                with open("./results/DamaWaitWinsR%d.csv" % row, "w") as w:
                    with open("./results/DamaCounts.csv", "w") as dc:
                        with open("./results/DamaOutcomes%d.csv" % row, "w") as do:
                            with open("./results/Damas.csv", "w") as d:
                                c.write("Wait,Total,0,1,2,3,4,5,6,7,8,9,10,11,12,etc\n")
                                w.write("Wait,Total,0,1,2,3,4,5,6,7,8,9,10,11,12,etc\n")
                                do.write("Wait,Won,Furiten Riichi,Changed Wait > Stayed Dama,Changed Wait > Riichi,Riichi Later\n")
                                dc.write("Wait,Total,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20\n")
                                d.write("Wait,Total,0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20\n")

                                for i in self.wait_counts[row]:
                                    c.write("%s,," % i)
                                    for j in range(40):
                                        c.write("%d," % self.wait_counts[row][i][j])
                                    c.write("\n")

                                    w.write("%s,," % i)
                                    for j in range(40):
                                        w.write("%d," % self.wins[row][i][j])
                                    w.write("\n")

                                    do.write("%s,%d,%d,%d,%d,%d\n" % (
                                        i,
                                        self.dama_outcomes[row][i]["Won"],
                                        self.dama_outcomes[row][i]["Furiten Riichi"],
                                        self.dama_outcomes[row][i]["Changed Wait > Stayed Dama"],
                                        self.dama_outcomes[row][i]["Changed Wait > Riichi"],
                                        self.dama_outcomes[row][i]["Riichi Later"]
                                    ))

                                    dc.write("%s,," % i)
                                    for j in range(1,21):
                                        dc.write("%d," % self.dama_counts[i][j])
                                    dc.write("\n")

                                    d.write("%s,," % i)
                                    for j in range(1,21):
                                        d.write("%d," % self.damas[i][j])
                                    d.write("\n")

def calculate_wait(hand):
    remaining_tiles = [4] * 38
    ukeire = calculateWaits(hand, remaining_tiles)

    types = ukeire[1]

    waits = []
    wait = ""
    for i in range(1, 10):
        if i in types:
            wait += str(i)
    if wait != "":
        waits.append(wait)

    wait = ""
    for i in range(11, 20):
        if i in types:
            wait += str(i % 10)
    if wait != "":
        waits.append(wait)

    wait = ""
    for i in range(21, 30):
        if i in types:
            wait += str(i % 10)
    if wait != "":
        waits.append(wait)

    for i in range(31,38):
        if i in types:
            waits.append("Z")
    
    waits.sort()
    wait_string = '+'.join(waits)

    if ukeire[0] == 0:
        wait_string = "Z"

    return [wait_string, ukeire]