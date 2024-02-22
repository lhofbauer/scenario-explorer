from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import json

# STYLE
style_active_tab = {"border":"0px", "background-color":"#f0f0f0"}
style_static_tab = {"border":"0px"}
style_active_label = {'background-color':"#fff",'font-weight':"700",'color':'#66c2a5'}
style_static_label = {'font-weight':'400', 'color':'#A5A5A5'}

# CONTENT

# COMPONENT
# - DEFINE FILTER FOR REGIONS
# -- Define the areas and fetch the name
areasfile = "./data/areas_codes_names.json"
with open(areasfile, 'r', encoding = 'utf-8') as json_file:
    data = json.load(json_file)

# -- Extract the list of areas' names
areas_list = [name for code, name in data.items()]
area_dropdown =  html.Div([ 
                    html.Div('Areas', className = 'facet_name', style = {'margin-right':'20px',
                                                                         'margin-top':'5px'}),
                    dcc.Dropdown(areas_list, areas_list[0], id = 'area_dropdown', 
                                 style = {'width':'300px'}),
                    ], style = {'display':'flex', 
                                'position':'absolute',
                                'width':'300px',
                                'margin-top':'10px',
                                'z-index':'1'})

# LAYOUT
def tabs(figures : list):
    return html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label = "Heat Generation", 
                        tab_id = "tab-1",
                        active_tab_style = style_active_tab,
                        active_label_style = style_active_label,
                        label_style = style_static_label),
                dbc.Tab(label = "Cost and Investment", 
                        tab_id = "tab-2", 
                        active_tab_style = style_active_tab,
                        active_label_style = style_active_label,
                        label_style = style_static_label),
                dbc.Tab(label = "Heat Generation (Regions)", 
                        tab_id = "tab-3", 
                        active_tab_style = style_active_tab,
                        active_label_style = style_active_label,
                        label_style = style_static_label),
            ],
            id="tabs",
            active_tab="tab-1",
        ),
        html.Div(area_dropdown, id = 'dropdown_component'),
        html.Div(figures, id = "figure-area"),
    ], 
    id = 'tab-area', style = {'width':'155vh', 'position':'absolute',
                              'top':'3rem', 'left':'23%'}
)