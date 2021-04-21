from log_analyzer import LogAnalyzer
from analysis_utils import convertTile, getTilesFromCall
from collections import Counter, defaultdict

discards = ['D', 'E', 'F', 'G']

class FlushCalls(LogAnalyzer):
    def __init__(self):
        self.one = defaultdict(Counter)
        self.two = defaultdict(Counter)
        self.three = defaultdict(Counter)
        self.four = defaultdict(Counter)

    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            if not "m" in win.attrib:
                continue

            if not "yaku" in win.attrib:
                continue

            player_discard = discards[int(win.attrib["who"])]
            discarded_tiles_after = []
            calls = []
            called = False
            last_call = None

            previous = win.getprevious()
            while previous is not None:
                if previous.tag == "INIT":
                    break
                elif previous.tag == "N" and previous.attrib["who"] == win.attrib["who"]:
                    called = True
                    call = getTilesFromCall(previous.attrib["m"])
                    if len(call) > 1:
                        calls.append(call)

                previous = previous.getprevious()

            discarded_tiles_after.reverse()
            calls.reverse()
            suits = []
            for call in calls:
                suits.append(int(call[0] / 10))
            
            flush_suit = -1
            single_suit = True
            for suit in suits:
                if suit == 3:
                    continue
                if flush_suit == -1:
                    flush_suit = suit
                elif suit != flush_suit:
                    single_suit = False
            
            if not single_suit or flush_suit == -1:
                continue

            calls_string = ""
            for call in calls:
                suit = int(call[0] / 10)
                if suit == 3:
                    calls_string += "Z "
                else:
                    calls_string += "%d%d%d " % (call[0] % 10, call[1] % 10, call[2] % 10)
            calls_string = calls_string.strip()
            
            winning_tile = convertTile(win.attrib["machi"])
            winning_tile_value = winning_tile % 10
            winning_tile_suit = int(winning_tile / 10)

            if winning_tile > 30:
                winning_tile_value = 10
            elif winning_tile_suit != flush_suit:
                winning_tile_value = 11
            
            calls_num = len(calls)

            if calls_num == 1:
                self.one[calls_string][winning_tile_value] += 1
            elif calls_num == 2:
                self.two[calls_string][winning_tile_value] += 1
            elif calls_num == 3:
                self.three[calls_string][winning_tile_value] += 1
            elif calls_num == 4:
                self.four[calls_string][winning_tile_value] += 1


    def PrintResults(self):
        with open("./results/FlushOne.csv", "w") as f:
            f.write("Calls,1,2,3,4,5,6,7,8,9,Z,Other\n")
            for i in self.one:
                f.write("%s," % i)
                for j in range(1,12):
                    f.write("%d," % self.one[i][j])
                f.write("\n")
                
        with open("./results/FlushTwo.csv", "w") as f:
            f.write("Calls,1,2,3,4,5,6,7,8,9,Z,Other\n")
            for i in self.two:
                f.write("%s," % i)
                for j in range(1,12):
                    f.write("%d," % self.two[i][j])
                f.write("\n")

        with open("./results/FlushThree.csv", "w") as f:
            f.write("Calls,1,2,3,4,5,6,7,8,9,Z,Other\n")
            for i in self.three:
                f.write("%s," % i)
                for j in range(1,12):
                    f.write("%d," % self.three[i][j])
                f.write("\n")

        with open("./results/FlushFour.csv", "w") as f:
            f.write("Calls,1,2,3,4,5,6,7,8,9,Z,Other\n")
            for i in self.four:
                f.write("%s," % i)
                for j in range(1,12):
                    f.write("%d," % self.four[i][j])
                f.write("\n")