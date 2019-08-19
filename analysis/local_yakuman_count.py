from log_counter import LogCounter
from analysis_utils import convertHai

discard_tags = ["D", "E", "F", "G"]

class LocalYakumanCount(LogCounter):
    def ParseLog(self, log, log_id):
        wins = log.findall("AGARI")

        for win in wins:
            # Daichisei
            if "yakuman" in win.attrib:
                if "42" in win.attrib["yakuman"].split(",") and "m" not in win.attrib:
                    hand = convertHai(win.attrib["hai"])
                    daichisei = True
                    for i in hand:
                        if i > 2:
                            daichisei = False
                    
                    if daichisei:
                        self.Count("Daichisei")
            
            # Three years on the stone
            if "yaku" in win.attrib:
                yaku = win.attrib["yaku"].split(",")
                if "21" in yaku and "5" in yaku:
                    self.Count("Ishinouenimosannen")

        # Renhou
        rounds = [[]]

        for child in log.getchildren():
            if child.tag == "INIT":
                rounds.append([child])
            else:
                rounds[-1].append(child)

        for round_ in rounds[1:]:
            discards = 0
            has_discarded = [False, False, False, False]

            for element in round_:
                if discards >= 3:
                    break

                first_character = element.tag[0]

                if first_character in discard_tags:
                    tile = element.tag[1:]
                    try:
                        tile = int(tile)
                        discards += 1
                        has_discarded[discard_tags.index(first_character)] = True
                    except ValueError:
                        continue

                if first_character == "N":
                    break
                
                if element.tag == "AGARI":
                    if element.attrib["who"] == element.attrib["fromWho"]:
                        break
                    
                    if has_discarded[int(element.attrib["who"])] == True:
                        break

                    self.Count("Renhou")
    
    def GetName(self):
        return "Local Yakuman"
                    