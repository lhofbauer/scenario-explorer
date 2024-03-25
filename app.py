from dash import Dash, html, dcc, callback, Output, Input, State, no_update
import dash_bootstrap_components as dbc
import pandas as pd
import numpy as np
import plotly.express as px
import json
from component import Sidebar, Tabs, Barchart, Linechart, Hexmap, ClusterChart, Navbar
from pathlib import Path
import time

# Get the absolute path of the parent directory containing the current script
appdir = str(Path(__file__).parent.resolve())

app = Dash(__name__,
           title = 'Energy Transition Scenario Explorer',
           update_title = "Updating ...",
           external_stylesheets = [dbc.themes.COSMO],
           suppress_callback_exceptions = True)

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
app.layout = html.Div([
                html.Div([Navbar.createNavbar(),
                       Sidebar.sidebar(),
                       Tabs.tabs([]),
                       dcc.Store(id='scenario_store'),
                       dcc.Store(id='response_store'),
                       dcc.Download(id="download_data")
                      ], id = 'content-container'),
                Navbar.createFooter(),]
                )



# DEFINE CALLBACKS

# limiting number of chosen scenarios
# @app.callback(
#     Output("chosen_scenario_dropdown", component_property="options"),
#     Input("chosen_scenario_dropdown", component_property="value"),
#     State("chosen_scenario_dropdown", component_property="options"),
# )
# def update_scenario_dropdown_options(scenarios, options):
#     if len(scenarios) > 3:
#         return [s for s in options if s["value"] in scenarios]
#     else:
#         return OPTIONS
    
# updating levers if pre-defined scenario is chosen
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
    Output('scenario_creation_response','children'),
    Output('response_store','data'),
    Input('submit_button','n_clicks'),
    State('chosen_scenario_dropdown', 'options'),
    State('nz_slider', 'value'),
    State('hp_slider','value'),
    State('dh_slider', 'value'),
    State('h2_slider','value'),
    State('lp_slider', 'value'),
    State('scenario_name_field', 'value'),
)
def update_scenario_list(count, scens, nz, hp, dh, h2, lp, name):
    response = ''
    if name == '':
        name = 'Scenario '+str(count)
    exscen = [s['value'] for s in scens]

    newscen = f'nz-{nz}_hp-{hp:02d}_dh-{dh:02d}_lp-{lp:02d}_h2-{h2:02d}_UK|LA|SO'
    
    if  newscen not in exscen:    
        response = 'Scenario added to list.'
        scens.append({'label': html.Span(children=name,
                                         style={'color': '#808080',
                                                'font-size': '14px'}),
                      'value': newscen})
    elif newscen in exscen and count > 0:
        response = 'Scenario already exists.' 
        
    return scens, response, response

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
    Input('chosen_scenario_dropdown','value'),
)
def update_scenario(scens):
    
    if isinstance(scens, str):
        scenarios = [scens]
    else:
        scenarios = scens
    
    return scenarios

# @callback(
#     Output('dropdown_component', 'style'),
#     Input('tabs', 'value'),
# )
# def update_filter_style(tab):
#     filter_active_dropdown = {'display':'block'}
#     filter_deactive_dropdown = {'display':'none'}

#     if tab in ['tab-2']:
#         return filter_active_dropdown
#     else:
#         return filter_deactive_dropdown
    
    
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
def update_graphs(scenarios, tab, subtab_1,subtab_2, lads, scen_options):
    
    scen_naming = {s['value']:s['label']['props']['children'] for s in scen_options}
    
    # Default scenrio if cleared
    default = ['nz-2050_hp-00_dh-00_lp-00_h2-00_UK|LA|SO']
    scenarios = scenarios if len(scenarios) > 0 else default
    
    # Check lads value and set default Hartlepool
    if isinstance(lads, str):
        lads = [lads]
    if lads == []:
        lads = ['Hartlepool']

    hover_popover_object = Sidebar.Popover('hover')  
      
    # Create graphs for the chosen tab
    if tab == 'tab-1' and subtab_1 == 'subtab-1-1':
        
        df_gen = pd.read_csv(f'{appdir}/data/plot_data_01.csv')
        df_cost = pd.read_csv(f'{appdir}/data/plot_data_03.csv')
        df_inst = pd.read_csv(f'{appdir}/data/plot_data_09.csv')
        df_gen_loc = pd.read_csv(f'{appdir}/data/plot_data_02.csv')
        
        year = 2050
        # - Create popover for graph titles
        content_gencomp_tooltip = ("This graph shows the heat generation in"
                                   " domestic and non-domestic properties by"
                                   " technology in the base years (2015-2020)"
                                   f" and for each scenario in {year}."
                                   " It also shows the total energy system cost"
                                   " (for meeting energy demands of the"
                                   " building sector, including other"
                                   " electricity and gas demand).")
        content_hpinst_tooltip = ("This graph shows the number of heat pumps"
                                   " installed annually in domestic properties"
                                   " for each scenario.")
        content_genmap_tooltip = ("These hexmaps show the fraction of heat demand"
                                   " met by the most common technologies (columns)"
                                   " for all scenarios (rows) in each"
                                   " local authority in Great Britain. Hover"
                                   " over a hexagon to see the name of the local"
                                   " authority.")
        

        gencomp_popover = hover_popover_object.create('t1-1_gencomp_popover', content_gencomp_tooltip,'popover_figure')
        hpinst_popover = hover_popover_object.create('t1-1_hpinst_popover', content_hpinst_tooltip,'popover_figure')
        genmap_popover = hover_popover_object.create('t1-1_genmap_popover', content_genmap_tooltip,'popover_figure')


        graph6 = Barchart.ScenCompGenBarchart(
                id = "heat_gen_cost_comp",
                title=None,#f"Heat generation in {year}",,
                df_gen = df_gen,
                df_cost = df_cost,
                year = year,
                scenarios = scenarios,
                naming = scen_naming,
                colormap = cdm)
        
        graph10 = Linechart.GenericLinechart(
                id = 'hp_installations',
                df = df_inst,
                title=None,
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
        
        marks ={y:str(y) for y in range(2025,2056,5)}
        yslider_popover_object = Sidebar.Popover('hover')
        yslider_popover = yslider_popover_object.create('yslider1_popover', 
                                                        'Year to be shown.','popover_lever')
        yslider = html.Div([   
                    html.Div(['Year', yslider_popover], className = 'facet_item_name'),
                    dcc.Slider(min = 2025, max = 2055, step = None, marks = marks,
                             value = 2050,
                             id= 'year_slider',
                             className = 'slider'),
                    ])
        
        glist = [dbc.Row([
                        dbc.Col([dbc.Stack([html.Div([f"Heat generation in {year}"],
                                                     className='figure_title'),
                                            gencomp_popover],
                                          direction="horizontal"),
                                 graph6]),
                        dbc.Col([dbc.Stack([html.Div([f"Heat pump installations"],
                                                     className='figure_title'),
                                            hpinst_popover],
                                          direction="horizontal"),
                                 graph10]),
                    ], className='figure_row'),
                dbc.Row([dbc.Col([dbc.Stack([html.Div([f"Heat generation across GB"],
                                             className='figure_title'),
                                    genmap_popover,html.Br(), html.Div(yslider)],
                                  direction="horizontal"),
                          dcc.Loading(html.Div(graph2))])
                         ],className='figure_row')
                    

                        # dcc.Loading(dbc.Col(html.Div(graph2)))],
                 ]
           
    elif tab == 'tab-1' and subtab_1 == 'subtab-1-2':
        
        content_syscost_tooltip = ("This graph shows the total annual energy system cost"
                                   " (for meeting the building sector demand)"
                                   " split based on different parts of the system.")
        content_invreq_tooltip = ("This graph shows average annual investment"
                                  " requirements for the period 2023 to 2054.")
        content_costmap_tooltip = ("These hexmaps show the annual heating cost"
                                   " per domestic property (taking terraced"
                                   " houses as reference)"
                                   " for 2050 normalized with the average cost"
                                   " for GB in the scenario shown on the left.")
        content_heatcost_tooltip = ("This graph shows the annual heating cost"
                                   " per domestic property (taking terraced"
                                   " houses as reference)"
                                   " normalized with the cost for the"
                                   " base year period for Base net-zero scenario."
                                   " The difference in the base year cost"
                                   " is due to differences in cost allocation"
                                   " across years (e.g., a faster phase out of"
                                   " gas boilers will lead cost for stranded gas"
                                   " network investments"
                                   " to be allocated to years where gas is still used).")
        
        
        syscost_popover = hover_popover_object.create('t1-2_syscost_popover', content_syscost_tooltip,'popover_figure')
        invreq_popover = hover_popover_object.create('t1-2_invreq_popover', content_invreq_tooltip,'popover_figure')
        costmap_popover = hover_popover_object.create('t1-2_costmap_popover', content_costmap_tooltip,'popover_figure')
        heatcost_popover = hover_popover_object.create('t1-2_heatcost_popover', content_heatcost_tooltip,'popover_figure')
                            


        files = ["plot_data_04_net.csv","plot_data_04_dh.csv",
                 "plot_data_04_h2.csv","plot_data_04_build.csv"]
        df_inv = [pd.read_csv(f'{appdir}/data/'+ f) for f in files]
        df_cost = pd.read_csv(f'{appdir}/data/plot_data_03.csv')
        df_hcost = pd.read_csv(f'{appdir}/data/plot_data_11.csv',
                               index_col=["RUN","REGION","YEAR"])
        
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

                                            
                                            
                                                                                      
        graph8 = Barchart.ScenCompCostBarchart(
                id = "heat_cost_comp",
                df_cost = df_cost,
                year = 2050,
                scenarios = scenarios,
                naming = scen_naming,
                title = None,
                z_label = "Sector",
                y_label = "Total system cost (billion GBP)")
           
        graph9 = Barchart.ScenCompInvBarchart(
                id = "heat_inv_comp",
                df_inv = df_inv,
                title = None,
                y_label= "Investments (billion GBP)",
                scenarios = scenarios,
                naming = scen_naming)
        
        graph3 = Hexmap.GenericHexmap(
                id = "hcost_maps",
                df = df_hcost,
                title = None,
                year = 2050,
                zlabel = "Annual heating<br>cost per property<br>(rel. to avg.)",
                scenarios = scenarios,
                naming=scen_naming,
                range_color=[0.8,1.2])
        
        graph4 = Linechart.GenericLinechart(
                id = 'hcost_path',
                df = df_hcost_gb,
                title=None,
                x="YEAR",
                y="VALUE",
                category="RUN",
                scenarios = scenarios,
                naming=scen_naming,
                x_label = "Year",
                y_label = "Heating cost per property (normalized)",
                l_label = "Scenarios"                            
                )
        
        # graph1 = Barchart.LongFormBarchart(
        #         'heat_generation_chart',
        #         f'{appdir}/data/plot_data_01.csv',
        #         title="testt",
        #         x="YEAR",
        #         y="VALUE",
        #         category="TECHNOLOGY",
        #         scenario = scenario,
        #         x_label = "year",
        #         y_label = "watt",
        #         sex =  "Technologies"                             
        #         )                             
        
       
        # graph2 = Barchart.LongFormBarchart(
        #         'heat_generation_cost',
        #         f'{appdir}/data/plot_data_03.csv',
        #         "Historical Data (2015) and Prediction",
        #         "YEAR",
        #         "VALUE",
        #         "TECHNOLOGY",   
        #         scenario = scenario,
        #         x_label = "year",
        #         y_label = "cost",
        #         sex = 'Technologies'                             
        #         )
        

        glist = [dbc.Row([
                        dbc.Col([dbc.Stack([html.Div([f"Total energy system cost in 2050"],
                                                     className='figure_title'),
                                            syscost_popover],
                                          direction="horizontal"),
                                 graph8]),
                        dbc.Col([dbc.Stack([html.Div([f"Average annual investment requirements"],
                                                     className='figure_title'),
                                            invreq_popover],
                                          direction="horizontal"),
                                 graph9]),
                    ], className='figure_row'),
                dbc.Row([
                            dbc.Col([dbc.Stack([html.Div([f"Heating cost per property (normalized)"],
                                                         className='figure_title'),
                                                costmap_popover],
                                              direction="horizontal"),
                                     graph3]),
                        ], className='figure_row'),
                dbc.Row([
                                dbc.Col([dbc.Stack([html.Div([f"Heating cost per property (normalized)"],
                                                             className='figure_title'),
                                                    heatcost_popover],
                                                  direction="horizontal"),
                                         graph4]),
                                dbc.Col([]),
                            ], className='figure_row'),
                ]
        
    elif tab == 'tab-1' and subtab_1 == 'subtab-1-3':
        
        content_empath_tooltip = ("This graph shows CO2 emissions from the"
                                  " energy system (with regard to the building"
                                  " sector).")
        content_nymap_tooltip = ("These hexmaps show the year local authorities"
                                 " reach net-zero emissions (assumed to be"
                                 " <2 % of base year emissions)")

        
        
        empath_popover = hover_popover_object.create('t1-3empath_popover', content_empath_tooltip,'popover_figure')
        nymap_popover = hover_popover_object.create('t1-3_nymap_popover', content_nymap_tooltip,'popover_figure')
   

        df_em = pd.read_csv(f'{appdir}/data/plot_data_10.csv')
        df_em_loc = pd.read_csv(f'{appdir}/data/plot_data_05.csv')
        
        graph1 = Linechart.GenericLinechart(
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
        
        graph2 = Hexmap.GenericHexmap(
                id = "net-zero_map",
                df = df_em_loc,
                title = None,
                zlabel = "Year of 98%<br> emission<br> reduction",
                scenarios = scenarios,
                naming=scen_naming,
                range_color=[2025,2060])
        

        
        glist = [dbc.Row([
                            dbc.Col([dbc.Stack([html.Div([f"Energy-related CO2 emissions"],
                                                         className='figure_title'),
                                                empath_popover],
                                              direction="horizontal"),
                                     graph1]),
                            dbc.Col([]),
                        ], className='figure_row'),
                dbc.Row([
                                    dbc.Col([dbc.Stack([html.Div([f"First year of net-zero emissions"],
                                                                 className='figure_title'),
                                                        nymap_popover],
                                                      direction="horizontal"),
                                             graph2]),
                                ], className='figure_row'),
                        
                ]
        # html.Div([graph1, graph2, graph5],
        #                  style={'display': 'flex', 'flexDirection': 'row'})]
        

    
    elif tab == 'tab-2' and subtab_2 == 'subtab-2-1':
        
        df_inst_loc = pd.read_csv(f'{appdir}/data/plot_data_09l.csv')
        df_gen_loc = pd.read_csv(f'{appdir}/data/plot_data_02n.csv')
        
        # convert to thousands
        df_inst_loc["VALUE"] = df_inst_loc["VALUE"]*1000
        
        year = 2050
        # - Create popover for graph titles
        
        content_gencomp_tooltip = ("This graph shows the heat generation in"
                                   " domestic and non-domestic properties by"
                                   " technology in the base years (2015-2020)"
                                   " and for each scenario and local authority"
                                   f" in {year}.")
        content_hpinst_tooltip = ("This graph shows the number of heat pumps"
                                   " installed annually in domestic properties"
                                   " for each scenario and local authority.")

        gencomp_popover = hover_popover_object.create('t2-1_gencomp_popover', content_gencomp_tooltip,'popover_figure')
        hpinst_popover = hover_popover_object.create('t2-1_hpinst_popover', content_hpinst_tooltip,'popover_figure')
 
        
        graph6 = Barchart.ScenLocalCompGenBarchart(
                id = "heat_gen_cost_local_comp",
                title=None,
                df_gen = df_gen_loc,
                year = year,
                lads = lads,
                y_label='Fraction supplied by technology (-)',
                scenarios = scenarios,
                naming = scen_naming,
                colormap = cdm)
        
        graph10 = Linechart.GenericLinechart(
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
        
        glist = [dbc.Row([
                        dbc.Col([dbc.Stack([html.Div([f"Heat generation in {year}"],
                                                     className='figure_title'),
                                            gencomp_popover],
                                          direction="horizontal"),
                                 graph6]),
                        dbc.Col([dbc.Stack([html.Div([f"Heat pump installations"],
                                                     className='figure_title'),
                                            hpinst_popover],
                                          direction="horizontal"),
                                 graph10]),
                    ], className='figure_row'),



                 ]
        # graph7 = ClusterChart.WideFromBarCharts(
        #                         'regional_heat_generation',
        #                         f'{appdir}/data/plot_data_07.csv',
        #                         "Historical Data (2015) and Prediction")
        
        # graph7_cluster = graph7.HeatGeneration(3, "YEAR", "REGION", area,
        #                                     x_label = "year", y_label = 'watt', 
        #                                     scenario = scenario, sex  = 'Technologies')
        # glist = [graph7_cluster]
    elif tab == 'tab-2' and subtab_2 == 'subtab-2-2':
        
        content_invreq_tooltip = ("This graph shows average annual investment"
                                  " requirements for the period 2023 to 2054.")

        content_heatcost_tooltip = ("This graph shows the annual heating cost"
                                   " per flat (as example of per property cost)."
                                   " This includes cost for heating system and"
                                   " the supply of energy. It relates to system cost"
                                   " and does not necessarily directly correlate"
                                   " with price/cost paid by households (e.g.,"
                                   " it does not include margins of power"
                                   " producers)"
                                   " The difference in the base year cost across"
                                   " the same LAD but different scenarios"
                                   " is due to differences in cost allocation"
                                   " across years (e.g., a faster phase out of"
                                   " gas boilers will lead to cost for stranded gas"
                                   " network investments"
                                   " to be allocated to years where gas is still used).")
        
        
       
        invreq_popover = hover_popover_object.create('t2-2_invreq_popover', content_invreq_tooltip,'popover_figure')  
        heatcost_popover = hover_popover_object.create('t2-2_heatcost_popover', content_heatcost_tooltip,'popover_figure')
                            


        files = ["plot_data_04_loc_net.csv","plot_data_04_loc_dh.csv",
                 "plot_data_04_loc_h2.csv","plot_data_04_loc_build.csv"]
        df_inv = [pd.read_csv(f'{appdir}/data/'+ f) for f in files]
        # df_cost = pd.read_csv(f'{appdir}/data/plot_data_03.csv')
        df_hcost = pd.read_csv(f'{appdir}/data/plot_data_11n.csv')
        
        # normalize with GB average (except GB values)
        
        # df_hcost[~df_hcost.index.get_level_values("REGION")
        #          .str.startswith("GB")] = (df_hcost[~df_hcost
        #                                             .index.get_level_values("REGION")
        #                                             .str.startswith("GB")]
        #                                             /df_hcost.xs((scenarios[0],
        #                                                           "GB"),
        #                                                          level=(0,1)))
        # df_hcost_gb = df_hcost.xs("GB",level=1)
        # df_hcost_gb = df_hcost_gb/df_hcost_gb.xs((scenarios[0],2015),level=(0,1)).squeeze()
        # df_hcost_gb = df_hcost_gb.reset_index()
        # df_hcost = df_hcost.reset_index()

                                            
                                                                                 
           
        graph1 = Barchart.ScenCompInvBarchart(
                id = "heat_inv_comp",
                df_inv = df_inv,
                title = None,
                y_label= "Investments (million GBP)",
                scenarios = scenarios,
                lads = lads,
                naming = scen_naming)
        
                                            
        graph2 = Linechart.GenericLinechart(
                id = 'hcost_path',
                df = df_hcost,
                title=None,
                x="YEAR",
                y="VALUE",
                category="RUN",
                scenarios = scenarios,
                lads = lads,
                naming=scen_naming,
                x_label = "Year",
                y_label = "Annual heating cost per property (GBP)",
                l_label = None                           
                )     
        

        

        glist = [dbc.Row([
                        dbc.Col([dbc.Stack([html.Div([f"Average annual investment requirements"],
                                                     className='figure_title'),
                                            invreq_popover],
                                          direction="horizontal"),
                                 graph1]),
                        dbc.Col([dbc.Stack([html.Div([f"Heating cost per property (flat)"],
                                                     className='figure_title'),
                                            heatcost_popover],
                                          direction="horizontal"),
                                 graph2]),
                    ], className='figure_row'),
                ]
        
    elif tab == 'tab-2' and subtab_2 == 'subtab-2-3':
        
        # - Create popover for graph titles
        
        content_empath_tooltip = ("This graph shows CO2 emissions from the"
                                  " energy system (with regard to the building"
                                  " sector).")

        empath_popover = hover_popover_object.create('t3-3_empath_popover', content_empath_tooltip,'popover_figure')

        
        df_em = pd.read_csv(f'{appdir}/data/plot_data_10_loc.csv')
        

    
        graph1 = Linechart.GenericLinechart(
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
            
        glist = [dbc.Row([
                            dbc.Col([dbc.Stack([html.Div([f"Energy-related CO2 emissions"],
                                                         className='figure_title'),
                                                empath_popover],
                                              direction="horizontal"),
                                     graph1]),
                            dbc.Col([]),
                        ], className='figure_row'),
                 
                ]
        # html.Div([graph1, graph2, graph5],
        #                  style={'display': 'flex', 'flexDirection': 'row'})]
        
        
    elif tab == 'tab-3':
       
        glist = [("Information on everything to go here."
                 "The dashboard source code is Copyright (C) 2024 Leonhard Hofbauer, Yueh-Chin Lin, licensed under a MIT license and available here.")]
    
    
    # options = [{'label':"Graph 1",
    #             'value':"g1"
    #             }]
    # download =  dcc.Dropdown(options, value="",
    #              id = 'download_dropdown',
    #              clearable = True,
    #              placeholder = "Download graph data"),


    return dbc.Container(glist,#+[download],
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
    
    fig = Hexmap.GenericHexmap(
            id = "heat_generation_map",
            df = df_gen_loc,
            title = None,
            zlabel = "Fraction<br>supplied by<br>technology (-)",
            techs = ["Air-source HP", "Heat interface unit",
              "Electric resistance heater","Biomass boiler",
              "H2 boiler"],
            year = year,
            scenarios = scenarios,
            naming=scen_naming,
            range_color=[0,1],
            figonly=True)

    return fig



# @callback(
#     Output("download_data", "data"),
#     Input("download_dropdown", "value"),
#     prevent_initial_call=True,
# )
# def download(value):
    
#     return dcc.send_data_frame(df.to_csv, "data.csv")



if __name__ == '__main__':
    app.run_server(host='127.0.0.1', port='8050')