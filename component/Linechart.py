import pandas as pd
import plotly.express as px

from dash import html, dcc


def GenericLinechart(id, df, x, y, category, naming=None, title=None,
                     x_label = None, y_label = None,l_label=None, 
                     scenarios = None):

    df = df[df['RUN'].isin(scenarios)] if scenarios else df
    df = df.replace(naming)

    fig = px.line(df, x = x, y = y,
                 color = category)
    
    fig.update_layout(
                    #paper_bgcolor = 'white',
                    #plot_bgcolor = 'white', 
                    yaxis_title=y_label,
                    xaxis_title=x_label,
                    legend_title_text=l_label,
                    title=title
                    )
                
    return html.Div(
        dcc.Graph(id = id, 
                  figure = fig,
                  config={'displaylogo':False})
    )
