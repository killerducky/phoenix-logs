from log_analyzer import LogAnalyzer
from analysis_utils import convertTile
from collections import Counter

discards = ['D', 'E', 'F', 'G']

class Matagi(LogAnalyzer):
    def __init__(self):
        self.riichi = [Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter()]
        self.first = [Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter()]
        self.both = [Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter()]
        self.dora = [Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter(),Counter()]
        self.all = Counter()
        self.aidayonken = [Counter(),Counter(),Counter(),Counter()]
        self.aida5ken = [Counter(),Counter(),Counter()]
        self.aida6ken = [Counter(),Counter()]

    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            if not "yaku" in win.attrib:
                continue

            yaku = win.attrib["yaku"].split(",")
            ids = [x for x in yaku[0::2]]
            if "1" not in ids: continue #not riichi

            player_discard = discards[int(win.attrib["who"])]
            discarded_tiles = []
            riichi = False

            previous = win.getprevious()
            while previous is not None:
                if previous.tag == "INIT":
                    break
                if previous.tag == "UN" or previous.tag == "DORA":
                    previous = previous.getprevious()
                    continue
                elif previous.tag[0] == player_discard:
                    if riichi:
                        discarded_tiles.append(convertTile(previous.tag[1:]))
                elif previous.tag == "REACH" and previous.attrib["who"] == win.attrib["who"] and previous.attrib["step"] == "2":
                    riichi = True

                previous = previous.getprevious()

            if len(discarded_tiles) < 3:
                continue

            discarded_tiles.reverse()

            winning_tile = convertTile(win.attrib["machi"])
            winning_tile_value = winning_tile % 10 - 1 # since arrays start at 0, all tile values will be 1 lower than reality
            winning_tile_suit = int(winning_tile / 10)
            self.all[winning_tile] += 1

            if winning_tile > 30:
                winning_tile_value = 9 # 9 is for "other", either another suit or an honor

            # track win rates based on dora
            dora = convertTile(win.attrib["doraHai"].split(",")[0])
            if dora < 30:
                dora_value = dora % 10 - 1
                dora_suit = int(dora / 10)
                adjusted_value = winning_tile_value
                if dora_suit != winning_tile_suit:
                    adjusted_value = 9
                self.dora[dora_value][adjusted_value] += 1

            riichi = discarded_tiles[-1]
            riichi_value = riichi % 10 - 1
            riichi_suit = int(riichi / 10)

            # We do this just to avoid double counting a tile
            first_three = [
                [False,False,False,False,False,False,False,False,False],
                [False,False,False,False,False,False,False,False,False],
                [False,False,False,False,False,False,False,False,False]
            ]

            # Flag which tiles are present in the discards. Change to range(3) for first three discards.
            for i in range(0, len(discarded_tiles) - 1):
                if discarded_tiles[i] < 30:
                    first_three[int(discarded_tiles[i] / 10)][discarded_tiles[i] % 10 - 1] = True
            
            for suit in range(3):
                for value in range(4):
                    if first_three[suit][value] and first_three[suit][value+5]:
                        if not first_three[suit][value+1] and not first_three[suit][value+4]:
                            adjusted_value = winning_tile_value
                            if suit != winning_tile_suit:
                                adjusted_value = 9
                            self.aidayonken[value][adjusted_value] += 1
                for value in range(3):
                    if first_three[suit][value] and first_three[suit][value+6]:
                        adjusted_value = winning_tile_value
                        if suit != winning_tile_suit:
                            adjusted_value = 9
                        self.aida5ken[value][adjusted_value] += 1
                for value in range(2):
                    if first_three[suit][value] and first_three[suit][value+7]:
                        adjusted_value = winning_tile_value
                        if suit != winning_tile_suit:
                            adjusted_value = 9
                        self.aida6ken[value][adjusted_value] += 1

            # loop through the array of flags
            for suit in range(3):
                for value in range(9):
                    # if the flag is set to true
                    if first_three[suit][value]:
                        # if the riichi tile is the same as the flagged tile, count it as being present in both
                        if riichi_value == value and suit == riichi_suit:
                            # if the suit doesn't match the winning tile's suit, set it to be other
                            adjusted_value = winning_tile_value
                            if suit != winning_tile_suit:
                                adjusted_value = 9
                            self.both[value][adjusted_value] += 1
                        # not present in both, only present in the first three
                        else:
                            # if the suit doesn't match the winning tile's suit, set it to be other
                            adjusted_value = winning_tile_value
                            if suit != winning_tile_suit:
                                adjusted_value = 9
                            self.first[value][adjusted_value] += 1
            
            # check that it's only present in the riichi tile and not the first three
            if riichi < 30 and not first_three[riichi_suit][riichi_value]:
                # if the suit doesn't match the winning tile's suit, set it to be other
                if riichi_suit != winning_tile_suit:
                            winning_tile_value = 9
                self.riichi[riichi_value][winning_tile_value] += 1

    def PrintResults(self):
        with open("./results/MatagiAll.csv", "w") as f:
            for i in self.all:
                f.write("%d,%d," % (i, self.all[i]))

        with open("./results/MatagiRiichi.csv", "w") as f:
            f.write("Riichi Tile,1,2,3,4,5,6,7,8,9,Other\n")
            for i in range(9):
                f.write("%d," % i)
                for j in range(10):
                    f.write("%d," % self.riichi[i][j])
                f.write("\n")

        with open("./results/MatagiFirst.csv", "w") as f:
            f.write("Tile In First 3,1,2,3,4,5,6,7,8,9,Other\n")
            for i in range(9):
                f.write("%d," % i)
                for j in range(10):
                    f.write("%d," % self.first[i][j])
                f.write("\n")

        with open("./results/MatagiBoth.csv", "w") as f:
            f.write("Tile Both,1,2,3,4,5,6,7,8,9,Other\n")
            for i in range(9):
                f.write("%d," % i)
                for j in range(10):
                    f.write("%d," % self.both[i][j])
                f.write("\n")
        
        with open("./results/MatagiDora.csv", "w") as f:
            f.write("Dora,1,2,3,4,5,6,7,8,9,Other\n")
            for i in range(9):
                f.write("%d," % i)
                for j in range(10):
                    f.write("%d," % self.dora[i][j])
                f.write("\n")
        
        with open("./results/MatagiAidaYonKen.csv", "w") as f:
            f.write("AidaYonKen,1,2,3,4,5,6,7,8,9,Other\n")
            for i in range(4):
                f.write("%d-%d," % (i+1, i+6))
                for j in range(10):
                    f.write("%d," % self.aidayonken[i][j])
                f.write("\n")
        
        with open("./results/MatagiAida5Ken.csv", "w") as f:
            f.write("Aida5Ken,1,2,3,4,5,6,7,8,9,Other\n")
            for i in range(3):
                f.write("%d-%d," % (i+1, i+7))
                for j in range(10):
                    f.write("%d," % self.aida5ken[i][j])
                f.write("\n")

        with open("./results/MatagiAida6Ken.csv", "w") as f:
            f.write("Aida6Ken,1,2,3,4,5,6,7,8,9,Other\n")
            for i in range(2):
                f.write("%d-%d," % (i+1, i+8))
                for j in range(10):
                    f.write("%d," % self.aida6ken[i][j])
                f.write("\n")