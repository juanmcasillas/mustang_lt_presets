#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ############################################################################
#
# sheet_2_json.py
# 11/02/2026 (c) Juan M. Casillas <juanm.casillas@gmail.com>
#
# read the google spreadsheet with Mustang LT profiles, do some json
# to avoid all the drama with URL auth, export the file and use it
# locally
#
# ############################################################################


import openpyxl
import pprint
import numbers

class Sheet2Json:
    def __init__(self, url):
        self.url = url
        self.wb = None

    def load(self):
        self.wb = openpyxl.load_workbook(self.url)
        # the file has two main sheets: "goated" and "(525) Archive"

        self.sheets = {
            "goated":          ( self.wb["goated"], self.run_goated )
            # "(525 Archive)": ( self.wb["(525) Archive"], self.run_525_archive)
        }

    def run(self):
        for sheet_key in self.sheets.keys():
            sheet, runner = self.sheets[sheet_key]
            return runner(sheet)

    def run_goated(self, sheet):
        # first row is the header:
        header = sheet.iter_rows(1,2)
        # on "goated"
        # Desc	
        # Amp	Gain	Vol	    Treb    Mid     Bass	
        # Stomp	Set 1	Set 2	Set 3	Set 4	Set 5	
        # Mod	Set 1	Set 2	Set 3	Set 4	Set 5	
        # Delay	Level	Time	Feedb	Other	
        # Rev	Level	Decay	Tone
        cfg = { "presets": [] }
        
        for row in sheet.iter_rows(2):
            entry = {}
            entry['tone'] = row[0].value
            entry['amp'] = {
                'id':     row[1].value,
                'gain':   self._v(row[2].value),
                'volume': self._v(row[3].value),
                'treb':   self._v(row[4].value),
                'mid':    self._v(row[5].value),
                'bass':   self._v(row[6].value)
            }
            entry['stomp'] = {
                'id':    row[7].value,
                'set_1': self._v(row[8].value),
                'set_2': self._v(row[9].value),
                'set_3': self._v(row[10].value),
                'set_4': self._v(row[11].value),
                'set_5': self._v(row[12].value)
            }

            entry['mod'] = {
                'id':    row[13].value,
                'set_1': self._v(row[14].value),
                'set_2': self._v(row[15].value),
                'set_3': self._v(row[16].value),
                'set_4': self._v(row[17].value),
                'set_5': self._v(row[18].value)
            }

            entry['delay'] = {
                'id':       row[19].value,
                'level':    self._v(row[20].value),
                'time':     self._v(row[21].value),
                'feedback': self._v(row[22].value),
                'other':    self._v(row[23].value)
            }
            entry['reverb'] = {
                'id':      row[24].value,
                'level':   self._v(row[25].value),
                'decay':   self._v(row[26].value),
                'tone':    self._v(row[27].value),
            }

            # clean empty
            for i in ["stomp", "mod", "delay", "reverb"]:
                if entry[i]['id'] in ['-',""]:
                    entry[i] = {}

            cfg["presets"].append(entry)

        return cfg

    def _v(self, v):
        r = None
        if isinstance(v, str):
            if v.lower() == "low": r = 0.0
            if v.lower() in ["-", ""]: r = None
            if "," in v:
                r = v.replace(",",".")
                r = float(r)
        if isinstance(v, numbers.Number):
            r = float(v)

        return r

if __name__ == "__main__":
    #s2j = Sheet2Json("https://docs.google.com/spreadsheets/d/1KWvjJ6q6Ora2MqmxtUAWjq9Uerp0Ycza5ouuKuol5HQ/edit?gid=1040178095#gid=1040178095")  
    s2j = Sheet2Json("FENDER MUSTANG LT_25.xlsx")  
    s2j.load()
    cfg = s2j.run()
    pprint.pprint(cfg)