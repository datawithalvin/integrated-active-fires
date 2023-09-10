import polars as pl
import pandas as pd
import geopandas as gpd
import datetime

import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff

from src.procedures import generate_density_map

from dotenv import dotenv_values

config = dotenv_values("./.env")
CONNECTION_URI = config.get("CONNECTION_URI")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SOLAR], title="Indonesia Comprehensive Environmental Monitoring Dashboard")
server = app.server

carousel = dbc.Carousel(
    items=[
        {"key": "1", "src": "https://www.nasa.gov/sites/default/files/thumbnails/image/nasa-logo-web-rgb.png"},
        {"key": "2", "src": "https://www.nasa.gov/sites/default/files/images/174116main_2006_01777_highres.jpg"},

    ],
    controls=False,
    indicators=False,
    interval=2000,
    ride="carousel",
)


app.layout = html.Div([
    dcc.Interval(
            id='interval-component',
            interval=60*1000, # in milliseconds, set to 1 minute
            n_intervals=0
    ),
    html.Div(id='live-update-text', style={'display': 'inline-block', 'margin-left': '20px', 'margin-top': '10px'}),


    # ----------------------------- First Row Viz Section ------------------------------
    dbc.Row([
        # ----- Scatter Map Place Holder -----
        # dbc.Col([dcc.Graph(id='scatter-map', figure={})], width=7),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id="filter-time-period",
                        options=[
                            {"label": "24 Jam Terakhir", "value": 2},
                            {"label": "7 Hari Terakhir", "value": 7},
                            {"label": "30 Hari Terakhir", "value": 30},
                            {"label": "90 Hari Terakhir", "value": 90}
                        ],
                        value=2, #default value
                        clearable=False,
                        optionHeight=20
                    )
                ], width=2)
            ]),
            dcc.Loading(
                id="loading",
                type="default",  # you can change this to "circle", "dot", or "cube" as per your preference
                children=[dcc.Graph(id="density-map", figure={})])
        ], width=7),

        # ----- Related Articles Place Holder -----
        dbc.Col([dcc.Graph(id='articles', figure={})], width=3),

        # ----- Air Quality Place Holder -----
        dbc.Col([dcc.Graph(id='aqi-nrt', figure={})], width=2),

    ]),

    # ----------------------------- Second Row Viz Section ------------------------------
    dbc.Row([
        # ----- Line Chart Place Holder -----
        # dbc.Col([dcc.Graph(id='line-chart-viirs', figure={})], width=4),
        dbc.Col([
            dbc.Row([
                dbc.Col([
                    dcc.Dropdown(
                        id="filter-3",
                        options=[
                            {"label": "Tingkat Nasional", "value": "Tingkat Nasional"},
                            {"label": "Provinsi A", "value": "Provinsi A"}
                        ],
                        value="Tingkat Nasional", #default value
                        clearable=False,
                        optionHeight=20
                    )
                ], width=4)
            ]),
            dcc.Graph(id="line-chart-viirs", figure={})
        ], width=4),

        # ----- Bar Chart Place Holder -----
        dbc.Col([dcc.Graph(id='top-province', figure={})], width=3),

        # ----- Related Socmed Post Place Holder -----
        dbc.Col([dcc.Graph(id='socmed-post', figure={})], width=3),

        # ----- Summary Place Holder -----
        dbc.Col(carousel, width=2),

    ]),
])


# ----------------------------- Dash App Callbacks -----------------------------

# ----- Callback for dates and times -----
@app.callback(Output('live-update-text', 'children'),
              [Input('interval-component', 'n_intervals')])
def update_date(n):
    # return datetime.datetime.now().strftime('%Y-%b-%d %H:%M')
    return datetime.datetime.now().strftime('%b %d, %Y | %H:%M')


# ----- Callback density map -----
@app.callback(
    Output("density-map", "figure"),
    Input("filter-time-period", "value")

)
def update_density_map(filter_time_period):
    fig = generate_density_map(n_day=filter_time_period, uri_connection=CONNECTION_URI)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)