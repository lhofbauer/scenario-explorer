from dash import html


#CONTENT
navbar_title = 'ENERGY TRANSITION SCENARIO EXPLORER'
footer_content = 'Copyright (C) 2024 Leonhard Hofbauer, Yueh-Chin Lin, licensed under a MIT license'


def createNavbar():
        navbar = html.Div([
                html.Div([navbar_title], className = "title"),
                html.A(['Git Repo'], href = 'https://www.example.com', className = 'navlink')
                ],
                id = 'navbar'
                )
        return navbar

def createFooter():
        footer = html.Footer([footer_content], id = 'footer', className = "footer_text")
        return footer