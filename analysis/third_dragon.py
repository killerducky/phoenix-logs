# -*- coding: utf-8 -*-

from log_counter import LogCounter
from analysis_utils import getTilesFromCall, GetWhoTileWasCalledFrom

class ThirdDragon(LogCounter):
    def ParseLog(self, log, log_id):
        rounds = [[]]

        for child in log.getchildren():
            if child.tag == "INIT":
                rounds.append([child])
            else:
                rounds[-1].append(child)

        dragons = [35, 36, 37]
        tenhou_dragons = [124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135]
        discard_tags = ["D", "E", "F", "G"]

        # First group of tags is irrelevant
        for round_ in rounds[1:]:
            caller = -1
            calls = 0
            secondCallIndex = 0
            dragons_found = []
            pao_player = -1

            for element in round_:
                if element.tag == "N":
                    calledTiles = getTilesFromCall(element)
                    if len(calledTiles) < 3:
                        continue
                        
                    who = int(element.attrib["who"])
                    if calledTiles[0] in dragons:
                        if caller == -1 or caller == who:
                            calls += 1
                            caller = who

                            if calls < 3:
                                for i in range(4):
                                    dragons_found.append((calledTiles[0] - 4) * 4 + i)

                            if calls == 2:
                                secondCallIndex = round_.index(element)

                            elif calls == 3:
                                self.Count("Pao Applied")
                                pao_player = GetWhoTileWasCalledFrom(element)
                        else:
                            # Someone else called the second dragon. No need to continue
                            break
            
            if calls < 2:
                continue

            # Count dragons discarded before the second call was made
            dragons_discarded = 0
            
            if "doraHai" in round_[-1].attrib:
                tile = round_[-1].attrib["doraHai"]
                if tile in tenhou_dragons and tile not in dragons_found:
                        dragons_discarded += 1

            for i in range(1, secondCallIndex):
                first_character = round_[i].tag[0]
                if first_character in discard_tags:
                    tile = round_[i].tag[1:]
                    try:
                        tile = int(tile)
                    except ValueError:
                        continue

                    if tile in tenhou_dragons and tile not in dragons_found:
                        if first_character != discard_tags[caller]:
                            dragons_discarded += 1
                        else:
                            dragons_discarded = 2
                            self.Count("Player Called Second Dragon After Discarding Third")
                        break
                
                if round_[i].tag == "DORA":
                    tile = int(round_[i].attrib["hai"])
                    if tile in tenhou_dragons and tile not in dragons_found:
                        dragons_discarded += 1
            
            if dragons_discarded > 1:
                continue
            
            self.Count("Two Dragons Called With Third Live")

            # Look for third dragon discarded after the second call was made
            for i in range(secondCallIndex + 1, len(round_)):
                first_character = round_[i].tag[0]
                if first_character in discard_tags:
                    tile = round_[i].tag[1:]
                    try:
                        tile = int(tile)
                    except ValueError:
                        continue

                    if tile in tenhou_dragons and tile not in dragons_found:
                        if first_character != discard_tags[caller]:
                            self.Count("Third Dragon Discarded With Pao Possible")
                        else:
                            self.Count("Player With Two Dragons Discards Third")
                        break

        wins = log.findall("AGARI")
        for win in wins:
            if "yakuman" in win.attrib:
                yakuman = win.attrib["yakuman"].split(",")
                pao = "paoWho" in win.attrib
                for index in yakuman:
                    if index == "39":
                        if pao:
                            self.Count("Pao Invoked")
                        elif win.attrib["fromWho"] == pao_player:
                            self.Count("Player In Pao Dealt In")
                        else:
                            if "m" not in win.attrib:
                                self.Count("Daisangen Won Without Pao And No Calls")
                            else:
                                calls = len(win.attrib["m"].split(","))
                                self.Count("Daisangen Won Without Pao And %d Call(s)" % calls)

    def GetName(self):
        return "Event"