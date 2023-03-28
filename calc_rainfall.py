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

import scipy.integrate

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

### Define cells and data structure
red_ll = []
with open("red.txt","r") as infile:
    for line in infile.readlines():
        red_ll.append((float(line.split(",")[0]),float(line.split(",")[1])))
        

blue_ll = []
with open("blue.txt","r") as infile:
    for line in infile.readlines():
        blue_ll.append((float(line.split(",")[0]),float(line.split(",")[1])))   
        
    
if "red_poly" not in locals():    
    radar = pyart.io.read_nexrad_level3(pth + "\\" + paths[0])
    ylocs = np.pad(radar.get_gate_lat_lon_alt(0)[0],((0,1),(0,1)),'wrap')
    xlocs = np.pad(radar.get_gate_lat_lon_alt(0)[1],((0,1),(0,1)),'wrap')    
    red_poly = Polygon(red_ll)
    blue_poly = Polygon(blue_ll)
    
    inds = []
    polys = []
    rainfall = []
    area = []
    
    blue_cells = []
    red_cells = []
    
    for i in range(0, xlocs.shape[0]-1):
        print(i)
        for j in range(0, xlocs.shape[1]-1):
            
            poly = Polygon([(xlocs[i,j], ylocs[i,j]),
                                      (xlocs[i+1,j], ylocs[i+1,j]),
                                      (xlocs[i+1,j+1], ylocs[i+1,j+1]),
                                      (xlocs[i,j+1], ylocs[i,j+1])]);
            
            if red_poly.contains(poly.centroid):
                cell = dict()
                cell['inds'] = (i,j)
                cell['poly'] = poly
                cell['area'] = Polygon([ccrs.Mercator().transform_point(xlocs[i,j], ylocs[i,j],ccrs.PlateCarree()),
                                      ccrs.Mercator().transform_point(xlocs[i+1,j], ylocs[i+1,j],ccrs.PlateCarree()),
                                      ccrs.Mercator().transform_point(xlocs[i+1,j+1], ylocs[i+1,j+1],ccrs.PlateCarree()),
                                      ccrs.Mercator().transform_point(xlocs[i,j+1], ylocs[i,j+1],ccrs.PlateCarree())
                                      ]).area
                red_cells.append(cell)
            elif blue_poly.contains(poly.centroid):
                cell = dict()
                cell['inds'] = (i,j)
                cell['poly'] = poly
                cell['area'] = Polygon([ccrs.Mercator().transform_point(xlocs[i,j], ylocs[i,j],ccrs.PlateCarree()),
                                      ccrs.Mercator().transform_point(xlocs[i+1,j], ylocs[i+1,j],ccrs.PlateCarree()),
                                      ccrs.Mercator().transform_point(xlocs[i+1,j+1], ylocs[i+1,j+1],ccrs.PlateCarree()),
                                      ccrs.Mercator().transform_point(xlocs[i,j+1], ylocs[i,j+1],ccrs.PlateCarree())
                                      ]).area
                blue_cells.append(cell)            

for cell in blue_cells:
    cell['time'] = []
    cell['time_s'] = []
    cell['rate'] = []
    cell['total'] = []
    
for cell in red_cells:
    cell['time'] = []
    cell['time_s'] = []
    cell['rate'] = []
    cell['total'] = []

### Compute rainfall Rates
start_time = datetime.strptime("202207250000","%Y%m%d%H%M")
end_time = datetime.strptime("202208250000","%Y%m%d%H%M")
epoch = datetime(2022,7,1)
ix = 0

for name, time, date in zip(paths, times, dates):
    ix += 1
    print("Working time {:s} ({:d} of {:d})".format(date, ix, len(times)))
    
    time_obj = datetime.strptime("2022" + date,"%Y%m%d%H%M")
    
    if time_obj < start_time or time_obj > end_time:
        print("Not in range!")
        continue

    radar = pyart.io.read_nexrad_level3(pth + "\\" + name)
    time_obj = datetime.strptime(radar.time['units'].split()[-1],"%Y-%m-%dT%H:%M:%SZ")
    
    
    ctables = (('NWSStormClearReflectivity', 0, 0.05),
                ('NWS8bitVel',-100,1.0))

    cent_lon = radar.longitude['data'][0]
    cent_lat = radar.latitude['data'][0]
    ylocs = np.pad(radar.get_gate_lat_lon_alt(0)[0],((0,1),(0,1)),'wrap')
    xlocs = np.pad(radar.get_gate_lat_lon_alt(0)[1],((0,1),(0,1)),'wrap')
    data = radar.get_field(0,'radar_estimated_rain_rate')
    
    for cell in blue_cells:
        if np.ma.masked is data[cell['inds'][0],cell['inds'][1]]:
            cell['rate'].append(0.0)
        else:
            cell['rate'].append(data[cell['inds'][0],cell['inds'][1]])
        cell['time'].append(time_obj)
        cell['time_s'].append(time_obj - epoch)
        
    for cell in red_cells:
        if np.ma.masked is data[cell['inds'][0],cell['inds'][1]]:
            cell['rate'].append(0.0)
        else:
            cell['rate'].append(data[cell['inds'][0],cell['inds'][1]])
        cell['time'].append(time_obj) 
        cell['time_s'].append(time_obj - epoch)


for cell in blue_cells:
    cell['total'] = scipy.integrate.cumtrapz(cell['rate'],cell['time_s']/3600,initial=0)
    
for cell in red_cells:
    cell['total'] = scipy.integrate.cumtrapz(cell['rate'],cell['time_s']/3600,initial=0)
        
plt.figure()
for cell in red_cells:
    plt.plot(cell['time'],cell['total'])

import pickle
with open("blue.pkl","wb") as outfile:
    pickle.dump(blue_cells,outfile)
with open("red.pkl","wb") as outfile:
    pickle.dump(red_cells,outfile)




