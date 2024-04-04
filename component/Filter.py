from dash import html, dcc
from component.Sidebar import Popover
import dash_bootstrap_components as dbc
import json
from pathlib import Path

# Get the absolute path of the parent directory containing the current script
appdir = str(Path(__file__).parent.parent.resolve())

with open(f'{appdir}/content/figures.json') as file:
    content = json.load(file)

class Filter:
    @staticmethod
    def Dropdown(options, id, default_option = None, clearable = False, className = None,
                 multiple = False, placeholder = None,
                 option_style = {'color': '#808080', 'font-size': '14px'}):
        
        dropdown_options = [{'label':html.Span(d['label'], style = option_style),
                             'value':d['value']}  for d in options]
        default_option = dropdown_options[0]['value'] if default_option == None else default_option
        dropdown = dcc.Dropdown(dropdown_options, default_option,
                                id = id, className = className, 
                                clearable = clearable, multi = multiple, 
                                placeholder = placeholder)
        return dropdown
    
    @staticmethod
    def YearSlider(min, max, step, id, default_value = None, tooltip = None, className = None):
        marks = {y:str(y) for y in range(min, max + 1, step)}
        default_value = min if default_value == None else default_value
        popover = Popover.hover('{}_popover'.format(id), tooltip) if tooltip else None
        yslider = html.Div([   
                    html.Div(['Year', popover], className = 'facet_item_name'),
                    dcc.Slider(min = min, max = max, step = step, marks = marks,
                               value = default_value, id = id, className = className)])
        return yslider