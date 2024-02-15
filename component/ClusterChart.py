import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc
import json
#Check Color Scheme https://plotly.com/python/discrete-color/

# Change the region code to name
mapfile = "./data/uk-local-authority-districts-2023.hexjson"

# load and process hexmap file
with open(mapfile, "r", encoding="utf-8") as json_file:
    data = json.load(json_file)
data = data["hexes"]

class WideFromBarCharts: 
    def __init__(self, id, path, title):
        self.id = id
        self.path = path
        self.title = title

    def createGraphs(self, cat_position, xaxis, division, x_label = None, 
                    y_label = None, scenario = None, sex = None):
        graphs = html.Div([], style = {'display':'flex', 'flex-wrap':'wrap'})
        raw_df = pd.read_csv(self.path)
        df = raw_df[raw_df['RUN'] == scenario] if scenario else raw_df
        categories = df.columns.to_list()[cat_position:]
        divisions = df[division].unique().tolist()
        
        for i in divisions[0:11]:
            df_split = df[df[division] == i] 
            if divisions.index(i) == 0:
                fig = px.bar(df_split, x = xaxis, y = categories, 
                            color_discrete_sequence=px.colors.qualitative.Alphabet)
                fig.layout = dict(xaxis = dict(type = "category"), barmode = 'stack', 
                                title = "{} - {}".format(self.title, data[i]['n']))
                fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white', 
                                legend_title_text = sex, legend_tracegroupgap = 5)
                fig.update_xaxes(title_text = x_label)
                fig.update_yaxes(title_text = y_label)

                graphs.children.append(html.Div(
                                        dcc.Graph(figure = fig,
                                                style = {'width': '155vh',
                                                        'height':'80vh'})))
            
            else: 
                fig = px.bar(df_split, x = xaxis, y = categories,
                             color_discrete_sequence=px.colors.qualitative.Alphabet)
                fig.layout = dict(xaxis = dict(type = "category"), barmode = 'stack', 
                                  title = data[i]['n'])
                fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white', 
                                  showlegend = False, )

                graphs.children.append(html.Div(
                                        dcc.Graph(figure = fig,
                                                style = {'width': '77.5vh',
                                                        'height':'40vh'})))

        


        return graphs
        
