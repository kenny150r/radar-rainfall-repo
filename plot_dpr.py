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
plt.ioff()

pth = "D:\\temp_data"

files = os.listdir(pth)
paths = []
times = []
dates = []
for file in files:
    if "DPRESX" in file:
        paths.append(file)
        times.append(file[-4:])
        dates.append(file[-8:])
        
indices = np.argsort(np.array(dates))
paths = np.array(paths)
times = np.array(times)
paths = paths[indices]
times = times[indices]
rain_list = []

start_time = datetime.strptime("202207290400","%Y%m%d%H%M")
end_time = datetime.strptime("202207290800","%Y%m%d%H%M")
ix = 0

red_ll = []
with open("red.txt","r") as infile:
    for line in infile.readlines():
        red_ll.append((float(line.split(",")[0]),float(line.split(",")[1])))
        

blue_ll = []
with open("blue.txt","r") as infile:
    for line in infile.readlines():
        blue_ll.append((float(line.split(",")[0]),float(line.split(",")[1])))        

for name, time, date in zip(paths, times, dates):
    ix += 1
    print("Working time {:s} ({:d} of {:d})".format(date, ix, len(times)))
    
    time_obj = datetime.strptime("2022" + date,"%Y%m%d%H%M")
    
    if time_obj < start_time or time_obj > end_time:
        print("Not in range!")
        continue
    else:
        print("Working {:s}".format(date))    

    radar = pyart.io.read_nexrad_level3(pth + "\\" + name)
    
    ctables = (('NWSStormClearReflectivity', 0, 0.05),
               ('NWS8bitVel',-100,1.0))

    cent_lon = radar.longitude['data'][0]
    cent_lat = radar.latitude['data'][0]
    ylocs = np.pad(radar.get_gate_lat_lon_alt(0)[0],((0,1),(0,1)),'wrap')
    xlocs = np.pad(radar.get_gate_lat_lon_alt(0)[1],((0,1),(0,1)),'wrap')
    data = radar.get_field(0,'radar_estimated_rain_rate')
    
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
    rh_colorbar.set_label('Rainfall Rate (in/hr)')
    add_timestamp(ax,time_obj)
    a = ax.add_geometries(red_poly, crs=ccrs.PlateCarree(), facecolor='w', edgecolor='r', alpha=0.2)
    a = ax.add_geometries(blue_poly, crs=ccrs.PlateCarree(), facecolor='w', edgecolor='b', alpha=0.2)
    #a = ax.add_geometries(polys, crs=ccrs.Mercator(), facecolor='w', edgecolor='b', alpha=0.2)
    plt.savefig("D:\\figures\\dpr_{:s}.png".format(date),dpi=150)
    
    