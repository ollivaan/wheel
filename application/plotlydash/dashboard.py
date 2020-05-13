import sys
sys.path.append("..")
import dash
import dash_table
import dash_html_components as html
import dash_core_components as dcc
import plotly.graph_objects as go
import pandas as pd
import numpy as np

from .layout import html_layout
from .sunburst_settings import sundata




def create_dashboard(server):
    """Initializes and creates the dash app for plotly"""
    dash_app = dash.Dash(server=server,
                         routes_pathname_prefix='/sustainability_wheel/',
                         external_stylesheets=['/static/dist/css/styles.css','https://fonts.googleapis.com/css?family=Lato']
                         )

    fig = sundata()
    dash_app.index_string = html_layout

    dash_app.layout = html.Div(
        children=[dcc.Graph(figure=fig),
            ],
        id='dash-container'
    )

    return dash_app.server


