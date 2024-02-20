from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

# STYLE
style_active_tab = {"border":"0px", "background-color":"#f0f0f0"}
style_static_tab = {"border":"0px"}
style_active_label = {'background-color':"#fff",'font-weight':"700",'color':'#66c2a5'}
style_static_label = {'font-weight':'400', 'color':'#A5A5A5'}

# CONTENT

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
        html.Div(figures, id="figure-area"),
    ], 
    id = 'tab-area'
)