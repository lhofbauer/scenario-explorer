from dash import html
import dash_bootstrap_components as dbc

#CONTENT
navbar_title = 'ENERGY TRANSITION SCENARIO EXPLORER'
navbar_subtitle = ''#'Explore heat decarbonization scenarios for Great Britain'
footer_content = 'Developed at UCL funded by EPSRC (EP/X525649/1)| [...]'


def createNavbar():
        navbar = html.Div([
                html.Div([navbar_title], className = "title"),
                html.Div([navbar_subtitle], className = "subtitle")
                ],
                id = 'navbar'
                )
        return navbar

def createFooter():
        footer = html.Footer([footer_content,
                              html.A(['Git Repo'], href = 'https://www.example.com', className = 'navlink')
                              ],
                             id = 'footer', className = "footer_text")
        return footer