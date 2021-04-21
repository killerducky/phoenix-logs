from log_analyzer import LogAnalyzer
from analysis_utils import convertHai, convertTile, discards, draws, GetNextRealTag, GetStartingHands, getTilesFromCall
from abc import abstractmethod

class LogHandAnalyzer(LogAnalyzer):
    def __init__(self):
        self.hands = [[], [], [], []]
        self.calls = [[], [], [], []]
        self.discards = [[], [], [], []]
        self.last_draw = [50,50,50,50]
        self.end_round = False
        self.current_log_id = ""
        self.ignore_calls = False

    def ParseLog(self, log, log_id):
        self.current_log_id = log_id
        rounds = log.findall("INIT")

        for round_ in rounds:
            self.RoundStarted(round_)
            next_element = GetNextRealTag(round_)

            while next_element is not None and self.end_round == False:
                if next_element.tag == "DORA":
                    self.DoraRevealed(next_element.attrib["hai"], next_element)

                elif next_element.tag[0] in discards:
                    who = discards.index(next_element.tag[0])
                    tile = convertTile(next_element.tag[1:])
                    self.TileDiscarded(who, tile, tile == self.last_draw[who], next_element)
                    
                elif next_element.tag[0] in draws:
                    who = draws.index(next_element.tag[0])
                    tile = convertTile(next_element.tag[1:])
                    self.last_draw[who] = tile
                    self.TileDrawn(who, tile, next_element)

                elif next_element.tag == "N":
                    if not self.ignore_calls:
                        self.TileCalled(int(next_element.attrib["who"]), getTilesFromCall(next_element.attrib["m"]), next_element)
                
                elif next_element.tag == "REACH":
                    self.RiichiCalled(int(next_element.attrib["who"]), int(next_element.attrib["step"]), next_element)
                
                elif next_element.tag == "INIT":
                    self.RoundEnded(round_)
                    break

                elif next_element.tag == "AGARI":
                    self.Win(next_element)
                
                elif next_element.tag == "RYUUKYOKU":
                    if "type" in next_element.attrib:
                        self.AbortiveDraw(next_element)
                    else:
                        self.ExhaustiveDraw(next_element)

                next_element = GetNextRealTag(next_element)
        
        self.ReplayComplete()
    
    def RoundStarted(self, init):
        self.hands = GetStartingHands(init)
        self.calls = [[], [], [], []]
        self.discards = [[], [], [], []]
        self.end_round = False
    
    def DoraRevealed(self, hai, element):
        pass

    def TileDiscarded(self, who, tile, tsumogiri, element):
        self.hands[who][tile] -= 1
        self.discards[who].append(tile)

    def TileDrawn(self, who, tile, element):
        self.hands[who][tile] += 1

    def TileCalled(self, who, tiles, element):
        length = len(tiles)
        if length == 1:
            self.hands[who][tiles[0]] -= 1
        elif length == 4:
            self.hands[who][tiles[0]] = 0
        else:
            self.hands[who][tiles[1]] -= 1
            self.hands[who][tiles[2]] -= 1
        self.calls[who].append(tiles)

    def RiichiCalled(self, who, step, element):
        pass

    def RoundEnded(self, init):
        pass

    def Win(self, element):
        pass

    def ExhaustiveDraw(self, element):
        pass

    def AbortiveDraw(self, element):
        pass

    def ReplayComplete(self):
        pass
    
    @abstractmethod
    def PrintResults(self):
        pass