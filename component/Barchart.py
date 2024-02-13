#from dash import Dash, html, dcc, callback, Output, Input
#import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html, dcc
import json
#Check Color Scheme https://plotly.com/python/discrete-color/

def WideFormBarchart(id, path, title, xaxis, cat_position, 
                     x_label = None, y_label = None, 
                     scenario = None, sex = None):
    raw_df = pd.read_csv(path)
    df = raw_df[raw_df['RUN'] == scenario] if scenario else raw_df
    categories = df.columns.to_list()[cat_position:]
    fig = px.bar(df, x = xaxis, y = categories, 
                 color_discrete_sequence=px.colors.qualitative.Alphabet)
    fig.layout = dict(xaxis = dict(type = "category"), barmode = 'stack', title = title)
    fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white', 
                      legend_title_text = sex, legend_tracegroupgap = 5)
    fig.update_xaxes(title_text = x_label)
    fig.update_yaxes(title_text = y_label)
    
    return html.Div(
        dcc.Graph(id = id, 
                  figure = fig,
                  style = {'width': '155vh',
                           'height':'80vh'})
    )

def LongFormBarchart(id, path, title, xaxis, yaxis, category,
                     x_label = None, y_label = None, 
                     scenario = None, sex = None):
    raw_df = pd.read_csv(path)
    df = raw_df[raw_df['RUN'] == scenario] if scenario else raw_df
    legend_items = df[category].to_list()
    if 'Others' in legend_items:
        legend_items.sort(key = 'Others'.__eq__)
    fig = px.bar(df, x = xaxis, y = yaxis, 
                 category_orders = {category: legend_items}, 
                 color = category)
    fig.layout = dict(xaxis = dict(type = "category"), barmode = 'stack', title = title)
    fig.update_layout(paper_bgcolor = 'white', plot_bgcolor = 'white', 
                      legend_title_text = sex, legend_tracegroupgap = 5)
    fig.update_xaxes(title_text = x_label)
    fig.update_yaxes(title_text = y_label)
    
    return html.Div(
        dcc.Graph(id = id, 
                  figure = fig,
                  style = {'width': '155vh',
                           'height':'80vh'})
    )