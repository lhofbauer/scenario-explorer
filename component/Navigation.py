from dash import html
import dash_bootstrap_components as dbc

# CONTENT
headbar_title = 'ENERGY TRANSITION SCENARIO EXPLORER [ALPHA VERSION]'
headbar_subtitle = ''#'Explore heat decarbonization scenarios for Great Britain'
headbar_warning = "THE DASHBOARD IS CURRENTLY BEING UPDATED WITH A NEW VERSION EXPECTED IN SEPTEMBER 2025"
footer_content = [
                  # html.A(['Developed at UCL'], href = 'https://www.ucl.ac.uk/bartlett/environment-energy-resources/bartlett-school-environment-energy-and-resources',
                  #        target="_blank",
                  #        className = 'navlink'),
                  # '|',
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

class Navigation:
       @staticmethod
       def HeadBar():
              headbar = html.Div([
                     html.Div([headbar_title], className = "title"),
                     html.Div([headbar_subtitle], className = "subtitle"),
                     html.Div([headbar_warning], className = "warning")
                     ],
                     id = 'navbar'
                     )
              return headbar
       
       @staticmethod
       def Footer():
              footer = html.Footer(footer_content,
                                   id = 'footer', className = "footer_text")
              return footer