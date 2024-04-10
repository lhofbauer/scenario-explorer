import dash_bootstrap_components as dbc
from dash import html

# LAYOUT
# - The default modal content calssName is 'modal-content'
def Modal():
    return  html.Div(
        [
            dbc.Modal(
                [
                dbc.ModalHeader(
                    dbc.ModalTitle("Energy Transition Scenario Explorer Tutorial",
                    id = 'modal_title'),),
                    dbc.ModalBody(dbc.Carousel(
                        items=[
                            {"key": "1", "src": "../assets/images/Tutorial1.jpg"},
                            {"key": "2", "src": "../assets/images/Tutorial2.jpg"},
                            {"key": "3", "src": "../assets/images/Tutorial3.jpg"},
                            {"key": "4", "src": "../assets/images/Tutorial4.jpg"},
                        ],
                controls = True,
                indicators = True,
                variant = 'dark'
            )),
                dbc.ModalFooter(
                    dbc.Button(
                        "Close",
                        id="close_modal",
                        n_clicks=0,
                    )
                ),
                ],
                id="tutorial_modal",
                scrollable = True,
                is_open = True,
                size = 'xl'
            ),
        ]
    )

    