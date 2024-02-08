#from dash import Dash, html, dcc, callback, Output, Input
#import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc
import json


def WideFormBarchart(id, path, title, xaxis, cat_position, scenario = None):
    raw_df = pd.read_csv(path)
    df = raw_df[raw_df['RUN'] == scenario] if scenario else raw_df
    categories = df.columns.to_list()[cat_position:]
    fig = px.bar(df, x = xaxis, y = categories , title = title)
    fig.layout = dict(xaxis = dict(type = "category"), barmode = 'stack')
    fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white')
    
    return html.Div(
        dcc.Graph(id = id, 
                  figure = fig, 
                  style = {'width': '155vh',
                           'height':'85vh'})
    )