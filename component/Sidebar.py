from dash import html, dcc
import dash_bootstrap_components as dbc
import pandas as pd
from pathlib import Path
import json
import re

appdir = str(Path(__file__).parent.parent.resolve())

# CONTENT
with open(f'{appdir}/content/sidebar.json') as file:
    content = json.load(file)

#POPOVER FOR LEVERS
class Popover():
    @staticmethod    
    def hover(popover_id, content, className = 'popover_lever'):
        return html.Div (
            [
                html.Img(
                    src = '../assets/icons/question_popover.png',
                    className = 'popover_lever', id = popover_id),
                dbc.Popover(
                    content, 
                    target = popover_id, 
                    body = True, 
                    trigger = 'hover')
])
    
# - Create popover for levers
lever_num = len([i for i in content.keys() if re.match(r'^lev_\d+$', i)]) + 1
lever_popovers = [Popover.hover(f'lever{i}_popover', 
                                content[f'lev_{i}_tooltip']) for i in range(1, lever_num)]

# EXTRACT SCENARIOS AND LEVERS
predef_scenarios = content['predefined_scenarios']

# create list of dropdown options including style
options = [{'label':html.Span(d['label'], 
                              style={'color': '#808080',
                                     'font-size': '14px'}),
                                'value':d['value']
                                } for d in predef_scenarios]

#LAYOUT
def sidebar():
    return html.Div(
       [
            html.Div(content['title'], className ='sidebar_title'),
            html.Hr(),
            html.P(content['description'], className = 'sidebar_description'),
            html.Br(),
            html.Div(content['facet_1'], className = 'facet_name'),
            dcc.Dropdown(options, predef_scenarios[0]['value'],
                         id = 'chosen_scenario_dropdown',
                         multi = True,
                         clearable = False,
                         placeholder = "Select at least one"),
            html.Div('', id = 'scenario_chosen_response'),
            html.Br(),
            html.Div(content['facet_2'], className = 'facet_name'),
            html.Div(content['dropdown_description'], className = 'sidebar_description'),
            dcc.Dropdown(options, predef_scenarios[0]['value'],
                         id = 'scenario_dropdown',
                         clearable = False,
                         placeholder = "No scenario chosen."),
            html.Div(content['levers_description'], className = 'sidebar_description'),
            html.Br(),
            html.Div([content['lev_1'], lever_popovers[0]], className = 'facet_item_name'),
            dcc.Slider(min = 2045, max = 2050, step = None, marks = content['lev1'],
                       value = 2050,
                       id= 'nz_slider', className = 'slider'),
            html.Div([content['lev_2'], lever_popovers[1]], className = 'facet_item_name'),
            dcc.Slider(min = 0, max = 1, step = None, marks = content['lev2'], value = 0,
                       id= 'hp_slider', className = 'slider'),
            html.Div([content['lev_3'], lever_popovers[2]], className = 'facet_item_name'),
            dcc.Slider(min = 0, max = 1, step = None, marks = content['lev3'],
                       value = 0,
                       id= 'dh_slider', className = 'slider'),
            html.Div([content['lev_4'], lever_popovers[3]], className = 'facet_item_name'),
            dcc.Slider(min = 0, max = 1, step = None, marks = content['lev4'],
                       value = 0,
                       id= 'h2_slider', className = 'slider'),
            html.Div([content['lev_5'], lever_popovers[4]], className = 'facet_item_name'),
            dcc.Slider(min = 0, max = 1, step = None, marks = content['lev5'], value = 0,
                       id= 'lp_slider', className = 'slider'),            
            html.Br(),
            dcc.Input(id='scenario_name_field', type='text', value='',
                      placeholder = 'Scenario name'),
            html.Div([html.Div('', id = 'scenario_creation_response'),
                      html.Button(id = 'submit_button', n_clicks = 0,
                                  children = 'Create & Display')],
                                  style = {'display':'flex', 
                                           'flex-direction': 'column',
                                           'align-items':'center',
                                           'padding-left':'10px'})

                ], 
        id = 'sidebar'
    )

