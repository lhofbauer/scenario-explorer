from dash import html


#CONTENT
navbar_title = 'ENERGY TRANSITION SCENARIO EXPLORER'
footer_content = 'Developed at UCL funded by EPSRC (EP/X525649/1)| [...]'


def createNavbar():
        navbar = html.Div([
                html.Div([navbar_title], className = "title"),
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