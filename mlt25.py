#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ############################################################################
#
# read_preset.py
# 11/02/2026 (c) Juan M. Casillas <juanm.casillas@gmail.com>
#
# Read the preset file.
#
# ############################################################################

import time
import ltamp
import json
import sys
from  pprint import pprint 
import io
import copy
import numbers
import math

def num_to_range(num, inMin, inMax, outMin, outMax):
  return outMin + ((float(num - inMin) / float(inMax - inMin)) * (outMax- outMin))

def map_volume(volume):
    if volume <= 0:
        return -60.0  
    min_amp = 0.001 
    amplitude = min_amp + (volume / 10.0) * (1.0 - min_amp)
    return 46.5 * math.log10(amplitude)

    v = num_to_range(volume, 0.0, 10.0, 0.0, 1.0)
    ret =  math.log10(v)
    return ret

def map_generic(generic):
    return num_to_range(generic, 0.0, 10.0, 0.0, 1.0)

def rmap_volume(volume):
    return 10* (10 ** (volume / 46.5)) # in 0.10 range.

def rmap_generic(generic):
    return num_to_range(generic, 0.0, 1.0, 0.0, 10.0)

class GenericAmp:
    def __init__(self, id, gain=5.0, volume=5.0, treb=1.0, mid=10.0, bass=7.0):
        self.data = {
            "volume": volume,
            "gain": gain,
            "treb": treb,
            "mid": mid,
            "bass": bass,

            "gatePreset": "off",
            "gateDetectorPosition": "jack",
            "cabsimType": "none",
            "sag": "match",
            "bias": 0.0,
            "presence": 0.0,

        }
        self.volume = volume
        self.gain = gain
        self.treb = treb
        self.mid = mid
        self.bass = bass

        self.id = id


    
    def to_dict(self):
        data = copy.copy(self.data)
        data["gain"]   = map_generic(self.gain)
        data["volume"] = map_volume(self.volume)
        data["treb"]   = map_generic(self.treb)
        data["mid"]    = map_generic(self.mid)    
        data["bass"]   = map_generic(self.bass)
        s = { 
            'FenderId': self.id,
            'nodeId': 'amp',
            'nodeType': 'dspUnit',
            'dspUnitParameters': data
        }
        return s

class Amp_50sTwin(GenericAmp):

        def __init__(self):
            # default config for amp is stored as fender values,
            # not in range 1..10, so we have to match the "normal" ones

            gain    = rmap_generic(0.5)
            volume  = rmap_volume(-15)
            treb    = rmap_generic(0.7)
            mid     = rmap_generic(0.72)
            bass    = rmap_generic(-0.62)

            super().__init__("DUBS_Twin57",gain, volume, treb, mid, bass)
            self.data["cabsimType"] = "65twn"

        def __init__(self, gain=5, volume=5, treb=5, mid=5, bass=5):

            super().__init__("DUBS_Twin57",gain, volume, treb, mid, bass)
            self.data["cabsimType"] = "65twn"

class MustangLTManager:
    def __init__(self, verbose=0, pdir="presets"):
        self.amp = None
        self.verbose = verbose
        self.pdir = pdir

    def connect(self):
        self.amp = ltamp.LtAmp()
        self.amp.connect()

        self.amp.send_sync_begin()
        self.amp.send_sync_end()

    def disconnect(self):
        if self.amp:
            self.amp.disconnect()
        if self.verbose:
            print("amp disconnected")

    def get_info(self):
        data = self.amp.request_firmware_version()
        return({'firmware': data})
    
    def get_preset(self, slot_id):
        self.amp.set_preset(slot_id)
        preset_data = self.amp.retrieve_preset(slot_id)
        if self.verbose and not preset_data:
            print(f"Can't retrieve preset_info for slot {slot_id}")
            return None
        if not "data" in preset_data.keys():
            raise ValueError("invalid json - data field not found")
        return json.loads(preset_data["data"])

    def heart_beat(self):
        if self.verbose:
            print("Waitting 3 seconds for heartbeat", end='')
        for i in range(3):
            self.amp.send_heartbeat()
            if self.verbose:
                print(".",end='')
                sys.stdout.flush()
            time.sleep(1)

    def save_preset(self, data, slot_id):
        self.amp.save_preset_as(json.dumps(data), True, slot_id)
         # for now, the same data read to test

    def backup_presets(self, pdir=None):
        pdir = pdir if pdir else self.pdir
        for preset_id in range(1,60):
            if self.verbose:
                print(f"backing up {preset_id} preset")
            preset_data = self.get_preset(preset_id)
            file = open(f"{pdir}/{preset_id}.json", "w+")
            file.write(json.dumps(preset_data))
            file.close()


    def set_amp(self, data, amp_data):
        # remove node amp
        # add new node.
        ret = copy.deepcopy(data)
        ret["audioGraph"]["nodes"] = []
        for n in data["audioGraph"]["nodes"]:
            if n["nodeId"] != "amp":
                ret["audioGraph"]["nodes"].append(n)
        ret["audioGraph"]["nodes"].append(amp_data.to_dict())
        return(ret)

    def print_preset(self, data, slot):
        s = io.StringIO('')
        is_custom = True if slot > 30 and slot < 61 else False
        print(f"info.displayName:\t{data["info"]["displayName"]}",file=s)
        print(f"info.author:\t\t{data["info"]["author"]}",file=s)
        print(f"set Slot:\t\t{slot}",file=s)
        print(f"Is custom?:\t\t{is_custom}",file=s)
        
        nodes_tmp = {}
        nodes = data["audioGraph"]["nodes"]
        for n in nodes:
            nodes_tmp[n["nodeId"]] = n
        
        nodes = nodes_tmp
        # routing is done fixed on the LT25 so 
        # PREFX  stompbox -> modulation ->
        # amp -> 
        # POSTFX delay -> reverb
        print("PRE-FX",file=s)
        for k in [ "stomp", "mod"]:
            n = nodes[k]
            print(f"\tNode {k}", file=s)
            print(f"\tFenderID:\t{n["FenderId"]}", file=s)
            if len(n['dspUnitParameters'].keys()) > 0:
                print(f"\tNode Parameters", file=s)
                for p in n['dspUnitParameters'].keys():
                    if p == "volume":
                        rmap = rmap_volume(n['dspUnitParameters'][p])
                    elif isinstance(n['dspUnitParameters'][p], numbers.Number):
                        rmap = rmap_generic(n['dspUnitParameters'][p])
                    else:
                        rmap = "n/a"
                    print(f"\t{p:<25s}{n['dspUnitParameters'][p]}({rmap})", file=s) 

        print("AMP",file=s)
        n = nodes["amp"]
        print(f"\tNode {k}", file=s)
        print(f"\tFenderID:\t{n["FenderId"]}", file=s)
        if len(n['dspUnitParameters'].keys()) > 0:
            print(f"\tNode Parameters", file=s)
            for p in n['dspUnitParameters'].keys():
                if p == "volume":
                    rmap = rmap_volume(n['dspUnitParameters'][p])
                elif isinstance(n['dspUnitParameters'][p], numbers.Number):
                    rmap = rmap_generic(n['dspUnitParameters'][p])
                else:
                    rmap = "n/a"
                print(f"\t{p:<25s}{n['dspUnitParameters'][p]}({rmap})", file=s) 

        print("POST-FX",file=s)
        for k in [ "delay", "reverb"]:
            n = nodes[k]
            print(f"\tNode {k}", file=s)
            print(f"\tFenderID:\t{n["FenderId"]}", file=s)
            if len(n['dspUnitParameters'].keys()) > 0:
                print(f"\tNode Parameters", file=s)
                for p in n['dspUnitParameters'].keys():
                    if p == "volume":
                        rmap = rmap_volume(n['dspUnitParameters'][p])
                    elif isinstance(n['dspUnitParameters'][p], numbers.Number):
                        rmap = rmap_generic(n['dspUnitParameters'][p])
                    else:
                        rmap = "n/a"                   
                    print(f"\t{p:<25s}{n['dspUnitParameters'][p]}({rmap})", file=s) 

        return(s.getvalue())
if __name__ == "__main__":

    amp = MustangLTManager(verbose=1)
    amp.connect()
    # 58 empty
    # 59 full
    # 60 custom tests

    slot_id = 59
    #print(amp.get_info())
    preset_data = amp.get_preset(slot_id)
    #print(amp.print_preset(preset_data, slot_id))
    #config_amp = Amp_50sTwin(gain=6.0, volume=7.5, treb=4.0, mid=3.0, bass=7.0 )
    
    #preset_data = amp.set_amp(preset_data, config_amp)
    print(amp.print_preset(preset_data, slot_id))
    #amp.save_preset(preset_data, slot_id)
     

    amp.heart_beat()
    amp.disconnect()