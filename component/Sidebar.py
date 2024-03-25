from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path

appdir = str(Path(__file__).parent.parent.resolve())

#CONTENT
content_title = 'Scenarios toolbar'
content_description = 'Create and choose scenarios to display below.'
content_facet_1 = 'Choose Scenarios to display'
dropdown_description = 'Choose a pre-defined scenario as starting point.'
levers_description = 'Adjust the scenario by moving the scenario levers.'
content_facet_2 = 'Customize Scenarios'
content_lev_1 = 'Net-zero Target'
content_lev_1_tooltip = 'This lever sets the year net-zero emissions are to be achieved in the UK.'
content_lev_2 = 'Heat Pump Rollout'
content_lev_2_tooltip = ('This lever customizes the rollout of domestic heat pumps.'
                         ' The "Fast" option assumes a roll out'
                         ' following government targets. The "Limited"'
                         ' option assumes a limit of 150k installations per year'
                         'in 2030 and 400k in 2060.')
content_lev_3 = 'District Heating'
content_lev_3_tooltip = ('This lever customizes the rollout of district heating networks.'
                         ' The "Cost-optimal" option assumes district heating is built'
                         ' where cost-optimal. The "Limited"'
                         ' option assumes a no additional district heating'
                         ' networks are built in future.')
content_lev_4 = 'Hydrogen'
content_lev_4_tooltip = ('This lever customizes the potential use of hydrogen'
                         ' for heating. The "Cost-optimal" option assumes'
                         ' hydrogen is only used where cost-optimal. The'
                         ' "Forced" option assumes 10% and 20% of demand is met by'
                         ' hydrogen boilers by 2040 and 2050, respectively.')
content_lev_5 = 'Local pledges'
content_lev_5_tooltip = ("This lever customizes to what extent local authorities' net-zero"
                         ' pledges are achieved. The "Not implemented" option assumes'
                         ' pledges are not specifically followed if not aligned'
                         ' with the national target. The "Implemented"'
                         ' option assumes the net-zero target years based'
                         ' on local authority pledges are achieved.')

#POPOVER FOR LEVERS

class Popover():
    def __init__(self, trigger):
        self.trigger = trigger
    
    def create(self, popover_id, content, className):
        self.children = content

        return html.Div (
            [
                html.Img(
                    src = '../assets/icons/question_popover.png',
                    className = className, id = popover_id),
                dbc.Popover(
                    content, 
                    target = popover_id, 
                    body = True, 
                    trigger = self.trigger)
        ])
    
# - Create popover for levers
hover_popover_object = Popover('hover')
lever1_popover = hover_popover_object.create('lever1_popover', content_lev_1_tooltip,'popover_lever')
lever2_popover = hover_popover_object.create('lever2_popover', content_lev_2_tooltip,'popover_lever')
lever3_popover = hover_popover_object.create('lever3_popover', content_lev_3_tooltip,'popover_lever')
lever4_popover = hover_popover_object.create('lever4_popover', content_lev_4_tooltip,'popover_lever')
lever5_popover = hover_popover_object.create('lever5_popover', content_lev_5_tooltip,'popover_lever')

#EXTRACT SCENARIOS AND LEVERS

# FIXME: define these scenarios in a data file and load from the file
predef_scenarios = [{'label': 'Base net-zero scenario',
                     'value':'nz-2050_hp-00_dh-00_lp-00_h2-00_UK|LA|SO'},
                    {'label': 'High ambition scenario',
                     'value':'nz-2045_hp-00_dh-00_lp-01_h2-00_UK|LA|SO'}]
# create list of dropdown options including style
options = [{'label':html.Span(d['label'], style={'color': '#808080',
                                          'font-size': '14px'}),
            'value':d['value']
            } for d in predef_scenarios]

# FIXME: test levers, to be updated and probably loaded from file
lev1 = {2045:"2045",
        2050:"2050"}
lev2 = {0:"Fast",
        1:"Limited"}
lev3 = {0:"Cost-optimal",
        1:"Limited"}
lev4 = {0:"Cost-optimal",
        1:"Enforced"}
lev5 = {0:"Not implemented",
        1:"Implemented"}

#LAYOUT
def sidebar():
    return html.Div(
       [
            html.Div(content_title, className ='sidebar_title'),
            html.Hr(),
            html.P(content_description, className = 'sidebar_description'),
            html.Br(),
            html.Div(content_facet_1, className = 'facet_name'),
            dcc.Dropdown(options, predef_scenarios[0]['value'],
                         id = 'chosen_scenario_dropdown',
                         multi = True,
                         clearable = False,
                         placeholder = "Select at least one."),
            html.Br(),
            html.Div(content_facet_2, className = 'facet_name'),
            html.Div(dropdown_description, className = 'sidebar_description'),
            dcc.Dropdown(options, predef_scenarios[0]['value'],
                         id = 'scenario_dropdown',
                         clearable = False,
                         placeholder = "No scenario chosen."),
            html.Div(levers_description, className = 'sidebar_description'),
            html.Br(),
            html.Div([content_lev_1,lever1_popover], className = 'facet_item_name'),
            dcc.Slider(min = 2045, max = 2050, step = None, marks = lev1,
                       value = 2050,
                       id= 'nz_slider', className = 'slider'),
            html.Div([content_lev_2, lever2_popover], className = 'facet_item_name'),
            dcc.Slider(min = 0, max = 1, step = None, marks = lev2, value = 0,
                       id= 'hp_slider', className = 'slider'),
            html.Div([content_lev_3,lever3_popover], className = 'facet_item_name'),
            dcc.Slider(min = 0, max = 1, step = None, marks = lev3,
                       value = 0,
                       id= 'dh_slider', className = 'slider'),
            html.Div([content_lev_4,lever4_popover], className = 'facet_item_name'),
            dcc.Slider(min = 0, max = 1, step = None, marks = lev4,
                       value = 0,
                       id= 'h2_slider', className = 'slider'),
            html.Div([content_lev_5, lever5_popover], className = 'facet_item_name'),
            dcc.Slider(min = 0, max = 1, step = None, marks = lev5, value = 0,
                       id= 'lp_slider', className = 'slider'),            
            html.Br(),
            dcc.Input(id='scenario_name_field', type='text', value='',
                      placeholder = 'Scenario name'),
            html.Div([html.Div('', id = 'scenario_creation_response'),
                      html.Button(id = 'submit_button', n_clicks = 0,
                                  children = 'Create')],
                                  style = {'display':'flex', 
                                           'flex-direction': 'column',
                                           'align-items':'center',
                                           'padding-left':'10px'})

            # dcc.Slider(min=2040, max=2050, step=None,marks=lev1,value=2050,
            #            tooltip={'template':'Net-zero target for the UK to be achieved in {value}.',
            #                     'placement':'bottom'}),
            #dbc.Nav([#dbc.NavLink("Home", href="/", active="exact"),],vertical=True,pills=True,),
        ], 
        id = 'sidebar'
    )

