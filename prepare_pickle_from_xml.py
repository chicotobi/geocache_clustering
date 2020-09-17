#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import glob
import zipfile
import pandas as pd  

p0 = "/home/hofmann/geocache_clustering/"

# My own geocaches
own = []
zips = glob.glob(p0+'/own/*.zip')
for z in zips:
    zipfile.ZipFile(z, 'r').extractall(p0+"extracted_own/")  
fs = glob.glob(p0+"extracted_own/*")
for f in fs:
    if not "wpts" in f:
        root = ET.parse(f).getroot()
        for i in range(7,len(root)):
            name = root[i][1].text
            own.append(name)
            
# All geocaches
lats = []
lons = []
names = []
zips = glob.glob(p0+'/geocache/*.zip')
for z in zips:
    zipfile.ZipFile(z, 'r').extractall(p0+"extracted/")
fs = glob.glob(p0+"extracted/*")
for f in fs:
    if not "wpts" in f:
        root = ET.parse(f).getroot()
        for i in range(7,len(root)):
            lat = root[i].attrib['lat']
            lon = root[i].attrib['lon']
            name = root[i][1].text
            if name not in own:
                lats.append(float(lat))
                lons.append(float(lon))
                names.append(name)
            
df = pd.DataFrame({"Name":names,"Lat":lats,"Lon":lons})
df["LatRad"] = df["Lat"] / 180 * 3.141592653
df["LonRad"] = df["Lon"] / 180 * 3.141592653
df.to_pickle(p0 + "/data.pickle")