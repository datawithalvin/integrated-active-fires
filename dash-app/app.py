# Import Packages ------------------------------------------------------
import datetime
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from src.procedures import generate_density_map, fetch_last_data, generate_line_chart, generate_top_prov, generate_top_kabkot, generate_calendar

from dotenv import dotenv_values

config = dotenv_values("./.env")
CONNECTION_URI = config.get("CONNECTION_URI")

# Instantiate Dash App ------------------------------------------------------
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.DARKLY], 
                title="Kabar Api",
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1", 'charSet':'“UTF-8”'}])
server = app.server


# DASHBOARD COMPONENTS ------------------------------------------------------
# Navigation
nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Tentang Kabar Api", href="", target="_blank", className="text-left")),
        dbc.NavItem(dbc.NavLink("GitHub", href="https://bit.ly/48wt3mv", target="_blank", className="text-left")),
        # dbc.NavItem(dbc.NavLink("Data with Alvin")),
        dbc.NavItem(
            [
                dcc.Interval(
                    id='interval-component',
                    interval=60*1000, # in milliseconds, set to 1 minute
                    n_intervals=0
                ),
                html.Div(
                    id='live-update-text', 
                    style={'margin-top': '6px'}),
            ], 
            className="text-left"
        )
    ],
    className="text-left"
)

# Select Timeframe
radioitems = html.Div(
    [
        dbc.Label("Pilih Timeframe:"),
        dbc.RadioItems(
            options=
            [
                {"label": "7 Hari Terakhir", "value": 7},
                {"label": "15 Hari Terakhir", "value": 15},
                {"label": "30 Hari Terakhir", "value": 30},
            ],
            value=7,
            id="radioitems-input",
        ),
    ],
    className="mb-3"
)

# Density Map
card_map = dbc.Card(
    [
        dbc.CardHeader("Peta Density Titik Api"),
        dbc.CardBody(
            [
                dcc.Loading(
                    id="loading-map",
                    type="cube",
                    fullscreen=False,
                    children=[dcc.Graph(id="density_map", figure={}, style={"height": "50vh"})]
                    ),
                    html.Div("Fetching data. Please wait.", id="loading-message", className="loading-message-hidden")
            ],
            style={"position": "relative"}
        )
]
)

# Big Numbers
card_n_fires = dbc.Card(
    [
        html.Small(id="n_days", className='big-number-tittle'),
        html.H5(id='count_fire', className='big-number')
    ], style={"height": "5vh"}
)
card_confidence = dbc.Card(
    [
        html.Small("Titik Api dengan High-Confidence Level", className='big-number-tittle'),
        html.H5(id='count_confidence', className='big-number')
    ], style={"height": "5vh"}
)
card_burn_area = dbc.Card(
    [
        html.Small("Luas Karhutla Jan-Agu 2023 (databoks)", className='big-number-tittle'),
        html.H5("267,935.59 hektare", className='big-number')
    ], style={"height": "5vh"}
)

# Top-5 Provinces
card_top_prov = dbc.Card(
    [
        dbc.CardHeader("Top-5 Provinsi"),
        dbc.CardBody(
            [
                dcc.Loading(
                    id="loading-top-prov",
                    type="cube",
                    fullscreen=False,
                    children=[dcc.Graph(id="top_10_prov", figure={}, style={"height": "21vh"})]
                    )
            ]
        )
]
)

# Top-5 Districts
card_top_district = dbc.Card(
    [
        dbc.CardHeader(f"Top-5 Kabupaten/Kota"),
        dbc.CardBody(
            [
                dcc.Loading(
                    id="loading-top-districts",
                    type="cube",
                    fullscreen=False,
                    children=[dcc.Graph(id="top_10_districts", figure={}, style={"height": "21vh"})]
                )
            ]
        )
]
)

# Daily Number of Fires
card_line_chart = dbc.Card(
    [
        dbc.CardHeader("Jumlah Titik Api Harian Terdeteksi Tingkat Nasional"),
        dbc.CardBody(
            [
                dcc.Loading(
                    id="loading-line-chart",
                    type="cube",
                    fullscreen=False,
                    children=[dcc.Graph(id="line_chart_viirs", figure={}, style={"height": "17vh"})]
                )
            ]
        )
]
)

# Latest Articles
query_articles = """
    SELECT title, url, image, published_time
    FROM articles
    WHERE published_date > CURRENT_DATE - INTERVAL '2 day'
    ORDER BY published_time DESC
"""
articles = fetch_last_data(query=query_articles, uri_connection=CONNECTION_URI)
articles = articles.to_pandas()

cards = []
for i, row in articles.iterrows():
    image = row["image"]
    title = row["title"]
    url = row["url"]
    publish = row["published_time"]

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
                                html.H5(f"{title}"),
                                html.Small(
                                    f"Published time: {publish}",
                                    className="card-text text-muted",
                                ),
                                dbc.Button(
                                    "Read Article",
                                    href=f"{url}",
                                    external_link=True,
                                    color="secondary",
                                    target="_blank"
                                )
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
        color="danger",
        outline=True
    )
    cards.append(card)

card_articles = dbc.Card(
    [
        dbc.CardHeader("Artikel Terkait"),
        dbc.CardBody(cards, style={"overflow": "auto", "maxHeight": "33vh"})
    ]
)

# Latest Air Quality Index
query_aqi = """
    WITH RANKED_DATA AS (
    SELECT 
        address, city, province, air_quality_index, category, updated_at, 
        ROW_NUMBER() OVER (PARTITION BY address, city, province ORDER BY updated_at DESC) AS rn
    FROM 
        air_quality_idn
    WHERE 
        DATE(updated_at) = CURRENT_DATE
    )
    SELECT 
        *
    FROM 
        RANKED_DATA
    WHERE 
        rn = 1
    ORDER BY 
        air_quality_index DESC
"""
air_quality = fetch_last_data(query=query_aqi, uri_connection=CONNECTION_URI)
air_quality = air_quality.to_pandas()

air_quality["province"] = air_quality["province"].replace(
    {
    "Dki Jakarta":"DKI Jakarta", "Ntt":"NTT", "Ntb":"NTB", "Nad":"Aceh"
    }
)

aqi_cards = []
for i, row in air_quality.iterrows():
    aqi = row["air_quality_index"]
    category = row.get("category", "Unknown")
    address = row["address"]
    updated_at = row["updated_at"]
    city = row["city"]

    color_mapping = {
        "Sangat Tidak Sehat": "secondary",
        "Tidak Sehat": "danger",
        "Sedang": "warning",
        "Baik": "success",
        "Berbahaya": "black",
        "Unknown": "info"  # for unexpected or missing values
    }

    color = color_mapping.get(category, "info")  # default to 'info' if category is not recognized

    card = dbc.Card(
        [
        # dbc.CardHeader(f"{city} | AQI: {aqi} | Category: {category}", style={"background": f"{color}"}),
        dbc.CardBody(
            [
                html.H6(f"{city} | AQI: {aqi} | {category}"),
                html.Hr(),
                html.P(f"Lokasi: {address}",
                       className="card-text"),
                html.Small(
                    f"Diperbaharui: {updated_at} (waktu lokal)",
                    className="card-text text-muted",
                ),
            ]
        )
        ],
        color=color,
        className="mb-1",
        style={"maxWidth": "500px"},
        outline=False
    )

    aqi_cards.append(card)

card_air_quality = dbc.Card(
    [
        dbc.CardHeader("Near Real-Time Kualitas Udara (AQI)"),
        dbc.CardBody(aqi_cards, style={"overflow": "auto", "maxHeight": "33vh"})
    ]
)

# Maximum temperature calendar heatmap
calendar_heatmap = dbc.Card(
    [
        dbc.CardHeader("Kalender Temperatur Maksimum Tingkat Nasional Tahun 2023"),
        dbc.CardBody(
            [
                html.Iframe(
                    id="heatmap-calendar",
                    style={'width': '100%', "height": "33vh"}
                    )
             ], 
             style={"height": "33vh"}
        )
    ]
)



# DASHBOARD LAYOUT ------------------------------------------------------
app.layout = dbc.Container(
    [
    # ----- First Row Layout -----
    # Contains title and navigation links
        dbc.Row(
            [
                dbc.Col(
                    [
                        html.Div(html.H3("Kabar Api"), style={"text-align": "left"})
                    ], lg=2, md=12, sm=12, xs=12, className="offset-lg-1", style={"height":"5vh"},
                ),
                dbc.Col(nav, lg=5, md=12, sm=12, xs=12, className="offset-lg-3", style={"height":"5vh"}),
                dcc.Store(id='store_data')
            ]
        ),

    # ----- Second Row Layout -----
    # Contains select timeframe, density map, big numbers, top-5 provinces, top-5 districts, daily number of fires
    dbc.Row(
        [
            dbc.Col([radioitems], lg=1, md=2, sm=2, xs=3), 
            dbc.Col([card_map], lg=5, md=10, sm=10, xs=9),
            dbc.Col(
                [
                    # Big numbers
                    dbc.Row(
                        [
                            dbc.Col([card_n_fires]),
                            dbc.Col([card_confidence]),
                            dbc.Col([card_burn_area]),
                        ], className="g-2"
                    ),

                    # Top-5 Provinces and Districts
                    dbc.Row(
                        [
                            dbc.Col([card_top_prov], width=6),
                            dbc.Col([card_top_district], width=6)
                        ], className="g-2"
                    ),

                    # Daily number of fires
                    dbc.Row(
                        [
                            dbc.Col([card_line_chart])
                        ], className="g-2"
                    )

                ], className="g-2", lg=5, md=12, sm=12, xs=12
            ),
        ], className="g-2"
    ),


    # ----- Third Row Layout -----
    # Contains articles, air quality index

    dbc.Row(
        [
            dbc.Col([calendar_heatmap], lg=4, md=12, sm=12, xs=12, className="offset-lg-1"),
            dbc.Col([card_articles], lg=3, md=12, sm=12, xs=12),
            dbc.Col([card_air_quality], lg=3, md=12, sm=12, xs=12),

        ], className="g-2"
    ),

    ], 
fluid=True
)


# ------------------- CALLBACKS -------------------
# ----- Calendar -----
@app.callback(
    Output('heatmap-calendar', 'srcDoc'),
    Input('radioitems-input', 'value')  # Replace with the ID and property of the component that triggers the callback
)
def update_calendar(data):  # Replace 'value' with the actual input value(s) you need
    query_temp = """
        SELECT date, max_temp_c
        FROM idn_gsod
        ORDER BY date DESC
    """
    max_temperature = fetch_last_data(query=query_temp, uri_connection=CONNECTION_URI)
    max_temperature = max_temperature.to_pandas()
    calendar_html = generate_calendar(max_temperature)
    return calendar_html

# ----- Callback for dates and times -----
@app.callback(
        Output('live-update-text', 'children'),
        Input('interval-component', 'n_intervals')
        )
def update_date(n):
    return datetime.datetime.now().strftime('%b %d, %Y | %H:%M')

# ----- Callback update card title -----
@app.callback(
    Output("n_days", "children"),
    Input("radioitems-input", "value")
)
def update_card_tittle(filter_time_period):
    n_days = f"Titik Api Terdeteksi {filter_time_period} Hari Terakhir"

    return n_days


# ----- Callback density map -----
@app.callback(
    Output("density_map", "figure"),
    Output("store_data", "data"),
    Input("radioitems-input", "value")
)
def update_density_map(filter_time_period):
    fig, data = generate_density_map(n_day=filter_time_period, uri_connection=CONNECTION_URI)
    return fig, data


# ----- Callback dcc.loading -----
@app.callback(
    Output("loading-message", "className"),
    [Input("loading-map", "loading_state")]
)
def update_loading_message(loading_state):
    if loading_state and loading_state["is_loading"]:
        return "loading-message-visible"
    return "loading-message-hidden"


# ----- Callback number of daily detected fire -----
@app.callback(
    Output("line_chart_viirs", "figure"),
    Output("count_fire", "children"),
    Output("count_confidence", "children"), 
    Input("store_data", "data")

)
def update_line_chart(jsonified_data):
    fig, count_fire, count_confidence = generate_line_chart(jsonified_data)
    return fig, count_fire, count_confidence


# ----- Callback top-5 province -----
@app.callback(
    Output("top_10_prov", "figure"),
    Input("store_data", "data")

)
def update_bar_chart(jsonified_data):
    fig = generate_top_prov(jsonified_data)
    return fig

# ----- Callback top-5 district -----
@app.callback(
    Output("top_10_districts", "figure"),
    Input("store_data", "data")

)
def update_bar_chart(jsonified_data):
    fig = generate_top_kabkot(jsonified_data)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)