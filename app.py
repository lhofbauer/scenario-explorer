from dash import Dash, html, dcc, callback, Output, Input, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
import json
from component import Sidebar, Tabs, Barchart, Hexmap, ClusterChart, Pagination


app = Dash(__name__, external_stylesheets=[dbc.themes.COSMO])

config = {
    'scrollZoom': True
}

# EXTRACT SCENARIOS
df = pd.read_csv('./data/plot_data_01.csv')
scenarios = sorted(df['RUN'].unique())


# DEFINE LAYOUT
app.layout = html.Div([Sidebar.sidebar(),
                       Tabs.tabs([]),
                      ])

@callback(
    Output('figure-area', 'children'),
    Output('dropdown_component', 'style'),
    Output('figure-area','style'),
    Input('scenario_dropdown', 'value'),
    Input('tabs', 'active_tab'),
    Input('area_dropdown','value'),
)
def update_graph(scenario, tab, area):
    
    graph1 = Barchart.WideFormBarchart(
            'heat_generation_chart',
            './data/plot_data_01.csv',
            "Historical Data (2015) and Prediction",
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
            "Year 2050 Predication by Region",
            "Fraction supplied by technology (-)",
            "Air-source HP",
            2050,
            scenario = scenario)
    
    graph3 = Barchart.LongFormBarchart(
            'heat_generation_cost',
            './data/plot_data_03.csv',
            "Historical Data (2015) and Prediction",
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
            "Predicted Year of Net-Zero Achievement",
            "VALUE",
            scenario = scenario,
            sex = 'year')   
    
    graph7 = ClusterChart.WideFromBarCharts(
                            'regional_heat_generation',
                            "./data/plot_data_07.csv",
                            "Historical Data (2015) and Prediction")
    
    graph7_cluster = graph7.HeatGeneration(3, "YEAR", "REGION", area,
                                        x_label = "year", y_label = 'watt', 
                                        scenario = scenario, sex  = 'Technologies')


    # Define Tab Figure Group Here
    # HG = Heat generation, CI = Cost and Investment
    # RH = Regional Heat Generation
    fig_group = {'HG' : [graph1, graph2, graph5],
                 'CI' : [graph3],
                 'RH' : [graph7_cluster]}  

    # Define get figure function using abbreviation index
    def getFig(tab):
        abbre = list(fig_group.keys())
        if tab == 'tab-3':
            return fig_group[abbre[int(tab[-1]) - 1]], {'display':'block'}, {'background-color':'white',
                                                                             'padding-top':'50px',
                                                                             'position':'absolute',
                                                                             'z-index':0}
        else:
            return fig_group[abbre[int(tab[-1]) - 1]], {'display':'none'}, {'padding-top':'0px'}

    return getFig(tab)

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050', debug=True)