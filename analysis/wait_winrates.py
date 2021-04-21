from analysis_utils import convertTile, discards, GetPreviousRealTag, GetNextRealTag, GetRoundName, CheckSeat, getTilesFromCall, draws, convertHai, convertHandToTenhouString
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from lxml import etree
from ukeire import calculateUkeire
from shanten import calculateMinimumShanten

class WaitWinrates(LogAnalyzer):
    def __init__(self):
        self.counts = defaultdict(Counter)
        self.wins = defaultdict(Counter)
        self.tsumo = defaultdict(Counter)
        self.ron = defaultdict(Counter)
        self.furiten_counts = defaultdict(Counter)
        self.furiten_wins = defaultdict(Counter)
        self.hands = defaultdict(dict)

    def ParseLog(self, log, log_id):
        riichis = log.findall("REACH")

        for riichi in riichis:
            if int(riichi.attrib["step"]) == 1:
                continue
            
            previous = GetPreviousRealTag(riichi)
            if previous.tag == "REACH":
                # there exists one broken replay in the dataset
                continue

            riichi_player = int(riichi.attrib["who"])
            riichi_discard = discards[riichi_player]
            riichi_draw = draws[riichi_player]

            riichi_tile = convertTile(previous.tag[1:])
            previous = GetPreviousRealTag(GetPreviousRealTag(previous))
            discarded_tiles = [False] * 38
            visible_tiles = [0] * 38
            held = [0] * 38
            held[riichi_tile] -= 1
            visible_tiles[riichi_tile] += 1
            discarded_tiles[riichi_tile] = True
            abort = False
            discards_pre_riichi = 0

            # gather the visible tiles and what their hand is
            while previous is not None:
                if previous.tag == "DORA":
                    visible_tiles[convertTile(previous.attrib["hai"])] += 1
                    previous = GetPreviousRealTag(previous)
                    continue
                elif previous.tag[0] in discards:
                    tile = convertTile(previous.tag[1:])
                    visible_tiles[tile] += 1
                    if previous.tag[0] == riichi_discard:
                        discarded_tiles[tile] = True
                        held[tile] -= 1
                        discards_pre_riichi += 1
                elif previous.tag[0] == riichi_draw:
                    tile = convertTile(previous.tag[1:])
                    held[tile] += 1
                elif previous.tag == "N":
                    if int(previous.attrib["who"]) == riichi_player:
                        abort = True
                        break # closed kans are too hard

                    tiles = getTilesFromCall(previous.attrib["m"])
                    if len(tiles) == 3:
                        visible_tiles[tiles[1]] += 1
                        visible_tiles[tiles[2]] += 1
                    elif len(tiles) == 4:
                        visible_tiles[tiles[0]] = 4
                    elif len(tiles) == 1:
                        visible_tiles[tiles[0]] += 1
                elif previous.tag == "REACH":
                    abort = True
                    break
                elif previous.tag == "INIT":
                    indicator = convertTile(previous.attrib["seed"].split(",")[5])
                    visible_tiles[indicator] += 1
                    starting_hand = convertHai(previous.attrib["hai%d" % riichi_player])
                    for i in range(38):
                        held[i] += starting_hand[i]
                    break
                previous = GetPreviousRealTag(previous)
            
            if abort:
                continue

            if discards_pre_riichi < 12:
                continue

            # check if they won
            next_element = GetNextRealTag(riichi)
            while next_element is not None:
                if next_element.tag == "AGARI" or next_element.tag == "RYUUKYOKU":
                    break
                next_element = GetNextRealTag(next_element)

            won = next_element.tag == "AGARI" and int(next_element.attrib["who"]) == riichi_player
            tsumo = False
            if won:
                tsumo = next_element.attrib["who"] == next_element.attrib["fromWho"]

            # check the wait
            remaining_tiles = [4] * 38
            ukeire = calculateUkeire(held, remaining_tiles, calculateMinimumShanten, 0)

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

            visible_outs = 0
            furiten = False
            for i in types:
                visible_outs += min(visible_tiles[i] + held[i], 4)
                if discarded_tiles[i]:
                    furiten = True
            
            if ukeire[0] > 0:
                if visible_outs > ukeire[0] or (won and visible_outs == ukeire[0]):
                    print("%s %s %s %d" % (wait_string, log_id, convertHandToTenhouString(held), visible_outs))
                    print(visible_tiles)

            if furiten:
                self.furiten_counts[wait_string][visible_outs] += 1
                if won:
                    self.furiten_wins[wait_string][visible_outs] += 1
            else:
                self.hands[wait_string][visible_outs] = convertHandToTenhouString(held)
                self.counts[wait_string][visible_outs] += 1
                if won:
                    self.wins[wait_string][visible_outs] += 1
                    if tsumo:
                        self.tsumo[wait_string][visible_outs] += 1
                    else:
                        self.ron[wait_string][visible_outs] += 1

    def PrintResults(self):
        with open("./results/RiichiWaitCounts.csv", "w") as c:
            with open("./results/RiichiWaitWins.csv", "w") as w:
                with open("./results/RiichiWaitTsumo.csv", "w") as t:
                    with open("./results/RiichiWaitRon.csv", "w") as r:
                        with open("./results/RiichiWaitHands.csv", "w") as h:
                            c.write("Wait,Total,0,1,2,3,4,5,6,7,8,9,10,11,12,etc\n")
                            w.write("Wait,Total,0,1,2,3,4,5,6,7,8,9,10,11,12,etc\n")
                            t.write("Wait,Total,0,1,2,3,4,5,6,7,8,9,10,11,12,etc\n")
                            r.write("Wait,Total,0,1,2,3,4,5,6,7,8,9,10,11,12,etc\n")
                            h.write("Wait,Total,0,1,2,3,4,5,6,7,8,9,10,11,12,etc\n")

                            for i in self.counts:
                                c.write("%s,," % i)
                                for j in range(40):
                                    c.write("%d," % self.counts[i][j])
                                c.write("\n")

                                w.write("%s,," % i)
                                for j in range(40):
                                    w.write("%d," % self.wins[i][j])
                                w.write("\n")

                                t.write("%s,," % i)
                                for j in range(40):
                                    t.write("%d," % self.tsumo[i][j])
                                t.write("\n")

                                r.write("%s,," % i)
                                for j in range(40):
                                    r.write("%d," % self.ron[i][j])
                                r.write("\n")

                                h.write("%s,," % i)
                                for j in range(40):
                                    if j in self.hands[i]:
                                        h.write("%s," % self.hands[i][j])
                                    else:
                                        h.write("None,")
                                h.write("\n")
        
        with open("./results/FuritenRiichiWaitCounts.csv", "w") as c:
            with open("./results/FuritenRiichiWaitWins.csv", "w") as w:
                c.write("Wait,Total,0,1,2,3,4,5,6,7,8,9,10,11,12,etc\n")
                w.write("Wait,Total,0,1,2,3,4,5,6,7,8,9,10,11,12,etc\n")

                for i in self.counts:
                    c.write("%s,," % i)
                    for j in range(40):
                        c.write("%d," % self.furiten_counts[i][j])
                    c.write("\n")

                    w.write("%s,," % i)
                    for j in range(40):
                        w.write("%d," % self.furiten_wins[i][j])
                    w.write("\n")