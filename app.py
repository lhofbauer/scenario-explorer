from dash import Dash, html, dcc, callback, Output, Input, State, no_update
from component import Sidebar, Tabs
from component.Filter import *
from component.Chart import *
from component.Map import *
from component.Navigation import *
from component.StyleDataLoader import *
from component.FigureGrid import *
from component.Sidebar import Popover
import dash_bootstrap_components as dbc
from pathlib import Path
import pandas as pd
import numpy as np
import time

# Get the absolute path of the parent directory containing the current script
appdir = str(Path(__file__).parent.resolve())

# Announce the app and make configuration
# For more arguments: https://dash.plotly.com/reference
app = Dash(__name__,
           title = 'Energy Transition Scenario Explorer [ALPHA VERSION]',
           update_title = "Updating ...",
           external_stylesheets = [dbc.themes.COSMO],
           suppress_callback_exceptions = True)

# DEFINE LAYOUT
app.layout = html.Div([
                html.Div([Navigation.HeadBar(),
                       Sidebar.sidebar(),
                       Tabs.tabs([]),
                       dcc.Store(id='scenario_store'),
                       dcc.Store(id='response_store'),
                       dcc.Download(id="download_data")
                      ], id = 'content-container'),
                Navigation.Footer(),]
                )

# DEFINE OTHER PARAM
# - properties for heatcost dropdowns
heatcost_options_prop = [
                {'label': 'Flats',
                 'value':'FL'},
                {'label': 'Terraced',
                 'value':'TE'},
                {'label': 'Detached',
                 'value':'DE'},
                {'label': 'Semi-detached',
                 'value':'SD'}]
heatcost_options_type = [
                {'label': 'Per property',
                 'value':'prop'},
                {'label': 'Per heat generated',
                 'value':'heat'}]

# DEFINE CALLBACKS
@callback(
    Output('nz_slider', 'value'), 
    Output('hp_slider','value'),
    Output('dh_slider', 'value'),
    Output('h2_slider','value'),
    Output('lp_slider', 'value'),
    Input('scenario_dropdown', 'value')
)
def update_levers(scenario):
    
    levers = scenario.split('_')[:-1]
    levers = {l.split('-')[0]:int(l.split('-')[1]) for l in levers}
    return levers["nz"], levers["hp"], levers["dh"], levers["h2"], levers["lp"]

# updating scenario dropdown style if levers are changed
@callback(
    Output('scenario_dropdown','style'),
    Input('nz_slider', 'value'),
    Input('hp_slider','value'),
    Input('dh_slider', 'value'),
    Input('h2_slider','value'),
    Input('lp_slider', 'value'),
    Input('scenario_dropdown','value')
)
def update_dropdown(nz, hp, dh, h2, lp, scen):
    # if levers moved, grey out dropdown
    scenario = f'nz-{nz}_hp-{hp:02d}_dh-{dh:02d}_lp-{lp:02d}_h2-{h2:02d}_UK|LA|SO'
    if scenario != scen:
        return {'background-color':'#d3d3d3'}
    
    return {'background-color':'#ffffff'}

# update scenario list with new scenarios
@callback(
    Output('chosen_scenario_dropdown', 'options'),
    Output('chosen_scenario_dropdown', 'value'),
    Output('scenario_creation_response','children'),
    Output('response_store','data'),
    Input('submit_button','n_clicks'),
    State('chosen_scenario_dropdown', 'options'),
    State('chosen_scenario_dropdown', 'value'),
    State('nz_slider', 'value'),
    State('hp_slider','value'),
    State('dh_slider', 'value'),
    State('h2_slider','value'),
    State('lp_slider', 'value'),
    State('scenario_name_field', 'value'),
)
def update_scenario_list(count, scens, ch_scens, nz, hp, dh, h2, lp, name):
    response = ''
    if name == '':
        name = 'Scenario '+ str(count)
    exscen = [s['value'] for s in scens]

    if len(name) > 24:
        return no_update, no_update, no_update, no_update

    newscen = f'nz-{nz}_hp-{hp:02d}_dh-{dh:02d}_lp-{lp:02d}_h2-{h2:02d}_UK|LA|SO'
    chosen_scens = list()
    if  newscen not in exscen:    
        response = 'Scenario added to list.'
        scens.append({'label': html.Span(children=name,
                                         style={'color': '#808080',
                                                'font-size': '14px'}),
                      'value': newscen})
        
        if isinstance(ch_scens, str):
            chosen_scens = [ch_scens, newscen]
        else:
            chosen_scens = ch_scens + [newscen]
        
    
    elif newscen in exscen and count > 0:
        response = 'Scenario already exists.' 
        
    return scens, chosen_scens, response, response

# Validation message for name
@callback(
    Output('scenario_creation_response','children', allow_duplicate = True),
    Input('scenario_name_field', 'value'),
    prevent_initial_call = True
)
def update_response(name):
    if len(name) > 24:
        return "No more than 24 characters"


# the scenario creation response fades out
@callback(
    Output('scenario_creation_response','children', allow_duplicate = True),
    Input('response_store','data'),
    prevent_initial_call = True
)
def update_response(data):
    if data != '':
        time.sleep(0.5)
    
    return ''

# update chosen scenarios if dropdown changed
@callback(
    Output('scenario_store', 'data'),
    Output('scenario_chosen_response', 'children'),
    Input('chosen_scenario_dropdown','value'),
)
def update_scenario(scens):
    
    #if type(scens) == list and len(scens) > 5:
    response = 'Please select less than 6 scenarios'
    #    return no_update, response

    if isinstance(scens, str):
        scenarios = [scens]
    else:
        scenarios = scens
    print (scenarios)
    if len(scenarios) > 5:
        return no_update, response
    else:
        return scenarios, None

    
# Define callback for authority selection in the local view
@callback(
        Output('local_auth_search_collapse','is_open'),
        Input('local_auth_search_button', 'n_clicks')
)
def collapse_dropdown(click):
    is_open = False if click % 2 == 0 else True
    return is_open

    
@callback(
    Output('figure-area', 'children'),
    Input('scenario_store','data'),
    Input('tabs', 'value'),
    Input('subtabs_1','value'),
    Input('subtabs_2','value'),
    Input('local_auth_search','value'),
    State('chosen_scenario_dropdown', 'options')
)
def update_graphs(scenarios, tab, subtab_1, subtab_2, lads, scen_options):
    # - Create popover for graph titles
    # -- Load tooltip data
    with open(f'{appdir}/content/figures.json') as file:
        content = json.load(file)

    scen_naming = {s['value']:s['label']['props']['children'] for s in scen_options}
    
    # Default scenrio if cleared
    default = ['nz-2050_hp-00_dh-00_lp-00_h2-00_UK|LA|SO']
    scenarios = scenarios if len(scenarios) > 0 else default
    
    # Check lads value and set default Hartlepool
    if isinstance(lads, str):
        lads = [lads]
    if lads == []:
        lads = ['Hartlepool']
  
      
    # Create graphs for the chosen tab
    if tab == 'tab-1' and subtab_1 == 'subtab-1-1':
        
        df_gen = pd.read_csv(f'{appdir}/data/plot_data_01.csv')
        df_cost = pd.read_csv(f'{appdir}/data/plot_data_03.csv')
        df_inst = pd.read_csv(f'{appdir}/data/plot_data_09.csv')
        df_gen_loc = pd.read_csv(f'{appdir}/data/plot_data_02.csv')
        
        year = 2050       

        # Load the style data for the colormap
        style_loader = ColorMapStyle()
        cdm = style_loader.construct_cdm()
        graph6 = Chart.ScenCompGenBarchart(
                id = "heat_gen_cost_comp",
                df_gen = df_gen,
                df_cost = df_cost,
                year = year,
                scenarios = scenarios,
                naming = scen_naming,
                colormap = cdm)
        
        graph10 = Chart.GenericLinechart(
                id = 'hp_installations',
                df = df_inst,
                x="YEAR",
                y="VALUE",
                category="RUN",
                scenarios = scenarios,
                naming=scen_naming,
                x_label = "Year",
                y_label = "Number of HPs installed per year (millions)",
                l_label = "Scenarios"                            
                )
        graph2 = Map.GenericHexmap(
                id = "heat_generation_map",
                df = df_gen_loc,
                zlabel = "Fraction<br>supplied by<br>technology (-)",
                techs = ["Air-source HP", "District heating",
                 "Electric resistance heater","Biomass boiler",
                 "H2 boiler"],
                year = 2050,
                scenarios = scenarios,
                naming=scen_naming,
                range_color=[0,1])
        

        yslider = Filter.YearSlider(2025, 2055, 5, 'year_slider', 2050,
                                    tooltip = 'Year to be shown.',
                                    className = 'slider')

        glist = FigureGrid.create([
            {'title':f"Heat generation in {year}",
             'popover':{'id':'t1-1_gencomp_popover',
                        'tooltip': content['gencomp_tooltip'].format(year = year),
                        'className':'popover_figure'
                        },
            'facet':None,
            'graph':graph6,
            },
            {'title':f"Heat pump installations",
             'popover':{'id':'t1-1_hpinst_popover',
                        'tooltip': content['hpinst_tooltip'],
                        'className':'popover_figure'
                        },
            'facet':None,
            'graph':graph10,
            },
            {'title':f"Heat generation across GB",
             'popover':{'id':'t1-1_genmap_popover',
                        'tooltip': content['genmap_tooltip'],
                        'className':'popover_figure'
                        },
            'facet':html.Div(yslider),
            'graph':graph2,
            },
        ], columns_per_row = "2 1")
        
           
    elif tab == 'tab-1' and subtab_1 == 'subtab-1-2':
        
        
                            
        files = ["plot_data_04_net.csv","plot_data_04_dh.csv",
                 "plot_data_04_h2.csv","plot_data_04_build.csv"]
        df_inv = [pd.read_csv(f'{appdir}/data/'+ f) for f in files]
        df_cost = pd.read_csv(f'{appdir}/data/plot_data_03.csv')
        
        prop = "FL"
        ty = "prop"
        
        if ty == "prop":
            df_hcost = pd.read_csv(f'{appdir}/data/plot_data_11_'+prop+'.csv',
                                   index_col=["RUN","REGION","YEAR"])
            label = "Annual heating<br>cost per property<br>(norm.)"
        elif ty == "heat":
            df_hcost = pd.read_csv(f'{appdir}/data/plot_data_12_'+prop+'.csv',
                                   index_col=["RUN","REGION","YEAR"])
            label = "Annual heating<br>cost per heat<br>generated (norm.)"

        
        # normalize with GB average (except GB values)
        df_hcost[~df_hcost.index.get_level_values("REGION")
                 .str.startswith("GB")] = (df_hcost[~df_hcost
                                                    .index.get_level_values("REGION")
                                                    .str.startswith("GB")]
                                                    /df_hcost.xs((scenarios[0],
                                                                  "GB"),
                                                                 level=(0,1)))
        df_hcost_gb = df_hcost.xs("GB",level=1)
        df_hcost_gb = df_hcost_gb/df_hcost_gb.xs((scenarios[0],2015),level=(0,1)).squeeze()
        df_hcost_gb = df_hcost_gb[df_hcost_gb.index.get_level_values("YEAR")>=2025]
        df_hcost_gb = df_hcost_gb.reset_index()
        df_hcost = df_hcost.reset_index()

                                            
                                            
                                                                                      
        graph8 = Chart.ScenCompCostBarchart(
                id = "heat_cost_comp",
                df_cost = df_cost,
                year = 2050,
                scenarios = scenarios,
                naming = scen_naming,
                z_label = "Sector",
                y_label = "Total system cost (billion GBP)")
           
        graph9 = Chart.ScenCompInvBarchart(
                id = "heat_inv_comp",
                df_inv = df_inv,
                y_label= "Investments (billion GBP)",
                scenarios = scenarios,
                naming = scen_naming)
        
        # Create dropdowns for graph3
        heatcost_prop_dropdown = Filter.Dropdown(heatcost_options_prop, 
                                                 'heatcost_prop_dropdown',
                                                 className = 'heatcost_dropdowns')
        heatcost_type_dropdown = Filter.Dropdown(heatcost_options_type, 
                                                 'heatcost_type_dropdown',
                                                 className = 'heatcost_dropdowns')

        graph3 = Map.GenericHexmap(
                id = "hcost_maps",
                df = df_hcost,
                year = 2050,
                zlabel = label,
                scenarios = scenarios,
                naming=scen_naming,
                range_color=[0.8,1.2],
                textangle= len(scenarios) * 15)
        
        graph4 = Chart.GenericLinechart(
                id = 'hcost_path',
                df = df_hcost_gb,
                x="YEAR",
                y="VALUE",
                category="RUN",
                scenarios = scenarios,
                naming=scen_naming,
                y_range = [0,df_hcost_gb["VALUE"].max()+0.05],
                x_label = "Year",
                y_label = "Heating cost per property (normalized)",
                l_label = "Scenarios"                            
                )
        
        glist = FigureGrid.create([
            {'title': "Total energy system cost in 2050",
             'popover':{'id':'t1-2_syscost_popover',
                        'tooltip': content['syscost_tooltip'],
                        'className':'popover_figure'
                        },
            'facet':None,
            'graph':graph8,
            },
            {'title': "Average annual investment requirements",
             'popover':{'id':'t1-2_invreq_popover',
                        'tooltip': content['invreq_tooltip'],
                        'className':'popover_figure'
                        },
            'facet':None,
            'graph':graph9,
            },
            {'title': "Heating system cost (normalized) [beta]",
             'popover':{'id':'t1-2_costmap_popover',
                        'tooltip': content['costmap_tooltip'],
                        'className':'popover_figure'
                        },
            'facet':html.Div([html.Div(heatcost_prop_dropdown),
                              html.Div(heatcost_type_dropdown)]),
            'graph':graph3,
            },
            {'title': "Heating system cost (normalized) [beta]",
             'popover':{'id':'t1-2_heatcost_popover',
                        'tooltip': content['heatcost_tooltip'],
                        'className':'popover_figure'
                        },
            'facet':None,
            'graph':graph4,
            },
        ], columns_per_row = '2 1 1')

                
    elif tab == 'tab-1' and subtab_1 == 'subtab-1-3':
       
        df_em = pd.read_csv(f'{appdir}/data/plot_data_10.csv')
        df_em_loc = pd.read_csv(f'{appdir}/data/plot_data_05.csv')
        
        graph1 = Chart.GenericLinechart(
                id = 'em_pathways',
                df = df_em,
                title=None,
                x="YEAR",
                y="VALUE",
                category="RUN",
                scenarios = scenarios,
                naming=scen_naming,
                x_label = "Year",
                y_label = "CO2eq emissions (kt)",
                l_label = "Scenarios"                            
                )
        
        graph2 = Map.GenericHexmap(
                id = "net-zero_map",
                df = df_em_loc,
                title = None,
                zlabel = "Year of 100%<br> emission<br> reduction",
                scenarios = scenarios,
                naming=scen_naming,
                range_color=[2025,2060])
        

        
        glist = FigureGrid.create([
            {'title': "Energy-related CO2 emissions",
             'popover':{'id':'t1-3empath_popover',
                        'tooltip': content['empath_tooltip'],
                        'className':'popover_figure'
                        },
            'facet':None,
            'graph':graph1,
            },
            {'title': "First year of net-zero emissions",
             'popover':{'id':'t1-3_nymap_popover',
                        'tooltip': content['nymap_tooltip'],
                        'className':'popover_figure'
                        },
            'facet':None,
            'graph':graph2,
            },
        ],
        columns_per_row = '1 1'
        )

    
    elif tab == 'tab-2' and subtab_2 == 'subtab-2-1':
        
        df_inst_loc = pd.read_csv(f'{appdir}/data/plot_data_09l.csv')
        df_gen_loc = pd.read_csv(f'{appdir}/data/plot_data_02n.csv')
        
        # convert to thousands
        df_inst_loc["VALUE"] = df_inst_loc["VALUE"]*1000
        
        
        # - Create popover for graph titles
        year = 2050

        # Load the style data for the colormap
        style_loader = ColorMapStyle()
        cdm = style_loader.construct_cdm()
        graph6 = Chart.ScenLocalCompGenBarchart(
                id = "heat_gen_cost_local_comp",
                title=None,
                df_gen = df_gen_loc,
                year = year,
                lads = lads,
                y_label='Fraction supplied by technology (-)',
                scenarios = scenarios,
                naming = scen_naming,
                colormap = cdm)
        
        graph10 = Chart.GenericLinechart(
                id = 'hp_installations_loc',
                df = df_inst_loc,
                title=None,
                x="YEAR",
                y="VALUE",
                category="RUN",
                scenarios = scenarios,
                lads = lads,
                naming=scen_naming,
                x_label = "Year",
                y_label = "Number of HPs installed per year (thousands)",
                l_label = None                            
                )
        
        glist = FigureGrid.create([
            {'title': f"Heat generation in {year}",
             'popover':{'id':'t2-1_gencomp_popover',
                        'tooltip': content['local_gencomp_tooltip'],
                        'className':'popover_figure'
                        },
            'facet':None,
            'graph':graph6,
            },
            {'title': "Heat pump installations",
             'popover':{'id':'t2-1_hpinst_popover',
                        'tooltip': content['local_hpinst_tooltip'],
                        'className':'popover_figure'
                        },
            'facet':None,
            'graph':graph10,
            },
        ],
        columns_per_row = '2'
        )

    elif tab == 'tab-2' and subtab_2 == 'subtab-2-2':

        files = ["plot_data_04_loc_net.csv","plot_data_04_loc_dh.csv",
                 "plot_data_04_loc_h2.csv","plot_data_04_loc_build.csv"]
        df_inv = [pd.read_csv(f'{appdir}/data/'+ f) for f in files]
        df_hcost = pd.read_csv(f'{appdir}/data/plot_data_11n_FL.csv')
        df_hcost = df_hcost.loc[df_hcost["YEAR"]>=2025,:]                                                                      
        
        graph1 = Chart.ScenCompInvBarchart(
                id = "heat_inv_comp",
                df_inv = df_inv,
                title = None,
                y_label= "Investment requirements (million GBP)",
                scenarios = scenarios,
                lads = lads,
                naming = scen_naming)
        
                                            
        graph2 = Chart.GenericLinechart(
                id = 'hcost_path',
                df = df_hcost,
                title=None,
                x="YEAR",
                y="VALUE",
                category="RUN",
                scenarios = scenarios,
                lads = lads,
                naming=scen_naming,
                y_range= [0, df_hcost.loc[df_hcost['RUN'].isin(scenarios) &
                                     df_hcost['REGION'].isin(lads),"VALUE"].max()+20],
                x_label = "Year",
                y_label = "Annual heating system cost per property (GBP)",
                l_label = None                           
                )     
     
        glist = FigureGrid.create([
            {'title': "Average annual investment requirements",
             'popover':{'id':'t2-2_invreq_popover',
                        'tooltip': content["local_invreq_tooltip"],
                        'className':'popover_figure'
                        },
            'facet':None,
            'graph':graph1,
            },
            {'title': "Heating system cost per property (flat) [beta]",
             'popover':{'id':'t2-2_heatcost_popover',
                        'tooltip': content["local_heatcost_tooltip"],
                        'className':'popover_figure'
                        },
            'facet':None,
            'graph':graph2,
            },
        ],
        columns_per_row = '2'
        )
        
    elif tab == 'tab-2' and subtab_2 == 'subtab-2-3':
        
        # - Create popover for graph titles
            
        df_em = pd.read_csv(f'{appdir}/data/plot_data_10_loc.csv')
        
        graph1 = Chart.GenericLinechart(
                id = 'em_pathways',
                df = df_em,
                title=None,
                x="YEAR",
                y="VALUE",
                category="RUN",
                scenarios = scenarios,
                lads=lads,
                naming=scen_naming,
                x_label = "Year",
                y_label = "CO2eq emissions (kt)",
                l_label = "Scenarios"                            
                )
            
  
        glist = FigureGrid.create([
            {'title': "Energy-related CO2 emissions",
             'popover':{'id':'t3-3_empath_popover',
                        'tooltip': content["local_empath_tooltip"],
                        'className':'popover_figure'
                        },
            'facet':None,
            'graph':graph1,
            },
        ],
        columns_per_row = '1'
        )


        
    elif tab == 'tab-3':
       
        glist = [html.Div([content['help_information'][0],
                            content['help_information'][1],
                            html.Br(), html.Br(),
                            content['help_information'][2]])]


    return dbc.Container(glist,
                         fluid = True,
                         style = {'background':'white'})

@callback(
    Output('heat_generation_map', 'figure'),
    Input('year_slider', 'value'),
    State('scenario_store','data'), 
    State('chosen_scenario_dropdown', 'options'),
)
def update_heat_gen_maps(year, scenarios, scen_options):
    
    scen_naming = {s['value']:s['label']['props']['children'] for s in scen_options}
    df_gen_loc = pd.read_csv(f'{appdir}/data/plot_data_02.csv')

    # Default scenrio if cleared
    default = ['nz-2050_hp-00_dh-00_lp-00_h2-00_UK|LA|SO']
    scenarios = scenarios if len(scenarios) > 0 else default
    
    fig = Map.GenericHexmap(
            id = "heat_generation_map",
            df = df_gen_loc,
            title = None,
            zlabel = "Fraction<br>supplied by<br>technology (-)",
            techs = ["Air-source HP", "District heating",
              "Electric resistance heater","Biomass boiler",
              "H2 boiler"],
            year = year,
            scenarios = scenarios,
            naming=scen_naming,
            range_color=[0,1],
            figonly=True)

    return fig

@callback(
    Output('hcost_maps', 'figure'),
    Input('heatcost_prop_dropdown', 'value'),
    Input('heatcost_type_dropdown', 'value'),
    State('scenario_store','data'), 
    State('chosen_scenario_dropdown', 'options'),
)
def update_heatcosts_maps(prop, ty, scenarios, scen_options):
    
    scen_naming = {s['value']:s['label']['props']['children'] for s in scen_options}
    if ty == "prop":
        df_hcost = pd.read_csv(f'{appdir}/data/plot_data_11_'+prop+'.csv',
                               index_col=["RUN","REGION","YEAR"])
        label = "Annual heating<br>cost per property<br>(norm.)"
    elif ty == "heat":
        df_hcost = pd.read_csv(f'{appdir}/data/plot_data_12_'+prop+'.csv',
                               index_col=["RUN","REGION","YEAR"])
        label = "Annual heating<br>cost per heat<br>generated (norm.)"
        
    # Default scenario if cleared
    default = ['nz-2050_hp-00_dh-00_lp-00_h2-00_UK|LA|SO']
    scenarios = scenarios if len(scenarios) > 0 else default
    
    
    # normalize with GB average (except GB values)
    df_hcost[~df_hcost.index.get_level_values("REGION")
             .str.startswith("GB")] = (df_hcost[~df_hcost
                                                .index.get_level_values("REGION")
                                                .str.startswith("GB")]
                                                /df_hcost.xs((scenarios[0],
                                                              "GB"),
                                                             level=(0,1)))
    df_hcost_gb = df_hcost.xs("GB",level=1)
    df_hcost_gb = df_hcost_gb/df_hcost_gb.xs((scenarios[0],2015),level=(0,1)).squeeze()
    df_hcost_gb = df_hcost_gb.reset_index()
    df_hcost = df_hcost.reset_index()
    

    fig = Map.GenericHexmap(
            id = "hcost_maps",
            df = df_hcost,
            title = None,
            year = 2050,
            zlabel = label,
            scenarios = scenarios,
            naming=scen_naming,
            range_color=[0.7,1.3],
            figonly=True)

    return fig


if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050')