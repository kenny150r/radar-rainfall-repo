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

#pth = "C:\\Users\\marga\\Kenny\\data"
pth = "D:\\temp_data"

files = os.listdir(pth)
paths = []
times = []
dates = []
for file in files:
    if "N0QESX" in file:
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
for name, time, date in zip(paths, times, dates):
    ix += 1
    print("Working time {:s} ({:d} of {:d})".format(date, ix, len(times)))
    
    time_obj = datetime.strptime("2022" + date,"%Y%m%d%H%M")
    
    if time_obj < start_time or time_obj > end_time:
        print("Not in range!")
        continue
    else:
        print("Working {:s}".format(date))    
    
    f = Level3File(name)
    
    ctables = (('NWSStormClearReflectivity', -20, 0.5),
               ('NWS8bitVel',-100,1.0))
    
    datadict = f.sym_block[0][0]
    
    data = f.map_data(datadict['data'])
    
    az = units.Quantity(np.array(datadict['start_az'] + [datadict['end_az'][-1]]), 'degrees')
    rng = units.Quantity(np.linspace(0, f.max_range, data.shape[-1] + 1), 'kilometers')

    cent_lon = f.lon
    cent_lat = f.lat
    
    xlocs, ylocs = azimuth_range_to_lat_lon(az, rng, cent_lon, cent_lat)
    
    poly = Polygon([(-114.898506, 35.951740),
                    (-114.866366, 35.937284),
                    (-114.853867, 35.935726),
                    (-114.845901, 35.946625),
                    (-114.846176, 35.973085),
                    (-114.859087, 35.984756),
                    (-114.898781, 35.986090),
                    (-114.898506, 35.951740)])
    # inds = []
    # polys = []
    # rainfall = []
    # area = []
    # for i in range(0, xlocs.shape[0]-1):
    #     for j in range(0, xlocs.shape[1]-1):
    #         if poly.contains(Point(xlocs[i,j], ylocs[i,j])):
    #             inds.append((i,j))
    #             rainfall.append(data[i,j])
    #             polys.append(Polygon([ccrs.Mercator().transform_point(xlocs[i,j], ylocs[i,j],ccrs.PlateCarree()),
    #                                   ccrs.Mercator().transform_point(xlocs[i+1,j], ylocs[i+1,j],ccrs.PlateCarree()),
    #                                   ccrs.Mercator().transform_point(xlocs[i+1,j+1], ylocs[i+1,j+1],ccrs.PlateCarree()),
    #                                   ccrs.Mercator().transform_point(xlocs[i,j+1], ylocs[i,j+1],ccrs.PlateCarree())
    #                                   ]))
    #             area.append(polys[-1].area)
    
    # rainfall = np.array(rainfall)
    # rainfall[np.isnan(rainfall)] = 0.0
    # area = np.array(area)
    # avg_rainfall = np.sum(rainfall * area) / np.sum(area)
    # rain_list.append(avg_rainfall)
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
    rh_colorbar.set_label('Reflectivity (DBz)')
    add_timestamp(ax,f.metadata['prod_time'])
    a = ax.add_geometries(poly, crs=ccrs.PlateCarree(), facecolor='w', edgecolor='r', alpha=0.2)
    #a = ax.add_geometries(polys, crs=ccrs.Mercator(), facecolor='w', edgecolor='b', alpha=0.2)
    plt.savefig("REFLECTIVITY_{:s}.png".format(date),dpi=150)
    
    
    