# -*- coding: utf-8 -*-

from log_counter import LogCounter

class EndResults(LogCounter):
    def ParseLog(self, log, log_id):
        wins = log.findall('AGARI')
        double_ron = False

        for win in wins:
            if double_ron == True:
                double_ron == False
                continue
            
            self.Count("Rounds")
            if win.attrib['who'] == win.attrib['fromWho']:
                self.Count("Tsumo")
            else:
                next_element = win.getnext()
                if next_element is not None and next_element.tag == "AGARI":
                    self.Count("Double Ron")
                    double_ron = True
                else:
                    self.Count("Ron")
        
        draws = log.findall('RYUUKYOKU')

        for draw in draws:
            self.Count("Rounds")
            if 'type' not in draw.attrib:
                self.Count("Exhaustive Draw")
                continue
            
            self.Count(draw.attrib['type'])

    def GetName(self):
        return "End Result"