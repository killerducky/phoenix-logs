# -*- coding: utf-8 -*-

from log_counter import LogCounter

class PaoRates(LogCounter):
    def ParseLog(self, log, log_id):
        wins = log.findall('AGARI')

        for win in wins:
            if "yakuman" in win.attrib:
                yakuman = win.attrib["yakuman"].split(",")
                pao = "paoWho" in win.attrib
                for index in yakuman:
                    if index == "39":
                        self.Count("Daisangen")
                        if pao:
                            self.Count("Daisangen Pao")
                    if index == "49":
                        self.Count("Daisuushii")
                        if pao:
                            self.Count("Daisuushii Pao")

    def GetName(self):
        return "Yakuman"