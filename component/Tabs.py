from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc
import json

# STYLE 
# (ONLY ATTRIBUTES WHICH CANNOT BE DEFINED IN CSS FILE)
style_active_label = {'background-color':"#fff",
                      'font-weight':"700",
                      'color':'#66c2a5'}

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
                    html.Div('Areas', id = 'area_label', className = 'facet_name',),
                    dcc.Dropdown(areas_list, areas_list[0], id = 'area_dropdown'),
                    ], id = 'dropdown_frame')

# LAYOUT
def tabs(figures : list):
    return html.Div(
    [
        dbc.Tabs(
            [
                dbc.Tab(label = "Heat Generation", 
                        tab_id = "tab-1",    
                        tab_class_name = 'tab',                
                        label_class_name = 'tab_label',
                        active_label_style = style_active_label
                        ),
                dbc.Tab(label = "Cost and Investment", 
                        tab_id = "tab-2", 
                        tab_class_name = 'tab',
                        label_class_name = 'tab_label',
                        active_label_style = style_active_label         
                        ),
                dbc.Tab(label = "Heat Generation (Regions)", 
                        tab_id = "tab-3",     
                        tab_class_name = 'tab',     
                        label_class_name = 'tab_label',
                        active_label_style = style_active_label
                        ),
            ],
            id="tabs",
            active_tab="tab-1",
        ),
        html.Div(area_dropdown, id = 'dropdown_component'),
        html.Div(figures, id = "figure-area"),
    ], 
    id = 'tab_area'
)