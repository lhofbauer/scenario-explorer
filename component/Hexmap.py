#from dash import Dash, html, dcc, callback, Output, Input
#import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from shapely.geometry import Polygon
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc
import json
import math



mapfile = "./data/uk-local-authority-districts-2023.hexjson"
map_column = "LAD23CD"

# load and process hexmap file
with open(mapfile, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)
data = data["hexes"]

mapdata = pd.DataFrame.from_dict(data,orient="index")
mapdata.index.name = map_column
mapdata = mapdata.rename(columns={"n":map_column[:-2]+"NM"})
mapdata = mapdata.reset_index()

r = 0.5 / np.sin(np.pi/3)
y_diff = np.sqrt(1 - 0.5**2)  

mapdata = mapdata.set_index("LAD23CD")

for hi in mapdata.index:

    row = mapdata.loc[hi, "r"]
    col = mapdata.loc[hi, "q"]
    
    if row % 2 == 1:
        col = col + 0.5
    row = row * y_diff
    
    c = [[col + math.sin(math.radians(ang)) * r,
          row + math.cos(math.radians(ang)) * r] 
         for ang in range(0, 360, 60)]

    mapdata.loc[hi, "geometry"] = Polygon(c)
    
mapdata = gpd.GeoDataFrame(mapdata, geometry="geometry")
mapdata = mapdata.reset_index()
geojson = mapdata.__geo_interface__



def WideFormHexmap(id, path, title, zlabel, technology, year, scenario = None,
                    x_label = None, y_label = None, style = None):
    raw_df = pd.read_csv(path)
    df = raw_df.copy()
    df = df[df['RUN'] == scenario] if scenario else df
    df = df[["REGION", technology]]
    techmap = mapdata.merge(right = df, left_on = map_column, right_on = 'REGION',
                            how='left')
    techmap[zlabel] = techmap[technology]
    fig = px.choropleth(techmap,
                    geojson = geojson,
                    locations = map_column,
                    color = zlabel,
                    featureidkey = "properties." + map_column,
                    projection = "mercator",
                    #color_continuous_scale="Emrld",
                    #hover_name=loc_column[:-2]+"NM",
                    #hover_data={loc_column:False},
                    )  
    fig.update_geos(fitbounds = "locations", visible = False)
    fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white', title = title)
    
    return html.Div(
        dcc.Graph(id = id, 
                  figure = fig, 
                  style = {'width': '155vh', 'height':'85vh'} 
                  if style == None else style)
    )


def LongFormHexmap(id, path, title, zlabel, scenario = None, sex = None, 
                   x_label = None, y_label = None, style = None):
    raw_df = pd.read_csv(path)
    df = raw_df.copy()
    df = df[df['RUN'] == scenario] if scenario else df
    # Creating a column with the given name "sex" to compensate 
    # the malfunction of legend_title_text
    df.rename(columns={zlabel: sex}, inplace=True)
    fig = px.choropleth(df,
                    geojson = geojson,
                    locations = 'REGION',
                    color = sex,
                    featureidkey = "properties." + map_column,
                    projection = "mercator",
                    )
    fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white', 
                      title = title)
    fig.update_geos(fitbounds = "locations", visible = False)
    
    return html.Div(
        dcc.Graph(id = id, 
                  figure = fig, 
                  style = {'width': '155vh', 
                           'height':'85vh',
                           } if style == None else style)
    )


