#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import flask
import os
from random import randint
import dash
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import dash_html_components as html
from dash.dependencies import Input, Output, State

from sklearn.cluster import dbscan

from flask.helpers import send_file

import urllib
import gpxpy
import gpxpy.gpx

token = "pk.eyJ1IjoiY2hpY290b2JpIiwiYSI6ImNrOXEzdXNzNDBnbnMzZnJ0NjdjNHJtenYifQ.1zM3EIf0UGBiauBZcEJAGg"
p = "data.pickle"
df = pd.read_pickle(p)

server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server, external_stylesheets=[dbc.themes.BOOTSTRAP])

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
    [dbc.Row(
      [dbc.Col(html.H1("Geocache-Clustering algorithm with DBSCAN in RLP"), width="auto")],justify="center"
              ),
       dbc.Row(
         [dbc.Col(
        html.Div([
            html.Label("Maximum neighbour distance", title="(Epsilon in DBSCAN * 1e-5)\nHigher value means more clusters",htmlFor="eps"),
            dcc.Slider(
                id='eps',
                min=0,
                max=30,
                value=14,
                marks=m
            ),
            html.Label("Minimum points in Cluster",title="Higher values means less clusters",htmlFor="npts"),
            dcc.Slider(
                id='npts',
                min=0,
                max=30,
                value=10,
                marks=m2
            ),
            dcc.Checklist(
                id="checkbox_plot_unclustered_points",
                    options=[
                        {'label': 'Show unclustered pts', 'value': 'show'},
                    ],
                    value=['show']
            ),
            dcc.Dropdown(
                    id='dropdown',
                    options=[],
                    value='all'
            ),
            html.A(
                'Download Data',
                id='download',
                download="cluster.gpx",
                href="",
                target="_blank"
            )
        ]),
        width=3
        ),
    dbc.Col(
        dcc.Graph(id='gra',animate=True)
    )]
    )
])

def get_layout_info(relayoutData):
    if relayoutData and "mapbox._derived" in relayoutData:
        mat = relayoutData["mapbox._derived"]["coordinates"]
        lat_min = min(np.array(mat)[:,1])
        lat_max = max(np.array(mat)[:,1])
        lon_min = min(np.array(mat)[:,0])
        lon_max = max(np.array(mat)[:,0])
        lat0 = relayoutData["mapbox.center"]["lat"]
        lon0 = relayoutData["mapbox.center"]["lon"]
        zoom0 = relayoutData["mapbox.zoom"]
    else:
        lat_min = 49.2
        lat_max = 49.7
        lon_min = 7.3
        lon_max = 8.3
        lat0 = 49.436
        lon0 = 7.766
        zoom0 = 9.5
    return lat_min, lat_max, lon_min, lon_max, lat0, lon0, zoom0

def filter_data(relayoutData):
    lat_min, lat_max, lon_min, lon_max, lat0, lon0, zoom0 = get_layout_info(relayoutData)
    mdf = df.copy()
    mdf = mdf[mdf["Lat"]>lat_min]
    mdf = mdf[mdf["Lat"]<lat_max]
    mdf = mdf[mdf["Lon"]>lon_min]
    mdf = mdf[mdf["Lon"]<lon_max]
    return mdf, lat0, lon0, zoom0

def get_dbscan_data(mdf,eps,npts):
    np.random.seed(42)
    res = dbscan(mdf[["LatRad","LonRad"]].values,eps=eps*1e-5,min_samples=npts,metric='haversine')
    df3 = mdf.copy()
    df3["cluster"] = res[1]
    return df3

def update_figure(d0, lat0, lon0, zoom0, plot_unclustered_points):
    fig = go.Figure()
    
    if plot_unclustered_points:
        d = d0[d0["cluster"]==-1]
        fig.add_trace(
            go.Scattermapbox(
                mode = "markers",
                marker = go.scattermapbox.Marker(
                    color='rgb(0, 0, 0)',
                    opacity=0.5),
                lat = d["Lat"],
                lon = d["Lon"],
                text="No cluster"))

    all_cluster_index = range(max(d0["cluster"])+1)
    for cluster_index in all_cluster_index:
        d = d0[d0["cluster"]==cluster_index]
        fig.add_trace(
            go.Scattermapbox(
                mode = "markers",
                lat = d["Lat"],
                lon = d["Lon"],
                text = "Cluster " + str(cluster_index)))
        
    fig.update_layout(
        go.Layout(
            showlegend=False,
            mapbox = dict(
                center=go.layout.mapbox.Center(lat=lat0,lon=lon0),
                accesstoken=token,
                zoom=zoom0),
            autosize = True,
            hovermode = 'closest',
            margin = dict(t=0, b=0, l=0, r=0))) 
    return fig

@app.callback(
    [Output('gra', 'figure'),
     Output("dropdown","options")],
    [Input('eps', 'value'),
     Input('npts','value'),
     Input('checkbox_plot_unclustered_points','value')],
    [State('gra','relayoutData')]
    )
def main_callback(eps,npts,checkbox_plot_unclustered_points,relayoutData):

    plot_unclustered_points = ('show' in checkbox_plot_unclustered_points)
    
    mdf, lat0, lon0, zoom0 = filter_data(relayoutData)

    d = get_dbscan_data(mdf,eps,npts)

    fig = update_figure(d, lat0, lon0, zoom0, plot_unclustered_points)

    # Update dropdown menu
    all_cluster_index = range(max(d["cluster"])+1)
    options = [{'label': i, 'value': i} for i in all_cluster_index]
    
    # Download file
    txt = "hello world"
    path = "tmp.txt"
    with open(path, "w") as file:
        file.write(txt)
    send_file(path, as_attachment=True)
    return fig, options

@app.callback(
    Output('download', 'href'),
    [Input('eps', 'value'),
     Input('npts','value'),
     Input('dropdown', 'value')],
    [State('gra','relayoutData')])
def update_downloader(eps,npts,idx_cluster,relayoutData):
    
    mdf, lat0, lon0, zoom0 = filter_data(relayoutData)
    
    d = get_dbscan_data(mdf,eps,npts)
    
    tmp = d[d["cluster"]==idx_cluster]
    
    gpx = gpxpy.gpx.GPX()
        
    # Create first track in our GPX:
    gpx_track = gpxpy.gpx.GPXTrack()
    gpx.tracks.append(gpx_track)
    
    # Create first segment in our GPX track:
    gpx_segment = gpxpy.gpx.GPXTrackSegment()
    gpx_track.segments.append(gpx_segment)
    
    for index, row in tmp.iterrows():
        lat = row["Lat"]
        lon = row["Lon"]
        gpx_segment.points.append(gpxpy.gpx.GPXTrackPoint(lat,lon))
    gpxString = "data:text/csv;charset=utf-8," + urllib.parse.quote(gpx.to_xml())
    return gpxString
    
if __name__ == '__main__':
    app.server.run(debug=True)