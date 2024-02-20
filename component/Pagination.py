from dash import Dash, html, dcc, callback, Output, Input
import dash_bootstrap_components as dbc

# STYLE

# CONTENT

# LAYOUT
def page_RH(id = '', page = 1):
    return html.Div(
    [
        dbc.Pagination(
            id = id,
            max_value = 0,
            active_page = page,
            previous_next = True,
            first_last = True,
            fully_expanded = False,  
            style = {'display':'none'}    
        ),
            ],
        
    )