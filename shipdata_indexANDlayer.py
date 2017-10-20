# -*- coding: utf-8 -*-
"""
Created on Tue Jan 19 13:47:35 2015

@author: zhaobin,yifan
"""
'''
Extract new data file named "06-08_indexANDlayer.csv "with new column "modNearestIndex" and "modDepthLayer"
'''
import pandas as pd
import numpy as np
import netCDF4
from datetime import datetime, timedelta
from turtleModule import str2ndlist, dist
import watertempModule as wtm   # a module that has all classes using ROMS and FVCOm model.
def nearest_point_index2(lon, lat, lons, lats):
    d = dist(lon, lat, lons ,lats)
    min_dist = np.min(d)
    index = np.where(d==min_dist)
    return index
#################################################################################33
    
shipData=pd.read_csv('shipdata.csv',index_col=0)
good_index=np.where(shipData.index!=2564)[0]
shiplat=pd.Series(str2ndlist(shipData['lat'][good_index],bracket=True),index=good_index)
shiplon=pd.Series(str2ndlist(shipData['lon'][good_index],bracket=True),index=good_index)
    

starttime = datetime(2013,07,10) # starttime and endtime can be any time that included by model, we just want a url to get "lon_rho", "lat_rho", "h", "s_rho" in model.
endtime = starttime + timedelta(hours=1)
tempObj = wtm.water_roms()
url = tempObj.get_url(starttime, endtime)
modData = netCDF4.Dataset(url)
modLons = modData.variables['lon_rho'][:]
modLats = modData.variables['lat_rho'][:]
s_rho = modData.variables['s_rho'][:]
h = modData.variables['h'][:]
#indexNotNull = shiplon[shiplon.isnull()==False].index # some obslat and obslon of point are empty, get rid of them.
                                                    # or this line can be the indices of TF which is less.
                                                    # indexTF = np.where(shipData['TF'].notnull())[0]

loc = []
for i in good_index:
    ind = []
    lon = shiplon[i]
    lat = shiplat[i]
    index = nearest_point_index2(lon, lat, modLons, modLats)
    ind.append(index[0][0])
    ind.append(index[1][0])
    loc.append(ind)
    #print i
loc = pd.Series(loc, index=good_index)
shipData['modNearestIndex'] = loc #add loc to shipData in case want to save it.

shipDepth = pd.Series(str2ndlist(shipData['depth'][good_index],bracket=True), index=good_index)
layersAll = []
for i in good_index:
    nearest_index = loc[i]
    layers = []
    depthLayers = h[nearest_index[0], nearest_index[1]] * s_rho
    for j in range(len(shipDepth[i])):
        # depthLayers = h[nearest_index[0], nearest_index[1]] * s_rho
        l = np.argmin(abs(depthLayers+shipDepth[i][j])) # shipData is positive and depthLayers is negitive. So the index of min sum is the layer
        layers.append(l)
        #print i, j, l
    layersAll.append(layers)
 
shipData['modDepthLayer'] = pd.Series(layersAll, index=good_index)
shipData.to_csv('ship_indexANDlayer.csv')
