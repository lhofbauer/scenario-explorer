import pandas as pd
import plotly.express as px

from dash import html, dcc


def GenericLinechart(id, df, x, y, category, naming=None, title=None,
                     x_label = None, y_label = None,l_label=None, 
                     scenarios = None, lads=None):

    df = df[df['RUN'].isin(scenarios)] if scenarios else df
    df = df[df['REGION'].isin(lads)] if lads else df
    

    df = df.replace(naming)
    
    if lads:
        df["RUN"] = df["RUN"] + "<br>" + df["REGION"]
        
    fig = px.line(df, x = x, y = y,
                 color = category)
    
    fig.update_layout(
                    #paper_bgcolor = 'white',
                    #plot_bgcolor = 'white', 
                    yaxis_title=y_label,
                    xaxis_title=x_label,
                    legend_title_text=l_label,
                    title=title,
                    margin=dict(l=20, r=20, t=10, b=20),
                    )
                
    return html.Div(
        dcc.Graph(id = id, 
                  figure = fig,
                  config={'displaylogo':False})
    )
