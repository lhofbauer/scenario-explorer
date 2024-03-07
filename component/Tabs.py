from dash import html, dcc
import json
from pathlib import Path
import dash_bootstrap_components as dbc

appdir = str(Path(__file__).parent.parent.resolve())

# STYLE 
# (ONLY ATTRIBUTES WHICH CANNOT BE DEFINED IN CSS FILE)

# CONTENT

# COMPONENT
# - DEFINE FILTER FOR REGIONS
# -- Define the areas and fetch the name
areasfile = f'{appdir}/data/areas_codes_names.json'
with open(areasfile, 'r', encoding = 'utf-8') as json_file:
    data = json.load(json_file)

# -- Extract the list of areas' names
areas_list = [name for code, name in data.items()]
area_dropdown =  html.Div([ 
                    html.Div('Areas', id = 'area_label', className = 'facet_name',),
                    dcc.Dropdown(areas_list, areas_list[0], id = 'area_dropdown',
                                 clearable = False),
                    ], id = 'dropdown_frame')

# -- Pack the dropdown area
dropdown_component = html.Div(area_dropdown, id = 'dropdown_component')


# - SUBTABS
# -- Subtabs for tab-1
subtabs_1 = html.Div ([
    dcc.Tabs([
        dcc.Tab(label = "Technology Mix", 
                        id = 'subtab-1-1',
                        value = "subtab-1-1",
                        className = 'custom-subtab_1_1',
                        selected_className = 'custom-subtab_1_1-selected'
                        ),
        dcc.Tab(label = "Cost & Investment", 
                        id = 'subtab-1-2',
                        value = "subtab-1-2",
                        className = 'custom-subtab_1_2',
                        selected_className = 'custom-subtab_1_2-selected'
                        ),
        dcc.Tab(label = "Emissions", 
                        id = 'subtab-1-3',
                        value = "subtab-1-3",
                        className = 'custom-subtab_1_3',
                        selected_className = 'custom-subtab_1_3-selected'
                        ),
    ], id = 'subtabs_1', value = 'subtab-1-1')
])


# -- Search bar for local authorities filter embeded in Subtabs for tab-2
button =  dbc.Button(
            "Select Local Authorities",
            id = "local_auth_search_button",
            n_clicks = 0,
        )

local_auth_search =  dcc.Dropdown(['example1', 'example2'], 'example1',
                         id = 'local_auth_search',
                         clearable = False,
                         searchable = True,
                         multi = True,
                         placeholder = "Choose at least one")

local_auth_search_collapse = dbc.Collapse(
                            local_auth_search,
                            id = "local_auth_search_collapse",
                            is_open = False,)

local_auth_search_component = html.Div([button, local_auth_search_collapse],
                                       id = 'local_auth_search_component')


# -- Subtabs for tab-2
subtabs_2 = html.Div ([
    dcc.Tabs([
        dcc.Tab(label = "Technology Mix", 
                        id = 'subtab-2-1',
                        value = "subtab-2-1",
                        className = 'custom-subtab_2_1',
                        selected_className = 'custom-subtab_2_1-selected'
                        ),
        dcc.Tab(label = "Cost & Investment", 
                        id = 'subtab-2-2',
                        value = "subtab-2-2",
                        className = 'custom-subtab_2_2',
                        selected_className = 'custom-subtab_2_2-selected'
                        ),
        dcc.Tab(label = "Emissions", 
                        id = 'subtab-2-3',
                        value = "subtab-2-3",
                        className = 'custom-subtab_2_3',
                        selected_className = 'custom-subtab_2_3-selected'
                        ),
    ], id = 'subtabs_2', value = 'subtab-2-1'),
        local_auth_search_component
                        ], 
        id = 'subtabs_2_plus_search_component')


# LAYOUT
def tabs(figures : list):
    return html.Div(
    [
        dcc.Tabs(
            [
                dcc.Tab([subtabs_1],
                        label = "National View", 
                        id = 'tab-1',
                        value = "tab-1",
                        className = 'custom-tab_1',
                        selected_className = 'custom-tab_1-selected'
                        ),
                dcc.Tab([subtabs_2],
                        label = "Local View", 
                        id = 'tab-2',
                        value = "tab-2",     
                        className = 'custom-tab_2',
                        selected_className = 'custom-tab_2-selected'   
                        ),
                dcc.Tab(label = "Help", 
                        id = 'tab-3',
                        value = "tab-3",  
                        className = 'custom-tab_3',
                        selected_className = 'custom-tab_3-selected'      
                        ),
            ],
            id="tabs",
            value="tab-1",
        ),
        #html.Div(area_dropdown, id = 'dropdown_component'),
        html.Div([figures], id = "figure-area"),
    ], 
    id = 'tab_area'
)