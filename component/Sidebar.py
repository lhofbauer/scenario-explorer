from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd

# STYLE
style_title = {'font-weight':'bold',
               'color':'#66c2a5',
               'text-align':'center',
               'font-size':'20px',
               'font-weight':'700'}
style_description = {'font-family':'Roboto',
                     'font-size':'16px',
                     'color':'#A5A5A5'}

#CONTENT
content_title = 'ENERGY TRANSITION'
content_description = "The graphs show the progress of energy transition in the UK"
content_facet_1 = 'Scenario'

#EXTRACT SCENARIOS
df = pd.read_csv('./data/plot_data_01.csv')
scenarios = sorted(df['RUN'].unique())

#LAYOUT
def sidebar():
    return html.Div(
       [
            html.Div(content_title, style = style_title ),
            html.Hr(),
            html.P(content_description, style = style_description),
            html.Br(),
            html.Div(content_facet_1, className = 'facet_name'),
            dcc.Dropdown(scenarios, scenarios[0], id = 'scenario_dropdown'),
            #dbc.Nav([#dbc.NavLink("Home", href="/", active="exact"),],vertical=True,pills=True,),
        ], 
        id = 'sidebar'
    )

