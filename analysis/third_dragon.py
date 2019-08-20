# -*- coding: utf-8 -*-

from log_counter import LogCounter
from log_seat_and_placement import LogSeatAndPlacement
from analysis_utils import getTilesFromCall, GetWhoTileWasCalledFrom, CheckSeat, GetPlacements

class ThirdDragon(LogCounter, LogSeatAndPlacement):
    def __init__(self):
        LogCounter.__init__(self)
        LogSeatAndPlacement.__init__(self)

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
        draw_tags = ["T", "U", "V", "W"]

        # First group of tags is irrelevant
        for round_ in rounds[1:]:
            caller = -1
            calls = 0
            secondCallIndex = 0
            dragons_found = []
            pao_player = -1

            for element in round_:
                if element.tag == "N":
                    calledTiles = getTilesFromCall(element.attrib["m"])
                    # Added kan
                    if len(calledTiles) < 3:
                        continue

                    who = int(element.attrib["who"])
                    if calledTiles[0] in dragons:
                        if caller == -1 or caller == who:
                            calls += 1
                            caller = who

                            if calls < 3:
                                # Build a list of dragons we aren't looking for
                                for i in range(4):
                                    dragons_found.append((calledTiles[0] - 4) * 4 + i)

                            if calls == 2:
                                secondCallIndex = round_.index(element)

                            elif calls == 3:
                                pao_player = (who + GetWhoTileWasCalledFrom(element)) % 4
                        else:
                            # Someone else called the second dragon. No need to continue
                            break
            
            if calls < 2:
                continue

            dealer = int(round_[0].attrib["oya"])
            placements = GetPlacements(round_[0].attrib["ten"], dealer)
            hands = []
            hands.append(list(map(int, round_[0].attrib["hai0"].split(","))))
            hands.append(list(map(int, round_[0].attrib["hai1"].split(","))))
            hands.append(list(map(int, round_[0].attrib["hai2"].split(","))))
            hands.append(list(map(int, round_[0].attrib["hai3"].split(","))))

            # Count dragons discarded before the second call was made
            dragons_visible = 0

            # If the hand was won, we can check the dora to see if it was a dragon
            if "doraHai" in round_[-1].attrib:
                tile = int(round_[-1].attrib["doraHai"].split(",")[0])
                if tile in tenhou_dragons and tile not in dragons_found:
                        dragons_visible += 1

            for i in range(1, secondCallIndex):
                # Someone called kan, see if the new dora is a dragon
                if round_[i].tag == "DORA":
                    tile = int(round_[i].attrib["hai"])
                    if tile in tenhou_dragons and tile not in dragons_found:
                        dragons_visible += 1
                    continue

                first_character = round_[i].tag[0]

                if first_character in draw_tags and first_character != draw_tags[caller]:
                    tile = round_[i].tag[1:]
                    try:
                        tile = int(tile)
                    except ValueError:
                        continue
                    
                    who = draw_tags.index(first_character)
                    hands[who].append(tile)

                if first_character in discard_tags:
                    tile = round_[i].tag[1:]
                    try:
                        tile = int(tile)
                    except ValueError:
                        continue

                    if tile in tenhou_dragons and tile not in dragons_found:
                        if first_character != discard_tags[caller]:
                            dragons_visible += 1
                            who = discard_tags.index(first_character)
                            hands[who].remove(tile)
                        else:
                            dragons_visible = 2
                            self.Count("Player Called Second Dragon After Discarding Third")
                            break

            # Daisangen isn't possible
            if dragons_visible > 1:
                self.Count("Two Dragons Called With Third Dead")
                continue

            self.Count("Two Dragons Called With Third Live")

            # Look for third dragon discarded after the second call was made
            for i in range(secondCallIndex + 1, len(round_)):
                if round_[i].tag == "DORA":
                    tile = int(round_[i].attrib["hai"])
                    if tile in tenhou_dragons and tile not in dragons_found:
                        dragons_visible += 1

                        if dragons_visible == 2:
                            self.Count("Kan Revealed Second of Third Dragon After Two Calls")
                            break
                    continue

                first_character = round_[i].tag[0]

                if first_character in discard_tags:
                    tile = round_[i].tag[1:]
                    try:
                        tile = int(tile)
                    except ValueError:
                        continue

                    if tile in tenhou_dragons and tile not in dragons_found:
                        if first_character != discard_tags[caller]:
                            who = discard_tags.index(first_character)
                            hands[who].remove(tile)

                            dragons_in_hand = 0
                            for tile in hands[who]:
                                if tile in tenhou_dragons and tile not in dragons_found:
                                    dragons_in_hand += 1

                            visible_to_player = dragons_visible + dragons_in_hand

                            if visible_to_player > 1:
                                self.Count("Third Dragon Discarded With 1 Visible While Having Another In Hand")
                                break

                            self.Count("Third Dragon Discarded With Pao Possible And %d Visible" % visible_to_player)
                            self.CountBySeatAndPlacement(
                                "Third Dragon Discarded With Pao Possible And %d Visible" % visible_to_player,
                                CheckSeat(who, dealer),
                                placements[who]
                            )

                            if caller == dealer:
                                self.CountBySeatAndPlacement(
                                    "Third Dragon Discarded With Pao Possible And %d Visible Against Dealer" % visible_to_player,
                                    CheckSeat(who, dealer),
                                    placements[who]
                                )
                            
                            next_element = round_[i].getnext()

                            if next_element.tag == "AGARI":
                                if "yakuman" in next_element.attrib:
                                    if "39" in next_element.attrib["yakuman"].split(","):
                                        self.Count("Dealt Into Daisangen With %d Visible" % visible_to_player)
                                    else:
                                        self.Count("Dealt Into Different Yakuman With %d Visible" % visible_to_player)
                                elif "yaku" in next_element.attrib:
                                    yaku = next_element.attrib["yaku"].split(",")

                                    if "30" in yaku:
                                        self.Count("Dealt Into Shousangen With %d Visible" % visible_to_player)
                                    else:
                                        self.Count("Dealt Into Other Hand With %d Visible" % visible_to_player)
                                
                                value = int(next_element.attrib["ten"].split(",")[1])
                                self.counts["Total Deal-in Value With %d Visible" % visible_to_player] += value
                                self.Count("Deal-in Counts With %d Visible" % visible_to_player)

                            if next_element.tag == "N" and pao_player > -1:
                                self.Count("Pao Applied With %d Visible" % visible_to_player)
                        else:
                            self.Count("Player With Two Dragons Discards Third")
                        break

                if first_character in draw_tags:
                    tile = round_[i].tag[1:]
                    try:
                        tile = int(tile)
                    except ValueError:
                        continue

                    if tile in tenhou_dragons and tile not in dragons_found:
                        if first_character != discard_tags[caller]:
                            self.Count("Third Dragon Drawn After Two Calls")
                            who = draw_tags.index(first_character)
                            hands[who].append(tile)

        wins = log.findall("AGARI")
        for win in wins:
            if "yakuman" in win.attrib:
                yakuman = win.attrib["yakuman"].split(",")
                pao = "paoWho" in win.attrib
                if "39" in yakuman:
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
                            self.Count("Daisangen Won Without Pao And No Calls")
                        else:
                            calls = list(map(getTilesFromCall, win.attrib["m"].split(",")))

                            dragon_calls = 0
                            for call in calls:
                                if call[0] in dragons:
                                    dragon_calls += 1

                            self.Count("Daisangen Won Without Pao And %d Call(s) (%d of which dragons)" % (len(calls), dragon_calls))

    def GetName(self):
        return "Daisangen Event"

    def PrintResults(self):
        LogCounter.PrintResults(self)
        LogSeatAndPlacement.PrintResults(self)