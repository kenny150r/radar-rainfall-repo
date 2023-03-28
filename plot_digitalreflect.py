# -*- coding: utf-8 -*-
"""
Created on Thu Feb 16 22:30:26 2023

@author: marga
"""

import numpy as np
import matplotlib.pyplot as plt
from metpy.calc import azimuth_range_to_lat_lon
from metpy.cbook import get_test_data
from metpy.io import Level3File
from metpy.plots import add_timestamp, colortables
from metpy.units import units

from cartopy.io.img_tiles import *

import os
from datetime import datetime
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import pyart
import pickle, glob

print("Done Importing")

plt.ioff()

pth = "D:\\temp_data"

files = glob.glob("D:\\temp_data\\*N0Q*")
paths = []
times = []
dates = []
for file in files:
    if "N0QESX" in file:
        paths.append(file)
        times.append(file[-4:])
        dates.append(file[-8:])
        
print("Done reading files")
        
indices = np.argsort(np.array(dates))
paths = np.array(paths)
times = np.array(times)
paths = paths[indices]
times = times[indices]
rain_list = []

ix = 0

red_ll = []
with open("red.txt","r") as infile:
    for line in infile.readlines():
        red_ll.append((float(line.split(",")[0]),float(line.split(",")[1])))
        

blue_ll = []
with open("blue.txt","r") as infile:
    for line in infile.readlines():
        blue_ll.append((float(line.split(",")[0]),float(line.split(",")[1])))        

with open("blue.pkl","rb") as outfile:
    blue_cells = pickle.load(outfile)
with open("red.pkl","rb") as outfile:
    red_cells = pickle.load(outfile) 
    
events = []
events.append((datetime(2022,7,25,20),datetime(2022,7,26,3)))
events.append((datetime(2022,7,27,21),datetime(2022,7,28,9)))
events.append((datetime(2022,7,29,4),datetime(2022,7,29,9)))
events.append((datetime(2022,7,30,2),datetime(2022,7,30,8)))
events.append((datetime(2022,8,18,20),datetime(2022,8,19,12)))
events.append((datetime(2022,8,24,11),datetime(2022,8,24,14)))
plt.close("all")

print(1)

for event in events:
    start_time = event[0]
    end_time = event[1]
    
    datestr = event[0].strftime("%Y%m%d")
    
    ixx = 0
    for name, time, date in zip(paths, times, dates):
        ix += 1
        print("Working time {:s} ({:d} of {:d})".format(date, ix, len(times)))
        
        time_obj = datetime.strptime("2022" + date,"%Y%m%d%H%M")
        
        if time_obj < start_time or time_obj > end_time:
            print("Not in range!")
            continue
        else:
            print("Working {:s}".format(date))    
    
        radar = pyart.io.read_nexrad_level3( name)
        
        ctables = (('NWSStormClearReflectivity', -20, 0.5),
                   ('NWS8bitVel',-100,1.0))
    
        cent_lon = radar.longitude['data'][0]
        cent_lat = radar.latitude['data'][0]
        ylocs = np.pad(radar.get_gate_lat_lon_alt(0)[0],((0,1),(0,1)),'wrap')
        xlocs = np.pad(radar.get_gate_lat_lon_alt(0)[1],((0,1),(0,1)),'wrap')
        data = radar.get_field(0,'reflectivity')

        red_poly = Polygon(red_ll)
        blue_poly = Polygon(blue_ll)
        
        plt.close('all')
        fig = plt.figure(figsize = (12,8))
        tiler = Stamen('terrain',cache=True)
        mercator = tiler.crs
        mercator = ccrs.Mercator()
        ax = plt.axes(projection=mercator)
        norm, cmap = colortables.get_with_steps(*ctables[0])
        z = ax.pcolormesh(xlocs, ylocs, data, norm=norm, cmap=cmap, transform = ccrs.PlateCarree(), alpha=0.5)
        ax.set_extent([cent_lon-0.3, cent_lon+0.3, 35.8, 36.1])
        ax.set_aspect('equal','datalim')
        ax.add_image(tiler, 12)
        rh_colorbar = fig.colorbar(z)
        rh_colorbar.set_label('Reflectivity, Base (dBZ)')
        add_timestamp(ax,time_obj)
        a = ax.add_geometries(red_poly, crs=ccrs.PlateCarree(), facecolor='w', edgecolor='r', alpha=0.2)
        a = ax.add_geometries(blue_poly, crs=ccrs.PlateCarree(), facecolor='w', edgecolor='b', alpha=0.2)
        #a = ax.add_geometries(polys, crs=ccrs.Mercator(), facecolor='w', edgecolor='b', alpha=0.2)
        plt.tight_layout()
        plt.savefig("D:\\radar\\base_reflectivity_{:s}_{:d}.jpg".format(datestr,ixx),dpi=100)
        ixx += 1
    
    
    