# -*- coding: utf-8 -*-

from log_counter import LogCounter
from analysis_utils import getTilesFromCall, GetWhoTileWasCalledFrom

winds = [31, 32, 33, 34]
tenhou_winds = [108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123]
discard_tags = ["D", "E", "F", "G"]
draw_tags = ["T", "U", "V", "W"]

class FourthWind(LogCounter):
    def ParseLog(self, log, log_id):
        rounds = [[]]

        for child in log.getchildren():
            if child.tag == "INIT":
                rounds.append([child])
            else:
                rounds[-1].append(child)

        # First group of tags is irrelevant
        for round_ in rounds[1:]:
            caller = -1
            calls = 0
            thirdCallIndex = 0
            winds_found = []
            pao_player = -1

            for element in round_:
                if element.tag == "N":
                    calledTiles = getTilesFromCall(element.attrib["m"])
                    # Added kan
                    if len(calledTiles) < 3:
                        continue

                    who = int(element.attrib["who"])
                    if calledTiles[0] in winds:
                        if caller == -1 or caller == who:
                            calls += 1
                            caller = who

                            if calls < 4:
                                # Build a list of dragons we aren't looking for
                                for i in range(4):
                                    winds_found.append((calledTiles[0] - 4) * 4 + i)

                            if calls == 3:
                                thirdCallIndex = round_.index(element)

                            elif calls == 4:
                                pao_player = (who + GetWhoTileWasCalledFrom(element)) % 4
                        else:
                            # Someone else called a wind. No need to continue
                            break
            
            if calls < 3:
                continue

            # Count winds discarded before the second call was made
            winds_discarded = 0

            # If the hand was won, we can check the dora to see if it was a wind
            if "doraHai" in round_[-1].attrib:
                tile = int(round_[-1].attrib["doraHai"].split(",")[0])
                if tile in tenhou_winds and tile not in winds_found:
                        winds_discarded += 1

            for i in range(1, thirdCallIndex):
                # Someone called kan, see if the new dora is a wind
                if round_[i].tag == "DORA":
                    tile = int(round_[i].attrib["hai"])
                    if tile in tenhou_winds and tile not in winds_found:
                        winds_discarded += 1
                    continue

                first_character = round_[i].tag[0]
                if first_character in discard_tags:
                    tile = round_[i].tag[1:]
                    try:
                        tile = int(tile)
                    except ValueError:
                        continue

                    if tile in tenhou_winds and tile not in winds_found:
                        if first_character != discard_tags[caller]:
                            winds_discarded += 1
                        else:
                            winds_discarded = 2
                            self.Count("Player Called Third Wind After Discarding Fourth")
                        break

            # Daisuushii isn't possible
            if winds_discarded > 1:
                self.Count("Three Winds Called With Fourth Dead")
                continue

            self.Count("Three Winds Called With Fourth Live")

            # Look for fourth wind discarded after the second call was made
            for i in range(thirdCallIndex + 1, len(round_)):
                if round_[i].tag == "DORA":
                    tile = int(round_[i].attrib["hai"])
                    if tile in tenhou_winds and tile not in winds_found:
                        winds_discarded += 1

                        if winds_discarded == 2:
                            self.Count("Kan Revealed Second of Fourth Wind After Three Calls")
                            break
                    continue

                first_character = round_[i].tag[0]
                if first_character in discard_tags:
                    tile = round_[i].tag[1:]
                    try:
                        tile = int(tile)
                    except ValueError:
                        continue

                    if tile in tenhou_winds and tile not in winds_found:
                        if first_character != discard_tags[caller]:
                            self.Count("Fourth Wind Discarded With Pao Possible And %d Visible" % winds_discarded)
                            next_element = round_[i].getnext()

                            if next_element.tag == "AGARI":
                                if "yakuman" in next_element.attrib:
                                    if "49" in next_element.attrib["yakuman"].split(","):
                                        self.Count("Dealt Into Daisuushii With %d Visible" % winds_discarded)
                                    elif "50" in next_element.attrib["yakuman"].split(","):
                                        self.Count("Dealt Into Shousuushii With %d Visible" % winds_discarded)
                                    else:
                                        self.Count("Dealt Into Different Yakuman With %d Visible" % winds_discarded)
                                elif "yaku" in next_element.attrib:
                                    self.Count("Dealt Into Other Hand With %d Visible" % winds_discarded)
                                
                                value = int(next_element.attrib["ten"].split(",")[1])
                                self.counts["Total Deal-in Value With %d Visible" % winds_discarded] += value
                                self.Count("Deal-in Counts With %d Visible" % winds_discarded)
                            
                            if next_element.tag == "N" and pao_player > -1:
                                self.Count("Pao Applied With %d Visible" % winds_discarded)
                        else:
                            self.Count("Player With Three Winds Discards Fourth")
                        break

                if first_character in draw_tags:
                    tile = round_[i].tag[1:]
                    try:
                        tile = int(tile)
                    except ValueError:
                        continue

                    if tile in tenhou_winds and tile not in winds_found:
                        if first_character != discard_tags[caller]:
                            self.Count("Fourth Wind Drawn After Three Calls")

        wins = log.findall("AGARI")
        for win in wins:
            if "yakuman" in win.attrib:
                yakuman = win.attrib["yakuman"].split(",")
                pao = "paoWho" in win.attrib
                if "49" in yakuman:
                    if pao:
                        if win.attrib["who"] == win.attrib["fromWho"]:
                            self.Count("Pao Invoked via Tsumo")
                        else:
                            self.Count("Pao Invoked via Ron")
                        if win.attrib["paoWho"] == win.attrib["fromWho"]:
                            self.Count("Player In Pao Dealt In")
                    elif int(win.attrib["fromWho"]) == pao_player:
                        self.Count("Player In Pao Dealt In")
                    else:
                        if "m" not in win.attrib:
                            self.Count("Daisuushii Won Without Pao And No Calls")
                        else:
                            calls = list(map(getTilesFromCall, win.attrib["m"].split(",")))

                            wind_calls = 0
                            for call in calls:
                                if call[0] in winds:
                                    wind_calls += 1

                            if len(calls) == 3 and wind_calls == 1:
                                print(log_id)
                                return

                            self.Count("Daisuushii Won Without Pao And %d Call(s) (%d of which winds)" % (len(calls), wind_calls))

    def GetName(self):
        return "Daisuushii Event"