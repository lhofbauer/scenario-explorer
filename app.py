from dash import Dash, html, dcc, callback, Output, Input, State, no_update
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
                       dcc.Store(id='scenario_store')
                      ])

# DEFINE CALLBACKS

# updating levers if pre-defined scenario is chosen
@callback(
    Output('nz_slider', 'value'),
    Output('hp_slider','value'),
    Input('scenario_dropdown', 'value')
)
def update_levers(scenario):
    
    levers = scenario.split('_')
    levers = {l.split('-')[0]:int(l.split('-')[1]) for l in levers}
    return levers["nz"], levers["hp"]

# updating scenario dropdown style if levers are changed
@callback(
    Output('scenario_dropdown','style'),
    Input('nz_slider', 'value'),
    Input('hp_slider','value'),
    State('scenario_dropdown','value')
)
def update_dropdown(nz, hp, scen):
    # if levers moved, grey out dropdown
    scenario = f'nz-{nz}_hp-{hp:02d}'
    if scenario != scen:
        return {'background-color':'#d3d3d3'}
    
    return {'background-color':'#ffffff'}

# update chosen scenario if submit button is pressed
@callback(
    Output('scenario_store', 'data'),
    Input('submit_button','n_clicks'),
    State('nz_slider', 'value'),
    State('hp_slider','value'),
)
def update_scenario(count, nz, hp):
    
    scenario = f'nz-{nz}_hp-{hp:02d}'
    
    return scenario

@callback(
    Output('dropdown_component', 'style'),
    Output('figure-area','style'),
    Input('tabs', 'active_tab'),
)
def update_filter_style(tab):
    filter_active_dropdown = {'display':'block'}
    filter_active_figures =  {'background-color':'white',
                                'padding-top':'50px',
                                'position':'absolute',
                                'z-index':0}
    filter_deactive_dropdown = {'display':'none'}
    filter_deactive_figures =  {'padding-top':'0px'}

    if tab in ['tab-3']:
        return filter_active_dropdown, filter_active_figures
    else:
        return filter_deactive_dropdown, filter_deactive_figures

@callback(
    Output('figure-area', 'children'),
    Input('scenario_store','data'),
    Input('tabs', 'active_tab'),
    Input('area_dropdown','value'),
)
def update_graphs(scenario, tab, area):
    
    # Create graphs for the chosen tab
    if tab == 'tab-1':
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
        
        
        graph5 = Hexmap.LongFormHexmap(
                "national_net_zero_map",
                "./data/plot_data_05.csv",
                "Predicted Year of Net-Zero Achievement",
                "VALUE",
                scenario = scenario,
                sex = 'year')
        
        glist = [graph1, graph2, graph5]
        
    elif tab == 'tab-2':
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
        glist = [graph3]

    elif tab == 'tab-3':
        graph7 = ClusterChart.WideFromBarCharts(
                                'regional_heat_generation',
                                "./data/plot_data_07.csv",
                                "Historical Data (2015) and Prediction")
        
        graph7_cluster = graph7.HeatGeneration(3, "YEAR", "REGION", area,
                                            x_label = "year", y_label = 'watt', 
                                            scenario = scenario, sex  = 'Technologies')
        glist = [graph7_cluster]


    # Define Tab Figure Group Here
    # HG = Heat generation, CI = Cost and Investment
    # RH = Regional Heat Generation
    # fig_group = {'HG' : [graph1, graph2, graph5],
    #              'CI' : [graph3],
    #              'RH' : [graph7_cluster]}  

    # Define get figure function using abbreviation index
    def getFig(tab):
        if tab in ['tab-3']:
            return glist
        else:
            return glist

    return getFig(tab)

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050', debug=True)