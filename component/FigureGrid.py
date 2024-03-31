from dash import Dash, html, dcc, callback, Output, Input, State
import dash_bootstrap_components as dbc
from component.Sidebar import Popover

class FigureGrid:
  @staticmethod
  def create(figures:list[dict]):
    figures = [
          html.Div([
          dbc.Stack(
              [html.Div(f['title'], className = 'figure_title'),
              Popover.hover(f['popover']['id'], 
                            f['popover']['tooltip'],
                            f['popover']['className'])               
            ], direction = 'horizontal'),
            f['graph']], style = {'display':'flex',
                                'flex-direction':'column',
                                'align-items':'flex-start'})
          for f in figures]
    
    grids = html.Div(figures,
                      style = {'display':'grid',
                              'grid-template-columns':'1fr 1 fr'})

    return grids