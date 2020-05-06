#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import xml.etree.ElementTree as ET
import plotly.graph_objects as go
import pandas as pd    
import glob
from sklearn.cluster import dbscan
import numpy as np

token = "pk.eyJ1IjoiY2hpY290b2JpIiwiYSI6ImNrOXEzdXNzNDBnbnMzZnJ0NjdjNHJtenYifQ.1zM3EIf0UGBiauBZcEJAGg"

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

all_markers = []
lats = []
lons = []
fs = glob.glob('/home/hofmann/Downloads/geocache/*/*.gpx',recursive=True)

for f in fs:
    if not "wpts" in f:
        root = ET.parse(f).getroot()
        for i in range(10,len(root)):
            lat = root[i].attrib['lat']
            lon = root[i].attrib['lon']
            lats.append(float(lat))
            lons.append(float(lon))

df = pd.DataFrame({"Lat":lats,"Lon":lons})
df["LatRad"] = df["Lat"] / 180 * 3.141592653
df["LonRad"] = df["Lon"] / 180 * 3.141592653

a = np.arange(0,0.001,0.0002)
b = list(map(lambda x : "{:.4f}".format(x),a))
m = dict(zip(a,b))

a = range(0,50,5)
b = list(map(str,a))
m2 = dict(zip(a,b))

a = range(4,20,2)
b = list(map(str,a))
m3 = dict(zip(a,b))

app.layout = html.Div(
    [dbc.Row([dbc.Col(
        html.Div([
            html.Label("Epsilon in DBSCAN",htmlFor="eps"),
            dcc.Slider(
                id='eps',
                min=0,
                max=0.001,
                step=0.00001,
                value=0.0005,
                marks=m
            ),
            html.Label("Min #Pts per cluster",htmlFor="npts"),
            dcc.Slider(
                id='npts',
                min=0,
                max=50,
                step=5,
                value=30,
                marks=m2
            ),
            html.Label("Show #Cluster",htmlFor="nclstr"),
            dcc.Slider(
                id='nclstr',
                min=4,
                max=20,
                value=5,
                marks=m3
            ),
            dcc.Checklist(
                id="unclstrd_pts",
                    options=[
                        {'label': 'Show unclustered pts', 'value': 'show'},
                    ],
                    value=['show']
            )  
        ]),
        width=3
        ),
    dbc.Col(    
        dcc.Graph(id='gra',animate=True)
    )]
    )
])
   
@app.callback(
    Output('gra', 'figure'),
    [Input('eps', 'value'),Input('npts','value'),
     Input("nclstr","value"),Input('unclstrd_pts','value')],
    [State('gra','relayoutData')]
    )
def update_figure(eps,npts,nclstr,unclstrd_pts,relayoutData):
    # Clustering
    fig = go.Figure()
    
    mdf = df.copy()    
    if relayoutData and "mapbox._derived" in relayoutData:
            mat = relayoutData["mapbox._derived"]["coordinates"]
            
            lon_min = min(np.array(mat)[:,0])
            lon_max = max(np.array(mat)[:,0])
            #width = lon_max - lon_min
            #lon_min -= width * 0.1
            #lon_max += width * 0.1
            
            lat_min = min(np.array(mat)[:,1])
            lat_max = max(np.array(mat)[:,1])
            #height = lat_max - lat_min
            #lat_min -= height * 0.1
            #lat_max += height * 0.1
            
            mdf = mdf[mdf["Lat"]>lat_min]
            mdf = mdf[mdf["Lat"]<lat_max]
            mdf = mdf[mdf["Lon"]>lon_min]
            mdf = mdf[mdf["Lon"]<lon_max]
            
            lat0 = relayoutData["mapbox.center"]["lat"]
            lon0 = relayoutData["mapbox.center"]["lon"]
            zoom0 = relayoutData["mapbox.zoom"]
    else:
        lat0 = 49.436
        lon0 = 7.766
        zoom0 = 7
       
    res = dbscan(mdf[["LatRad","LonRad"]].values,eps=eps,min_samples=npts,metric='haversine')
    grpd = mdf.copy()
    grpd["cluster"] = res[1]

    if 'show' in unclstrd_pts:
        grp = grpd[grpd["cluster"]==-1]
        fig.add_trace(go.Scattermapbox(
            
        mode = "markers",
        marker=go.scattermapbox.Marker(
                color='rgb(0, 0, 0)',
                opacity=0.5
            ),
        lon = grp["Lon"],
        lat=grp["Lat"]))
    
    nclstr = min(max(res[1]+1),nclstr)
    
    for idx_clstr in range(nclstr):
        grp = grpd[grpd["cluster"]==idx_clstr]
        fig.add_trace(go.Scattermapbox(
        mode = "markers",
        lon = grp["Lon"],
        lat=grp["Lat"]))
    fig.update_layout(
    go.Layout(
    mapbox = dict(
            center=go.layout.mapbox.Center(lat=lat0,lon=lon0),
            accesstoken=token,
            zoom=zoom0
            ),
            title="Eps is " + str(eps) + " and npts is " + str(npts),
            autosize=True,
            hovermode='closest',
            margin=dict(t=0, b=0, l=0, r=0)
            ))
    return fig

app.run_server(debug=True)