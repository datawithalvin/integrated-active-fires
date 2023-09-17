import datetime
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from src.procedures import generate_density_map, fetch_last_data, generate_line_chart, generate_top_prov, generate_top_kabkot

from dotenv import dotenv_values

config = dotenv_values("./.env")
CONNECTION_URI = config.get("CONNECTION_URI")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.DARKLY], title="Indonesia Comprehensive Environmental Monitoring Dashboard")
server = app.server


query = f"""
    SELECT title, url, image, published_time
    FROM articles
    WHERE published_date = CURRENT_DATE
    LIMIT 15"""

articles = fetch_last_data(query=query, uri_connection=CONNECTION_URI)
articles = articles.to_pandas()

image = articles["image"][2]
title = articles["title"][2]

url = articles["url"][2]
publish = articles["published_time"][2]

card = dbc.Card(
    [
        dbc.Row(
            [
                dbc.Col(
                    dbc.CardImg(
                        src=image,
                        className="img-fluid rounded-start",
                    ),
                    className="col-md-3",
                ),
                dbc.Col(
                    dbc.CardBody(
                        [
                            html.H4(f"{title}", className="card-title"),
                            html.Small(
                                f"Published date: {publish}",
                                className="card-text text-muted",
                            ),
                        ]
                    ),
                    className="col-md-9",
                ),
            ],
            className="g-0 d-flex align-items-center",
        )
    ],
    className="mb-3",
    style={"maxWidth": "540px"},
    color="warning",
    outline=True
)

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


app.layout = dbc.Container([
    dbc.Row([
        dcc.Interval(
            id='interval-component',
            interval=60*1000, # in milliseconds, set to 1 minute
            n_intervals=0
    ),
    html.Div(id='live-update-text', style={'display': 'inline-block', 'margin-left': '20px', 'margin-top': '10px'}),
    ]),


    # dcc.Interval(
    #         id='interval-component',
    #         interval=60*1000, # in milliseconds, set to 1 minute
    #         n_intervals=0
    # ),
    # html.Div(id='live-update-text', style={'display': 'inline-block', 'margin-left': '20px', 'margin-top': '10px'}),


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
                            {"label": "1 Hari Terakhir", "value": 2},
                            {"label": "7 Hari Terakhir", "value": 7},
                            {"label": "15 Hari Terakhir", "value": 15},
                            {"label": "30 Hari Terakhir", "value": 30},
                        ],
                        value=2, #default value
                        clearable=False,
                        optionHeight=20,
                    )
                ], width=2)
            ]),
            dcc.Loading(
                id="loading",
                type="cube",
                fullscreen=True,
                children=[dcc.Graph(id="density-map", figure={}, style={"height": "50vh"})])
        ], width=6),

        # ----- Related Articles Place Holder -----
        dbc.Col(card, width=3),

        # ----- Air Quality Place Holder -----
        dbc.Col([dcc.Graph(id='aqi-nrt', figure={}, style={"height": "60vh"})], width=3),

    ]),

    # ----------------------------- Second Row Viz Section ------------------------------
    dbc.Row([
        # ----- Line Chart Place Holder -----
        # dbc.Col([dcc.Graph(id='line-chart-viirs', figure={})], width=4),
        dbc.Col([
            # dbc.Row([
            #     dbc.Col([
            #         dcc.Dropdown(
            #             id="filter-3",
            #             options=[
            #                 {"label": "Tingkat Nasional", "value": "Tingkat Nasional"},
            #                 {"label": "Provinsi A", "value": "Provinsi A"}
            #             ],
            #             value="Tingkat Nasional", #default value
            #             clearable=False,
            #             optionHeight=20
            #         )
            #     ], width=4)
            # ]), 
            dcc.Graph(id="line-chart-viirs", figure={}, style={"height": "30vh"})
        ], width=4),

        # ----- Bar Chart Place Holder -----
        dbc.Col([dcc.Graph(id='top-province', figure={}, style={"height": "30vh"})], width=3),

        # ----- Related Socmed Post Place Holder -----
        dbc.Col([dcc.Graph(id='top-kabkot', figure={}, style={"height": "30vh"})], width=3),

        # ----- Summary Place Holder -----
        dbc.Col(carousel, width=2),

        # stores the result data
        dcc.Store(id='result-data')
    ]),
], 
fluid=True
)


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
    Output("result-data", "data"),
    Input("filter-time-period", "value")
)
def update_density_map(filter_time_period):
    fig, data = generate_density_map(n_day=filter_time_period, uri_connection=CONNECTION_URI)

    return fig, data


# ----- Callback line chart -----
@app.callback(
    Output("line-chart-viirs", "figure"),
    Input("result-data", "data")

)
def update_line_chart(jsonified_data):
    fig = generate_line_chart(jsonified_data)
    return fig


# ----- Callback bar chart -----
@app.callback(
    Output("top-province", "figure"),
    Input("result-data", "data")

)
def update_bar_chart(jsonified_data):
    fig = generate_top_prov(jsonified_data)
    return fig



# ----- Callback bar chart kabkot-----
@app.callback(
    Output("top-kabkot", "figure"),
    Input("result-data", "data")

)
def update_bar_chart(jsonified_data):
    fig = generate_top_kabkot(jsonified_data)
    return fig



if __name__ == '__main__':
    app.run_server(debug=True)