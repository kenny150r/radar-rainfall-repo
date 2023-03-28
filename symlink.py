# -*- coding: utf-8 -*-
"""
Created on Fri Feb 17 01:00:15 2023

@author: marga
"""

import os
os.chdir("STORM_07292022")
d = os.listdir()

d.sort()

ix = 0
for i in d:
    if "_0" in i and "TOTAL" in i:
        os.link(i,i.split("_0")[0] + "{:d}.png".format(ix))
        ix += 1