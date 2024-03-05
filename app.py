from dash import Dash, html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import json
from component import Sidebar, Tabs, Barchart, Linechart, Hexmap, ClusterChart, Pagination
from pathlib import Path

# Get the absolute path of the parent directory containing the current script
appdir = str(Path(__file__).parent.resolve())

app = Dash(__name__,
           title='Energy Transition Scenario Explorer',
           update_title="Updating ...",
           external_stylesheets=[dbc.themes.COSMO])

config = {
    'scrollZoom': True
}

# LOAD STYLE DATA
palette = 'tol-light'
continuous = False
theme = 'default'

cp = pd.read_csv(f'{appdir}/data/colour_palette.csv',
                 index_col=["PALETTE"])
cp = cp.loc[palette,:] #df.loc[row_indexer, column_indexer] : -> select all rows
cp = cp.sort_values("PC_CODE")

if not continuous:
    ca = pd.read_csv(f'{appdir}/data/colour_allocation.csv',
                     index_col=["THEME"]) 
    
    naming = pd.read_csv(f'{appdir}/data/naming.csv',
                         index_col=["NAME_IN_MODEL"])
    naming = naming["NAME"]
    ca["ARTEFACT"] = ca["ARTEFACT"].replace(naming) # Map the name with the index as the baseline
    
    ca = ca.loc[theme,:]
    ca = ca.merge(right = cp[["PC_CODE",
                            "COLOUR_CODE"]],
                  how = "left",
                  on = "PC_CODE")
    ca = ca.drop("PC_CODE", axis = 1)
    ca = ca.set_index("ARTEFACT")
    ca = ca["COLOUR_CODE"].to_dict()

if continuous:
    ca = list()
    ca.append([0,cp.loc[cp["PC_CODE"]==-1,"COLOUR_CODE"].squeeze()])
    colours = cp.loc[cp["PC_CODE"]!=-1, "COLOUR_CODE"].to_list()
    for s, c in zip(np.linspace(0.001, 1, len(colours)), colours):
        ca.append([s, c])

# cdm = utils.get_colour_map(palette="tol-light")
cdm = ca


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

# update scenario list with new scenarios
@callback(
    Output('chosen_scenario_dropdown', 'options'),
    Input('submit_button','n_clicks'),
    State('chosen_scenario_dropdown', 'options'),
    State('nz_slider', 'value'),
    State('hp_slider','value'),
    State('scenario_name_field', 'value'),
)
def update_scenario_list(count, scens, nz, hp, name):
    
    if name == '':
        name = 'Scenario '+str(count)
    exscen = [s['value'] for s in scens]
    if f'nz-{nz}_hp-{hp:02d}' not in exscen:    
        scens.append({'label': html.Span(children=name,
                                         style={'color': '#808080',
                                                'font-size': '14px'}),
                      'value': f'nz-{nz}_hp-{hp:02d}'})
    
    return scens

# update chosen scenarios if dropdown changed
@callback(
    Output('scenario_store', 'data'),
    Input('chosen_scenario_dropdown','value'),
)
def update_scenario(scens):
    
    # FIXME: currently just taking the first scenario, to be updated
    if isinstance(scens,str):
        scenarios = [scens]
    else:
        scenarios = scens
    
    return scenarios

@callback(
    Output('dropdown_component', 'style'),
    Output('figure-area','style'),
    Input('tabs', 'value'),
)
def update_filter_style(tab):
    filter_active_dropdown = {'display':'block'}
    filter_active_figures =  {'background-color':'white',
                                'padding-top':'50px',
                                'position':'absolute',
                                'z-index':0}
    filter_deactive_dropdown = {'display':'none'}
    filter_deactive_figures =  {'padding-top':'0px'}

    if tab in ['tab-2']:
        return filter_active_dropdown, filter_active_figures
    else:
        return filter_deactive_dropdown, filter_deactive_figures

@callback(
    Output('figure-area', 'children'),
    Input('scenario_store','data'),
    Input('tabs', 'value'),
    Input('area_dropdown','value'),
    State('chosen_scenario_dropdown', 'options')
)
def update_graphs(scenarios, tab, area, scen_options):
    
    scen_naming = {s['value']:s['label']['props']['children'] for s in scen_options}
    
    scenario = scenarios[0]
    # Create graphs for the chosen tab
    if tab == 'tab-1':
        
        df_gen = pd.read_csv(f'{appdir}/data/plot_data_01.csv')
        df_cost = pd.read_csv(f'{appdir}/data/plot_data_03.csv')
        df_inst = pd.read_csv(f'{appdir}/data/plot_data_09.csv')
        df_gen_loc = pd.read_csv(f'{appdir}/data/plot_data_02.csv')
        
        files = ["plot_data_04_net.csv","plot_data_04_dh.csv",
                 "plot_data_04_h2.csv","plot_data_04_build.csv"]
        df_inv = [pd.read_csv(f'{appdir}/data/'+ f) for f in files]
        
        graph6 = Barchart.ScenCompGenBarchart(
                id = "heat_gen_cost_comp",
                title="te",
                df_gen = df_gen,
                df_cost = df_cost,
                year = 2050,
                scenarios = scenarios,
                naming = scen_naming,
                colormap = cdm)
        
        graph10 = Linechart.GenericLinechart(
                id = 'hp_installations',
                df = df_inst,
                title="Heat pump installations (domestic)",
                x="YEAR",
                y="VALUE",
                category="RUN",
                scenarios = scenarios,
                naming=scen_naming,
                x_label = "Year",
                y_label = "Number of HPs installed per year (millions)",
                l_label = "Scenarios"                            
                )  
        
        graph2 = Hexmap.GenericHexmap(
                id = "heat_generation_map",
                df = df_gen_loc,
                title = None,
                zlabel = "Fraction<br>supplied by<br>technology (-)",
                techs = ["Air-source HP", "Heat interface unit",
                 "Electric resistance heater","Biomass boiler",
                 "H2 boiler"],
                year = 2050,
                scenarios = scenarios,
                naming=scen_naming,
                range_color=[0,1])
        
        graph8 = Barchart.ScenCompCostBarchart(
                id = "heat_cost_comp",
                df_cost = df_cost,
                year = 2050,
                scenarios = scenarios,
                naming = scen_naming,
                title = "Energy system cost in 2050",
                z_label = "Sector",
                y_label = "Cost (billion GBP)")
           
        graph9 = Barchart.ScenCompInvBarchart(
                id = "heat_inv_comp",
                df_inv = df_inv,
                title = "Annual investment requirements",
                scenarios = scenarios,
                naming = scen_naming)
        
        
        graph1 = Barchart.LongFormBarchart(
                'heat_generation_chart',
                f'{appdir}/data/plot_data_01.csv',
                title="testt",
                x="YEAR",
                y="VALUE",
                category="TECHNOLOGY",
                scenario = scenario,
                x_label = "year",
                y_label = "watt",
                sex =  "Technologies"                             
                )                             
        
       
        graph3 = Barchart.LongFormBarchart(
                'heat_generation_cost',
                f'{appdir}/data/plot_data_03.csv',
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
                f'{appdir}/data/plot_data_05.csv',
                "Predicted Year of Net-Zero Achievement",
                "VALUE",
                scenario = scenario,
                sex = 'year')

        
        
        glist = [dbc.Row(dbc.Col([html.Div("Technology mix",
                                          className ='section_title'),
                                 html.Hr()])),
                 dbc.Row([
                        dbc.Col(html.Div(graph6)),
                        dbc.Col(html.Div(graph10)),
                    ], className='figure_row'),
                 dbc.Row([
                        dbc.Col(html.Div(graph2)),
                        ], className='figure_row'),
                 dbc.Row(dbc.Col([html.Div("Economics",
                                className ='section_title'),
                                html.Hr()])),
                 dbc.Row([
                        dbc.Col(html.Div(graph8)),
                        dbc.Col(html.Div(graph9)),
                    ], className='figure_row'),
                 
                 dbc.Row(
                    [
                        dbc.Col(html.Div(graph1)),
                        dbc.Col(html.Div(graph3)),
                    ], className='figure_row'),
                                  
                 dbc.Row([
                        dbc.Col(html.Div(graph5)),
                    ], className='figure_row'),

                ]
        # html.Div([graph1, graph2, graph5],
        #                  style={'display': 'flex', 'flexDirection': 'row'})]
        

    elif tab == 'tab-2':
        graph7 = ClusterChart.WideFromBarCharts(
                                'regional_heat_generation',
                                f'{appdir}/data/plot_data_07.csv',
                                "Historical Data (2015) and Prediction")
        
        graph7_cluster = graph7.HeatGeneration(3, "YEAR", "REGION", area,
                                            x_label = "year", y_label = 'watt', 
                                            scenario = scenario, sex  = 'Technologies')
        glist = [graph7_cluster]
        
    elif tab == 'tab-3':
       
        glist = ["Information on everything to go here."]


    return dbc.Container(glist,
                         fluid = True,
                         style = {'background':'white'})

if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050', debug=True)