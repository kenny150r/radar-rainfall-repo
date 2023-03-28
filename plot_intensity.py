# -*- coding: utf-8 -*-
"""
Created on Tue Feb 21 22:10:11 2023

@author: Kenny
"""


import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from metpy.calc import azimuth_range_to_lat_lon
from metpy.cbook import get_test_data
from metpy.io import Level3File
from metpy.plots import add_timestamp, colortables
from metpy.units import units

from cartopy.io.img_tiles import *

import os
from datetime import datetime, timedelta
from shapely.geometry import Point
from shapely.geometry.polygon import Polygon

import pyart
import scipy.integrate
import pickle

from matplotlib import rc
rc('font',**{'family':'sans-serif','sans-serif':['Arial']})
#rc('font',**{'family':'serif','serif':['Times']})


intensity = dict()
intensity['duration'] = []
intensity['5min'] = []
intensity['10min'] = []
intensity['15min'] = []
intensity['30min'] = []
intensity['60min'] = []
with open("int.txt","r") as infile:
    lines = infile.readlines()
    for d in lines[0].split(",")[1:]:
        intensity['duration'].append(float(d.replace("/n","")))
    for d in lines[1].split(",")[1:]:
        intensity['5min'].append(float(d.replace("/n","")))
    for d in lines[2].split(",")[1:]:
        intensity['10min'].append(float(d.replace("/n","")))        
    for d in lines[3].split(",")[1:]:
        intensity['15min'].append(float(d.replace("/n","")))
    for d in lines[4].split(",")[1:]:
        intensity['30min'].append(float(d.replace("/n","")))
    for d in lines[5].split(",")[1:]:
        intensity['60min'].append(float(d.replace("/n","")))
                
                        
epoch = datetime(2022,7,1)
     
gauge = dict()  
gauge['time'] = []
gauge['time_s'] = []
gauge['val'] = []
with open("gaugedata.txt","r") as infile:
    lines = infile.readlines()
    lines.reverse()
    for line in lines:
        gauge['time'].append(datetime.strptime(line.split(",")[0].replace('"',''),"%m/%d/%Y %H:%M:%S") + timedelta(hours=7))
        gauge['time_s'].append((gauge['time'][-1] - epoch).total_seconds())
        gauge['val'].append(float(line.split(",")[1].replace('"','')))

gauge['time_s'] = np.array(gauge['time_s'])
gauge['rate'] = np.array(gauge['val'])*(60/5) # 5 min data
gauge['total'] = scipy.integrate.cumtrapz(gauge['rate'],gauge['time_s']/3600,initial=0)

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



for event in events:
    ix = np.argwhere(np.logical_and(blue_cells[0]['time'] > event[0], blue_cells[0]['time'] < event[1]))
    
    fig, ax = plt.subplots(6,1,sharex=True)
    ax = ax.flatten()
    fig.set_size_inches(8.5, 11)
    
    for cell in red_cells:
        time_array = cell['time_s'][ix]
        rate_array = cell['rate'][ix]        
        time_linspace = np.linspace(time_array[0][0],time_array[-1][0],200)
        time_plot = []
        for sec in time_linspace:
            time_plot.append(cell['time'][ix][0] + timedelta(seconds = (sec - time_linspace[0])))
        cell['time_plot'] = time_plot
        #rainfall, past 5 min
        cell['rainfall_5_min'] = []
        for i in range(0, len(time_linspace)):
            start = np.interp(time_linspace[i] - 5 * 60,cell['time_s'],cell['total'])
            end = np.interp(time_linspace[i],cell['time_s'],cell['total'])
            cell['rainfall_5_min'].append(end-start)
        cell['rainfall_5_min'] = np.array(cell['rainfall_5_min'])
        
        #rainfall, past 10 min
        cell['rainfall_10_min'] = []
        for i in range(0, len(time_linspace)):
            start = np.interp(time_linspace[i] - 10 * 60,cell['time_s'],cell['total'])
            end = np.interp(time_linspace[i],cell['time_s'],cell['total'])
            cell['rainfall_10_min'].append(end-start)
        cell['rainfall_10_min'] = np.array(cell['rainfall_10_min'])
                                 
        #rainfall, past 15 min    
        cell['rainfall_15_min'] = []
        for i in range(0, len(time_linspace)):
            start = np.interp(time_linspace[i] - 15 * 60,cell['time_s'],cell['total'])
            end = np.interp(time_linspace[i],cell['time_s'],cell['total'])
            cell['rainfall_15_min'].append(end-start)
        cell['rainfall_15_min'] = np.array(cell['rainfall_15_min'])
                                         
        #rainfall, past 30 min
        cell['rainfall_30_min'] = []
        for i in range(0, len(time_linspace)):
            start = np.interp(time_linspace[i] - 30 * 60,cell['time_s'],cell['total'])
            end = np.interp(time_linspace[i],cell['time_s'],cell['total'])
            cell['rainfall_30_min'].append(end-start)
        cell['rainfall_30_min'] = np.array(cell['rainfall_30_min'])
                                         
        #rainfall, past 60 min
        cell['rainfall_60_min'] = []
        for i in range(0, len(time_linspace)):
            start = np.interp(time_linspace[i] - 60 * 60,cell['time_s'],cell['total'])
            end = np.interp(time_linspace[i],cell['time_s'],cell['total'])
            cell['rainfall_60_min'].append(end-start)
        cell['rainfall_60_min'] = np.array(cell['rainfall_60_min'])
                                                              
        # p, = ax[0].plot(np.array(cell['time'])[ix],cell['rate'][ix],"-x",markersize=2)
        p, = ax[0].plot(cell['time_plot'],cell['rainfall_5_min'],"-x",markersize=2,linewidth=1)
        ax[1].plot(cell['time_plot'],cell['rainfall_10_min'],"-x",color=p.get_color(),markersize=2,linewidth=1)
        ax[2].plot(cell['time_plot'],cell['rainfall_15_min'],"-x",color=p.get_color(),markersize=2,linewidth=1)
        ax[3].plot(cell['time_plot'],cell['rainfall_30_min'],"-x",color=p.get_color(),markersize=2,linewidth=1)
        ax[4].plot(cell['time_plot'],cell['rainfall_60_min'],"-x",color=p.get_color(),markersize=2,linewidth=1)
        ax[5].plot(np.array(cell['time'])[ix],cell['total'][ix].squeeze() - cell['total'][ix].squeeze()[0],"-x",color=p.get_color(),markersize=2)
    ax[0].plot(cell['time_plot'],cell['rainfall_5_min'],"-x",markersize=2,linewidth=1,label='Radar')

    gauge['time_plot'] = time_plot                    
    #rainfall, past 5 min
    gauge['rainfall_5_min'] = []
    for i in range(0, len(time_linspace)):
        start = np.interp(time_linspace[i] - 5 * 60,gauge['time_s'],gauge['total'])
        end = np.interp(time_linspace[i],gauge['time_s'],gauge['total'])
        gauge['rainfall_5_min'].append(end-start)
    gauge['rainfall_5_min'] = np.array(gauge['rainfall_5_min'])
    
    #rainfall, past 10 min
    gauge['rainfall_10_min'] = []
    for i in range(0, len(time_linspace)):
        start = np.interp(time_linspace[i] - 10 * 60,gauge['time_s'],gauge['total'])
        end = np.interp(time_linspace[i],gauge['time_s'],gauge['total'])
        gauge['rainfall_10_min'].append(end-start)
    gauge['rainfall_10_min'] = np.array(gauge['rainfall_10_min'])
                             
    #rainfall, past 15 min    
    gauge['rainfall_15_min'] = []
    for i in range(0, len(time_linspace)):
        start = np.interp(time_linspace[i] - 15 * 60,gauge['time_s'],gauge['total'])
        end = np.interp(time_linspace[i],gauge['time_s'],gauge['total'])
        gauge['rainfall_15_min'].append(end-start)
    gauge['rainfall_15_min'] = np.array(gauge['rainfall_15_min'])
                                     
    #rainfall, past 30 min
    gauge['rainfall_30_min'] = []
    for i in range(0, len(time_linspace)):
        start = np.interp(time_linspace[i] - 30 * 60,gauge['time_s'],gauge['total'])
        end = np.interp(time_linspace[i],gauge['time_s'],gauge['total'])
        gauge['rainfall_30_min'].append(end-start)
    gauge['rainfall_30_min'] = np.array(gauge['rainfall_30_min'])
                                     
    #rainfall, past 60 min
    gauge['rainfall_60_min'] = []
    for i in range(0, len(time_linspace)):
        start = np.interp(time_linspace[i] - 60 * 60,gauge['time_s'],gauge['total'])
        end = np.interp(time_linspace[i],gauge['time_s'],gauge['total'])
        gauge['rainfall_60_min'].append(end-start)
    gauge['rainfall_60_min'] = np.array(gauge['rainfall_60_min'])    
    gauge['total2'] = []
    for i in range(0, len(time_linspace)):
        gauge['total2'].append(np.interp(time_linspace[i],gauge['time_s'],gauge['total']))
    gauge['total2'] = np.array(gauge['total2'])        
    
    iii = 0
    for i, timeframe in zip([0,1,2,3,4],['5min','10min','15min','30min','60min']):
        for freq, col, fix in zip(["10Y", "50Y", "100Y"],["grey","black","darkred"],[3,5,6]):
            ax[i].plot([cell['time_plot'][0],cell['time_plot'][-1]],[intensity[timeframe][fix],intensity[timeframe][fix]],"--",color=col)
            ax[i].text(cell['time_plot'][0],intensity[timeframe][fix],freq,color=col,horizontalalignment='left',verticalalignment='top')

    ax[0].plot(gauge['time_plot'],gauge['rainfall_5_min'],"-",markersize=2,linewidth=2,color="k",label='CCRFCD 4824')
    ax[1].plot(gauge['time_plot'],gauge['rainfall_10_min'],"-",markersize=2,linewidth=2,color="k")
    ax[2].plot(gauge['time_plot'],gauge['rainfall_15_min'],"-",markersize=2,linewidth=2,color="k")
    ax[3].plot(gauge['time_plot'],gauge['rainfall_30_min'],"-",markersize=2,linewidth=2,color="k")
    ax[4].plot(gauge['time_plot'],gauge['rainfall_60_min'],"-",markersize=2,linewidth=2,color="k")
    ax[5].plot(gauge['time_plot'],gauge['total2'] - gauge['total2'][0],"-",markersize=2,linewidth=2,color="k")


    # ax[0].set_ylabel("Rainfall Rate (in/hr)",fontsize=6)
    ax[0].set_ylabel("Rainfall, 5 min (in)",fontsize=9)
    ax[1].set_ylabel("Rainfall, 10 min (in)",fontsize=9)
    ax[2].set_ylabel("Rainfall, 15 min (in)",fontsize=9)
    ax[3].set_ylabel("Rainfall, 30 min (in)",fontsize=9)
    ax[4].set_ylabel("Rainfall, 60 min (in)",fontsize=9)
    ax[5].set_ylabel("Storm Total Rainfall (in)",fontsize=9)    
    ax[0].grid(True)
    ax[1].grid(True)
    ax[2].grid(True)
    ax[3].grid(True)
    ax[4].grid(True)    
    ax[5].grid(True)    
    # ax[1].xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
    # ax[1].xaxis.set_minor_formatter(mdates.DateFormatter("%m/%d %H:%M"))
    # ax[3].xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
    # ax[3].xaxis.set_minor_formatter(mdates.DateFormatter("%m/%d %H:%M"))    
    ax[5].xaxis.set_major_formatter(mdates.DateFormatter("%m/%d %H:%M"))
    ax[5].xaxis.set_minor_formatter(mdates.DateFormatter("%m/%d %H:%M"))
    ax[0].legend(fontsize=8)
    # plt.sca(ax[3])
    # _ = plt.xticks(rotation=90,fontsize=9)  
    # plt.sca(ax[4])
    # _ = plt.xticks(rotation=90,fontsize=9)  
    plt.sca(ax[5])
    _ = plt.xticks(rotation=90,fontsize=9)      
    plt.yticks(fontsize=9)
    plt.tight_layout()       
    plt.savefig("INTENSITY_SUMMARY_{:s}.pdf".format(event[0].strftime("%Y%m%d")))
    # plt.savefig("fig\\INTENSITY_SUMMARY_{:s}.jpeg".format(event[0].strftime("%Y%m%d")),dpi=125)
    
    
    
    
