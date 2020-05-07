#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import xml.etree.ElementTree as ET
import glob
import pandas as pd  

p = "/home/hofmann/geocache_clustering/geocache_clustering/data.pickle"

all_markers = []
lats = []
lons = []
names = []
fs = glob.glob('/home/hofmann/Downloads/geocache/*/*.gpx',recursive=True)

for f in fs:
    if not "wpts" in f:
        root = ET.parse(f).getroot()
        for i in range(7,len(root)):
            lat = root[i].attrib['lat']
            lon = root[i].attrib['lon']
            name = root[i][1].text
            lats.append(float(lat))
            lons.append(float(lon))
            names.append(name)

df = pd.DataFrame({"Name":names,"Lat":lats,"Lon":lons})
df["LatRad"] = df["Lat"] / 180 * 3.141592653
df["LonRad"] = df["Lon"] / 180 * 3.141592653
df.to_pickle(p)

