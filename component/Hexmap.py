#from dash import Dash, html, dcc, callback, Output, Input
#import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
from shapely.geometry import Polygon
import geopandas as gpd
import plotly.express as px
from plotly.subplots import make_subplots
from dash import html, dcc
import json
import math

from pathlib import Path
appdir = str(Path(__file__).parent.parent.resolve())

mapfile = f'{appdir}/data/uk-local-authority-districts-2023.hexjson'
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



def GenericHexmap(id, df,  scenarios, techs=None, year= None, title=None,
                  zlabel=None,
                  naming=None,
                  style = None,
                  range_color=None,
                  figonly=False):

    df = df[df['RUN'].isin(scenarios)] if scenarios else df
    df = df[(df['YEAR'] == year)] if year else df
    df = df.replace(naming)

    scenarios = [naming[s] if s in naming.keys()
                 else s for s in scenarios] if naming else scenarios
    
    if techs and len(techs)==1 and len(scenarios)==1:
        pass
        # df = df[["REGION", technology]]
        # techmap = mapdata.merge(right = df, left_on = map_column, right_on = 'REGION',
        #                         how='left')
        # techmap[zlabel] = techmap[technology]
        
        # fig = px.choropleth(techmap,
        #                 geojson = geojson,
        #                 locations = map_column,
        #                 color = zlabel,
        #                 featureidkey = "properties." + map_column,
        #                 projection = "mercator",
        #                 #color_continuous_scale="Emrld",
        #                 #hover_name=loc_column[:-2]+"NM",
        #                 #hover_data={loc_column:False},
        #                 )  
        # fig.update_geos(fitbounds = "locations", visible = False)
        # fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white', title = title)
    elif techs is None:
        
        techmap = mapdata.merge(right = df, left_on = map_column, right_on = 'REGION',
                                how='left')
        
        gobj = list()
        
        for scen in scenarios:
            ftechmap = techmap[(techmap["RUN"] == scen)]
            
            fig = px.choropleth(ftechmap,
                            geojson = geojson,
                            locations = map_column[:-2]+"NM",
                            color = "VALUE",
                            featureidkey = "properties." + map_column[:-2]+"NM",
                            projection = "mercator",
                            #color_continuous_scale="Emrld",
                            #hover_name=map_column[:-2]+"NM",
                            #hover_data={loc_column:False},
                            )  
            gobj.append(fig)
                
        cols = len(scenarios)
        rows = 1
        specs = [[{'type': 'choropleth'} for c in range(cols)] for r in range(rows)]
        fig = make_subplots(rows=rows, cols=cols,specs=specs,
                            horizontal_spacing = 0,vertical_spacing = 0,
                            column_titles=scenarios , row_titles=None)
        i=0
        for c in range(cols):
            fig.add_trace(gobj[i]["data"][0],row=1, col=c+1)
            i = i+1
        
        fig.update_geos(visible=False,
                        lonaxis_range=[-7.5,17],
                        lataxis_range=[-3.5,27])
        print(ftechmap)
        fig.update_traces(hovertemplate = "%{location}: %{z}")
        fig.update_coloraxes(colorbar_title=dict(text=zlabel),
                             cmin=range_color[0] if range_color else None,
                             cmax=range_color[1] if range_color else None)
        

    else:

        # ccm = utils.get_colour_map(palette="tol-inc",continuous=True)
        # ccm = ccm[1:]
        # ccm[0][0]=0
        
        df = df[df['TECHNOLOGY'].isin(techs)]
        
        techmap = mapdata.merge(right = df, left_on = map_column, right_on = 'REGION',
                                how='left')
        
        gobj = list()
        for tech in techs:
            for scen in scenarios:
                ftechmap = techmap[(techmap['TECHNOLOGY'] == tech)&
                                    (techmap["RUN"] == scen)]
                #ftechmap[zlabel] = ftechmap[tech]
                
                fig = px.choropleth(ftechmap,
                                geojson = geojson,
                                locations = map_column[:-2]+"NM",
                                color = "VALUE",
                                featureidkey = "properties." + map_column[:-2]+"NM",
                                projection = "mercator",
                                #color_continuous_scale="Emrld",
                                #hover_name=loc_column[:-2]+"NM",
                                #hover_data={loc_column:False},
                                )  
                gobj.append(fig)
                
        
        cols = len(techs)
        rows = len (scenarios)
        specs = [[{'type': 'choropleth'} for c in range(cols)] for r in range(rows)]
        fig = make_subplots(rows=rows, cols=cols,specs=specs,
                            horizontal_spacing = 0,vertical_spacing = 0,
                            column_titles=techs , row_titles=scenarios)
        i=0
        for c in range(cols):
            for r in range(rows):
                fig.add_trace(gobj[i]["data"][0],row=r+1, col=c+1)
                i = i+1
        
        fig.update_geos(visible=False,
                        lonaxis_range=[-7.5,17],
                        lataxis_range=[-3.5,27])
        fig.update_traces(hovertemplate = "%{location}: %{z}")
        fig.update_coloraxes(colorbar_title=dict(text=zlabel),
                             #colorscale = ccm,
                             cmin=range_color[0] if range_color else None,
                             cmax=range_color[1] if range_color else None)
        fig.update_layout(height = len(scenarios) * 400)

    
    if figonly:
        return fig
    
    
    return html.Div(
        dcc.Graph(id = id, 
                  figure = fig,
                  config={'scrollZoom':False,
                         'displaylogo':False})
                  # style = {'width': '155vh', 'height':'85vh'} 
                  # if style == None else style)
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
                  figure = fig, )
                  # style = {'width': '155vh', 
                  #          'height':'85vh',
                  #          } if style == None else style)
    )


