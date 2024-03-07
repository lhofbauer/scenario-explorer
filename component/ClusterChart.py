import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc
import json
from component import Pagination
#Check Color Scheme https://plotly.com/python/discrete-color/

from pathlib import Path
appdir = str(Path(__file__).parent.parent.resolve())


# Change the region code to name
mapfile = f'{appdir}/data/uk-local-authority-districts-2023.hexjson'

# load and process hexmap file
with open(mapfile, "r", encoding = "utf-8") as json_file:
    data = json.load(json_file)
mapfiledata = data["hexes"]

# Define the areas and fetch the name
areasfile = f'{appdir}/data/areas_codes_names.json'
with open(areasfile, 'r', encoding = 'utf-8') as json_file:
    data = json.load(json_file)

# Swap the data structure to {name: code}
areas_object = {v: k for k, v in data.items()}

# Extract the list of areas' names
areas_list = [name for code, name in data.items()]

# {regionCode:areaCode} mapping file
region_area_code_mapping = f'{appdir}/data/region_area_code_mapping.json'
with open(region_area_code_mapping, 'r', encoding = 'utf-8') as json_file:
    data = json.load(json_file)

# {region code: area code}
region_area = data

class WideFromBarCharts: 
    def __init__(self, id, path, title):
        self.id = id
        self.path = path
        self.title = title

    def HeatGeneration(self, cat_position, xaxis, division, area, x_label = None, 
                    y_label = None, scenario = None, sex = None):
        raw_df = pd.read_csv(self.path)
        df = raw_df[raw_df['RUN'] == scenario] if scenario else raw_df
        categories = df.columns.to_list()[cat_position:]
        regions_list = df[division].unique().tolist()

        # Filtered divisions through the given area
        filtered_regions = [r for r in regions_list if region_area[r] == areas_object[area]]

        graphs = html.Div([], style = {'display':'flex', 'flex-wrap':'wrap'})

        counter = 0
        for i in filtered_regions:
            if counter == 0:
                counter += 1
                df_split = df[df[division] == i] 

                fig = px.bar(df_split, x = xaxis, y = categories, 
                            color_discrete_sequence=px.colors.qualitative.Alphabet)
                fig.layout = dict(xaxis = dict(type = "category"), barmode = 'stack', 
                                title = "{} - {}".format(self.title, mapfiledata[i]['n']))
                fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white', 
                                legend_title_text = sex, legend_tracegroupgap = 5)
                fig.update_xaxes(title_text = x_label)
                fig.update_yaxes(title_text = y_label)

                graphs.children.append(html.Div(
                                        dcc.Graph(figure = fig,
                                                style = {'width': '120vh',
                                                        'height':'60vh'})))
        
            else: 
                fig = px.bar(df_split, x = xaxis, y = categories,
                                color_discrete_sequence=px.colors.qualitative.Alphabet)
                fig.layout = dict(xaxis = dict(type = "category"), barmode = 'stack', 
                                    title = mapfiledata[i]['n'])
                fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white', 
                                    showlegend = False, )

                graphs.children.append(html.Div(
                                        dcc.Graph(figure = fig,
                                                style = {'width': '60vh',
                                                        'height':'35vh'})))



        return graphs
        
