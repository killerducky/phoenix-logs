from log_counter import LogCounter

discard_tags = ["D", "E", "F", "G"]

class RoundLength(LogCounter):
    def ParseLog(self, log, log_id):
        rounds = [[]]

        for child in log.getchildren():
            if child.tag == "INIT":
                rounds.append([child])
            else:
                rounds[-1].append(child)

        
        for round_ in rounds[1:]:
            discards = 0
            quick_abort = False

            for element in round_:
                if discards < 5 and element.tag == "RYUUKYOKU":
                    quick_abort = True
                    break

                first_character = element.tag[0]

                if first_character in discard_tags:
                    tile = element.tag[1:]
                    try:
                        tile = int(tile)
                    except ValueError:
                        continue
                    discards += 1
            
            if quick_abort == False:
                self.Count(discards)
    
    def GetName(self):
        return "Discards in Round"
                    