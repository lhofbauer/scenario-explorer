from dash import html
import dash_bootstrap_components as dbc

#CONTENT
navbar_title = 'ENERGY TRANSITION SCENARIO EXPLORER [ALPHA VERSION]'
navbar_subtitle = ''#'Explore heat decarbonization scenarios for Great Britain'
footer_content = [
                  html.A(['Developed at UCL'], href = 'https://www.ucl.ac.uk/bartlett/environment-energy-resources/bartlett-school-environment-energy-and-resources',
                         target="_blank",
                         className = 'navlink'),
                  '|',
                  html.A(['Funded by EPSRC (EP/X525649/1)'], href = 'https://www.ukri.org/councils/epsrc/',
                         target="_blank",
                         className = 'navlink'),
                  '|',
                  html.A(['Source code on GitHub'], href = 'https://www.ukri.org/councils/epsrc/',
                         target="_blank",
                         className = 'navlink'),
                  '|',
                  html.A(['Get in touch'], href = 'mailto:leonhard.hofbauer.18@ucl.ac.uk',
                         target="_blank",
                         className = 'navlink'),
                  ]


def createNavbar():
        navbar = html.Div([
                html.Div([navbar_title], className = "title"),
                html.Div([navbar_subtitle], className = "subtitle")
                ],
                id = 'navbar'
                )
        return navbar

def createFooter():
        footer = html.Footer(footer_content,
                             id = 'footer', className = "footer_text")
        return footer