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
                       Tabs.tabs([]),])

@callback(
    Output('figure-area', 'children'),
    Input('scenario_dropdown', 'value'),
    Input('tabs', 'active_tab'),
)
def update_graph(scenario, tab):
    figures = []
    graph1 = Barchart.WideFormBarchart(
            'heat_generation_chart',
            './data/plot_data_01.csv',
            "Annual Heat Generation",
            "YEAR",
            2,   
            scenario = scenario,
            x_label = "year",
            y_label = "watt",
            sex =  "Technologies"                             
            )                             
    
    graph2 = Hexmap.WideFormHexmap(
            "heat_generation_map",
            "./data/plot_data_02.csv",
            "Heat Generation Map",
            "Fraction supplied by technology (-)",
            "Air-source HP",
            2050,
            scenario = scenario)
    
    graph3 = Barchart.LongFormBarchart(
            'heat_generation_cost',
            './data/plot_data_03.csv',
            "Heat Generation Cost",
            "YEAR",
            "VALUE",
            "TECHNOLOGY",   
            scenario = scenario,
            x_label = "year",
            y_label = "cost",
            sex = 'Technologies'                             
            )

    graph5 = Hexmap.LongFormHexmap(
            "national_net_zero_map",
            "./data/plot_data_05.csv",
            "National Net-Zero Map",
            "VALUE",
            scenario = scenario,
            sex = 'Year of net-zero achievement')                         

    if tab == 'tab-1':
        figures.extend([graph1, graph2, graph5])
    else:
        figures.extend([graph3])

    return figures

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050', debug=True)