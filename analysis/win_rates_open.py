from log_analyzer import LogAnalyzer
from analysis_utils import convertTile, getTilesFromCall
from collections import Counter, defaultdict

discards = ['D', 'E', 'F', 'G']

class WinRatesOpen(LogAnalyzer):
    def __init__(self):
        self.chii_same = defaultdict(Counter)
        self.chii_diff = defaultdict(Counter)
        self.pon_same = defaultdict(Counter)
        self.pon_diff = defaultdict(Counter)
        self.all = Counter()

    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            if not "m" in win.attrib:
                continue

            if not "yaku" in win.attrib:
                continue

            player_discard = discards[int(win.attrib["who"])]
            discarded_tiles_after = []
            called = False
            last_call = None

            previous = win.getprevious()
            while previous is not None:
                if previous.tag == "INIT":
                    break
                if previous.tag == "UN" or previous.tag == "DORA":
                    previous = previous.getprevious()
                    continue
                elif previous.tag[0] == player_discard:
                    discarded_tiles_after.append(convertTile(previous.tag[1:]))
                elif not called and previous.tag == "N" and previous.attrib["who"] == win.attrib["who"]:
                    called = True
                    last_call = previous.attrib["m"]
                    break

                previous = previous.getprevious()

            call = getTilesFromCall(last_call)
            if len(call) == 4 or len(call) == 1:
                continue

            discarded_tiles_after.reverse()

            tile_after_call = discarded_tiles_after[0]
            tile_after_call_value = tile_after_call % 10
            tile_after_call_suit = int(tile_after_call / 10)
            if tile_after_call_suit == 3:
                continue

            called_value = call[0] % 10
            called_suit = int(call[0] / 10)
            call_was_pon = call[0] == call[1]
            if(called_suit == 3):
                called_value = 10

            winning_tile = convertTile(win.attrib["machi"])
            winning_tile_value = winning_tile % 10
            winning_tile_suit = int(winning_tile / 10)
            self.all[winning_tile] += 1

            if winning_tile > 30:
                winning_tile_value = 10 # 10 is for "other", either another suit or an honor

            adjusted_value = winning_tile_value
            if winning_tile_suit != tile_after_call_suit:
                adjusted_value = 10

            if call_was_pon:
                if called_suit == tile_after_call_suit:
                    self.pon_same["%d->%d" % (called_value, tile_after_call_value)][adjusted_value] += 1
                else:
                    self.pon_diff["%d->%d" % (called_value, tile_after_call_value)][adjusted_value] += 1
            else:
                if called_suit == tile_after_call_suit:
                    self.chii_same["%d%d%d->%d" % (call[0] % 10, call[1] % 10, call[2] % 10, tile_after_call_value)][adjusted_value] += 1
                else:
                    self.chii_diff["%d%d%d->%d" % (call[0] % 10, call[1] % 10, call[2] % 10, tile_after_call_value)][adjusted_value] += 1


    def PrintResults(self):
        with open("./results/CallAll.csv", "w") as f:
            for i in self.all:
                f.write("%d,%d," % (i, self.all[i]))

        with open("./results/CallPonSame.csv", "w") as f:
            f.write("Pon,1,2,3,4,5,6,7,8,9,Other\n")
            for i in self.pon_same:
                f.write("%s," % i)
                for j in range(1,11):
                    f.write("%d," % self.pon_same[i][j])
                f.write("\n")

        with open("./results/CallPonDiff.csv", "w") as f:
            f.write("Pon,1,2,3,4,5,6,7,8,9,Other\n")
            for i in self.pon_diff:
                f.write("%s," % i)
                for j in range(1,11):
                    f.write("%d," % self.pon_diff[i][j])
                f.write("\n")

        with open("./results/CallChiiSame.csv", "w") as f:
            f.write("Chii,1,2,3,4,5,6,7,8,9,Other\n")
            for i in self.chii_same:
                f.write("%s," % i)
                for j in range(1,11):
                    f.write("%d," % self.chii_same[i][j])
                f.write("\n")

        with open("./results/CallChiiDiff.csv", "w") as f:
            f.write("Chii,1,2,3,4,5,6,7,8,9,Other\n")
            for i in self.chii_diff:
                f.write("%s," % i)
                for j in range(1,11):
                    f.write("%d," % self.chii_diff[i][j])
                f.write("\n")