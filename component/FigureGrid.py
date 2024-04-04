from dash import html, dcc
import dash_bootstrap_components as dbc
from component.Sidebar import Popover

class FigureGrid:
  @staticmethod
  def create(figures:list[dict], columns_per_row):
    figures = [
        dbc.Col([
        dbc.Stack(
            [html.Div(f['title'], className = 'figure_title'),
            Popover.hover(f['popover']['id'], 
                          f['popover']['tooltip'],
                          f['popover']['className'])               
          ], direction = 'horizontal'),
          f['facet'],
          dcc.Loading(f['graph']) if f['facet'] is not None else f['graph']],  
          className = 'figure_col')

        for f in figures]

    
    figure_count = 0
    columns_per_row = [int(i) for i in columns_per_row.split()]
    row_num = len(columns_per_row)
    grid_layout = html.Div(children = [])
    for i in range(row_num):
      grid_layout.children.append(dbc.Row(children = [], className = 'figure_row'))
      for j in range(columns_per_row[i]):
        grid_layout.children[i].children.append(figures[figure_count])
        figure_count += 1
  

    return grid_layout