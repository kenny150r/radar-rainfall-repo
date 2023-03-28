# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 22:20:47 2023

@author: marga
"""

import requests, os

base_url = "https://www.ncei.noaa.gov/pub/has/"

hass = ["HAS012352946",
        "HAS012352945",
        "HAS012352943",
        "HAS012352942",
        "HAS012352944",
        "HAS012352940",
        "HAS012352939"]

for has in hass:
    file = "fileList.txt"
    r = requests.get(base_url + has + "/" + file)
    flist = r.content.decode('utf-8').split('\n')
    
    for i,f in enumerate(flist):
        print("Working {:d} of {:d}".format(i,len(flist)))
        if "NTPESX" in f or "N0Q" in f:
            print("Saving {:s}".format(f))
            if os.path.exists("C:\\Users\\Kenny\\metdata\\" + f.split("/")[-1]):
                print("Already done!")
                continue
            try:
                r = requests.get(base_url + has + "/" +f)
                with open("C:\\Users\\Kenny\\metdata\\" + f.split("/")[-1],'wb') as outfile:
                    outfile.write(r.content)
            except:
                continue