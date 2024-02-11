from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import json
from component import Sidebar, Tabs, Barchart, Hexmap


app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

config = {
    'scrollZoom': True
}

#EXTRACT SCENARIOS
df = pd.read_csv('./data/plot_data_01.csv')
scenarios = sorted(df['RUN'].unique())

app.layout = html.Div([Sidebar.sidebar(),
                       Tabs.tabs([
                           Barchart.WideFormBarchart(
                                'heat_generation_chart',
                                './data/plot_data_01.csv',
                                "Annual Heat Generation",
                                "YEAR",
                                2,                                
                                ),
                           Hexmap.WideFormHexmap(
                               "heat_generation_map",
                               "./data/plot_data_02.csv",
                               "Heat generation map",
                               "Fraction supplied by technology (-)",
                               "Air-source HP",
                               2050,
                               )  
                            ]
                                ),
                                
                       ])

@callback(
    Output('figure-area', 'children'),
    Input('scenario_dropdown', 'value'),
)
def update_graph(scenario):
    figures = []
    graph1 = Barchart.WideFormBarchart(
                                'heat_generation_chart',
                                './data/plot_data_01.csv',
                                "Annual Heat Generation",
                                "YEAR",
                                2,   
                                scenario = scenario                             
                                )
    figures.append(graph1)
    
    graph2 = Hexmap.WideFormHexmap(
        "heat_generation_map",
        "./data/plot_data_02.csv",
        "Heat generation map",
        "Fraction supplied by technology (-)",
        "Air-source HP",
        2050,
        scenario=scenario)
    
    figures.append(graph2)
    return figures

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050', debug=True)