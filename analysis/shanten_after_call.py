from analysis_utils import convertTile, discards, GetPreviousRealTag, GetNextRealTag, GetRoundName, CheckSeat, getTilesFromCall, draws, convertHai, convertHandToTenhouString, GetWhoTileWasCalledFrom
from log_analyzer import LogAnalyzer
from collections import defaultdict, Counter
from lxml import etree
from shanten import calculateStandardShanten
from urllib.parse import unquote

class ShantenAfterCall(LogAnalyzer):
    def __init__(self):
        self.counts = defaultdict(Counter)
        self.shantens = defaultdict(Counter)
        self.tenpais = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        data = log.find("UN")
        tori = -1

        for i in range(4):
            name = unquote(data.attrib["n%d" % i])
            if name == "tori0612":
                tori = i
                break

        if tori == -1:
            return
        calls = log.findall("N")

        for call in calls:
            if GetWhoTileWasCalledFrom(call) == 0:
                # closed kan
                continue

            player = int(call.attrib["who"])
            if player != tori:
                continue

            call_tiles = getTilesFromCall(call.attrib["m"])

            if len(call_tiles) == 1:
                continue
            
            riichi_discard = discards[player]
            riichi_draw = draws[player]
            
            previous = GetPreviousRealTag(call)
            next_discard = convertTile(GetNextRealTag(call).tag[1:])

            held = [0] * 38
            held[call_tiles[1]] -= 1
            held[call_tiles[2]] -= 1
            if len(call_tiles) > 3:
                held[call_tiles[3]] -= 1

            abort = False
            turns = 1
            times_called = 1

            # gather the visible tiles and what their hand is
            while previous is not None:
                if previous.tag == "DORA":
                    pass

                elif previous.tag[0] == riichi_discard:
                    tile = convertTile(previous.tag[1:])
                    held[tile] -= 1
                    turns += 1

                elif previous.tag[0] == riichi_draw:
                    tile = convertTile(previous.tag[1:])
                    held[tile] += 1

                elif previous.tag == "N":
                    if int(previous.attrib["who"]) == player:
                        if GetWhoTileWasCalledFrom(previous) != 0:
                            call_tiles = getTilesFromCall(previous.attrib["m"])

                            if len(call_tiles) == 1:
                                held[call_tiles[0]] -= 1
                            else:
                                times_called += 1
                                if times_called > 3: break

                                held[call_tiles[1]] -= 1
                                held[call_tiles[2]] -= 1

                                if len(call_tiles) > 3:
                                    held[call_tiles[3]] -= 1
                        else:
                            call_tiles = getTilesFromCall(previous.attrib["m"])
                            if len(call_tiles) > 3:
                                # ankan
                                held[call_tiles[1]] -= 4
                                held[31] += 3
                            else:
                                # sanma nuki
                                held[call_tiles[0]] -= 1

                elif previous.tag == "INIT":
                    starting_hand = convertHai(previous.attrib["hai%d" % player])
                    for i in range(38):
                        held[i] += starting_hand[i]
                    break
                previous = GetPreviousRealTag(previous)
            
            if abort:
                continue

            if times_called > 3:
                continue

            held[31] += 3 * times_called
            shanten = calculateStandardShanten(held)

            self.counts[turns][times_called] += 1
            self.shantens[turns][times_called] += shanten

            if shanten == 0:
                self.tenpais[turns][times_called] += 1

    def PrintResults(self):
        with open("./results/ToriCallTurnCounts.csv", "w") as c:
            with open("./results/ToriCallTurnShanten.csv", "w") as s:
                with open("./results/ToriCallTurnTenpais.csv", "w") as t:
                    c.write("Turn,First Call,Second Call,Third Call\n")
                    s.write("Turn,First Call,Second Call,Third Call\n")
                    t.write("Turn,First Call,Second Call,Third Call\n")

                    for i in self.counts:
                        c.write("%d," % i)
                        s.write("%d," % i)
                        t.write("%d," % i)
                        for j in range(1,4):
                            c.write("%d," % self.counts[i][j])
                            s.write("%d," % self.shantens[i][j])
                            t.write("%d," % self.tenpais[i][j])
                        c.write("\n")
                        s.write("\n")
                        t.write("\n")
    
    def GetTypeOfCall(self, call_tiles):
        if call_tiles[0] == call_tiles[1]:
            if call_tiles[0] > 34:
                return "Dragon"
            elif call_tiles[0] < 30 and (call_tiles[0] % 10 == 9 or call_tiles[0] % 10 == 1):
                return "Terminal"
            return "Other"
        if call_tiles[1] + 1 == call_tiles[2] or call_tiles[1] - 1 == call_tiles[2]:
            if call_tiles[1] % 10 == 1 or call_tiles[1] % 10 == 9 or call_tiles[2] % 10 == 1 or call_tiles[2] % 10 == 9:
                return "Penchan"
            return "Ryanmen"
        return "Kanchan"
        