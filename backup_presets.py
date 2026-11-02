#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ############################################################################
#
# backup_presets.py
# 11/02/2026 (c) Juan M. Casillas <juanm.casillas@gmail.com>
#
# read all the available presets, and store them in the presets directory
#
# ############################################################################

from mlt25 import *


if __name__ == "__main__":

    amp = MustangLTManager(verbose=1)
    amp.connect()

    amp.backup_presets()
    
    amp.heart_beat()
    amp.disconnect()