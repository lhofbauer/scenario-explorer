from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import json
from component import Sidebar, Tabs, Barchart


app = Dash(__name__, external_stylesheets=[dbc.themes.FLATLY])

config = {
    'scrollZoom': True
}

app.layout = html.Div([Sidebar.sidebar(),
                       Tabs.tabs([
                           Barchart.WideFormBarchart(
                                'heat_generation_chart',
                                './raw data/data/plot_data_01.csv',
                                "Annual Heat Generation",
                                "YEAR",
                                2
                                ),
                            Barchart.WideFormBarchart(
                                'heat_generation_chart',
                                './raw data/data/plot_data_01.csv',
                                "Annual Heat Generation",
                                "YEAR",
                                2
                                )]
                                ),
                                
                       ])


if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050', debug=True)