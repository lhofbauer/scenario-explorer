from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import pandas as pd


#CONTENT
content_title = 'ENERGY TRANSITION'
content_description = 'The graphs show the national progress of energy transition in the UK'
content_facet_1 = 'Create Scenarios'
dropdown_description = 'Choose a pre-defined or default scenario as starting point.'
levers_description = 'Adjust the scenario by moving the scenario levers.'
content_facet_2 = 'Choose Scenarios to display'
content_lev_1 = 'Net-zero Target'
content_lev_1_tooltip = 'This lever sets the year net-zero emissions are to be achieved in the UK.'
content_lev_2 = 'Heat Pump Rollout'
content_lev_2_tooltip = 'This lever contraints the rollout of heat pumps. [...]'


#EXTRACT SCENARIOS AND LEVERS

# FIXME: define these scenarios in a data file and load from the file
predef_scenarios = [{'label': 'Base net-zero scenario',
                     'value':'nz-2050_hp-00'},
                    {'label': 'High ambition scenario',
                     'value':'nz-2040_hp-01'}]
# create list of dropdown options including style
options = [{'label':html.Span(d['label'], style={'color': '#808080',
                                          'font-size': '14px'}),
            'value':d['value']
            } for d in predef_scenarios]
    
# FIXME: test levers, to be updated and probably loaded from file
lev1 = {2040:"2040",
        2045:"2045",
        2050:"2050"}
lev2 = {0:"No limitation",
        1:"Constraint"}

#LAYOUT
def sidebar():
    return html.Div(
       [
            #html.Div(content_title, className ='sidebar_title'),
            #html.Hr(),
            html.P(content_description, className = 'sidebar_description'),
            html.Br(),
            html.Div(content_facet_1, className = 'facet_name'),
            html.Div(dropdown_description, className = 'sidebar_description'),
            dcc.Dropdown(options, predef_scenarios[0]['value'],
                         id = 'scenario_dropdown',
                         clearable = False,
                         placeholder = "No scenario chosen."),
            html.Div(levers_description, className = 'sidebar_description'),
            html.Div(content_lev_1, className = 'facet_item_name',
                     title = content_lev_1_tooltip),
            dcc.Slider(min = 2040, max = 2050, step = None, marks = lev1,
                       value = 2050,
                       id= 'nz_slider', className = 'slider'),
            html.Div(content_lev_2, className = 'facet_item_name',
                     title = content_lev_2_tooltip),
            dcc.Slider(min = 0, max = 1, step = None, marks = lev2, value = 0,
                       id= 'hp_slider', className = 'slider'),
            html.Br(),
            dcc.Input(id='scenario_name_field', type='text', value='',
                      placeholder = 'Scenario name'),
            html.Button(id = 'submit_button', n_clicks = 0,
                        children='Create'),
            html.Div(content_facet_2, className = 'facet_name'),
            dcc.Dropdown(options, predef_scenarios[0]['value'],
                         id = 'chosen_scenario_dropdown',
                         clearable = True,
                         multi=True,
                         placeholder = "No scenario chosen."),
            # dcc.Slider(min=2040, max=2050, step=None,marks=lev1,value=2050,
            #            tooltip={'template':'Net-zero target for the UK to be achieved in {value}.',
            #                     'placement':'bottom'}),
            #dbc.Nav([#dbc.NavLink("Home", href="/", active="exact"),],vertical=True,pills=True,),
        ], 
        id = 'sidebar'
    )

