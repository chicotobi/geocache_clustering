#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd  
import plotly.graph_objects as go

import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from sklearn.cluster import dbscan

token = "pk.eyJ1IjoiY2hpY290b2JpIiwiYSI6ImNrOXEzdXNzNDBnbnMzZnJ0NjdjNHJtenYifQ.1zM3EIf0UGBiauBZcEJAGg"
p = "/home/hofmann/geocache_clustering/geocache_clustering/data.pickle"
df = pd.read_pickle(p)

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

a = range(0,30,5)
b = list(map(str,a))
m = dict(zip(a,b))

a = range(0,30,5)
b = list(map(str,a))
m2 = dict(zip(a,b))

a = range(4,20,2)
b = list(map(str,a))
m3 = dict(zip(a,b))

app.layout = html.Div(
    [dbc.Row([dbc.Col(
        html.Div([
            html.Label("Epsilon in DBSCAN x 1e-5",htmlFor="eps"),
            dcc.Slider(
                id='eps',
                min=0,
                max=30,
                value=14,
                marks=m
            ),
            html.Label("Min #Pts per cluster",htmlFor="npts"),
            dcc.Slider(
                id='npts',
                min=0,
                max=30,
                value=10,
                marks=m2
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
     Input('unclstrd_pts','value')],
    [State('gra','relayoutData')]
    )
def update_figure(eps,npts,unclstrd_pts,relayoutData):
    # Clustering
    fig = go.Figure()
    
    mdf = df.copy()    
    if relayoutData and "mapbox._derived" in relayoutData:
        mat = relayoutData["mapbox._derived"]["coordinates"]
        
        lon_min = min(np.array(mat)[:,0])
        lon_max = max(np.array(mat)[:,0])
        lat_min = min(np.array(mat)[:,1])
        lat_max = max(np.array(mat)[:,1])
        lat0 = relayoutData["mapbox.center"]["lat"]
        lon0 = relayoutData["mapbox.center"]["lon"]
        zoom0 = relayoutData["mapbox.zoom"]
    else:
        lon_min = 7.3
        lon_max = 8.3
        lat_min = 49.2
        lat_max = 49.7
        lat0 = 49.436
        lon0 = 7.766
        zoom0 = 9.5

    mdf = mdf[mdf["Lat"]>lat_min]
    mdf = mdf[mdf["Lat"]<lat_max]
    mdf = mdf[mdf["Lon"]>lon_min]
    mdf = mdf[mdf["Lon"]<lon_max]
    
    np.random.seed(42) 
    res = dbscan(mdf[["LatRad","LonRad"]].values,eps=eps*1e-5,min_samples=npts,metric='haversine')
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
        lat=grp["Lat"],text="No cluster"))
    
    for idx_clstr in range(max(res[1])+1):
        grp = grpd[grpd["cluster"]==idx_clstr]
        fig.add_trace(go.Scattermapbox(
        mode = "markers",
        lon = grp["Lon"],
        lat=grp["Lat"],
        text="Cluster "+str(idx_clstr+1)))
    fig.update_layout(
    go.Layout(
        showlegend=False,   
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

if __name__ == '__main__':
    app.run_server(debug=True)