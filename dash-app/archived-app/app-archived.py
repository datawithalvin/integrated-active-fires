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

# ------------------- INITIALIZE CARDS -------------------
# articles section
query = f"""
    SELECT title, url, image, published_time
    FROM articles
    WHERE published_date > CURRENT_DATE - INTERVAL '2 day'
    """

articles = fetch_last_data(query=query, uri_connection=CONNECTION_URI)
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

card_articles = dbc.Card([
    dbc.CardHeader("Related Articles"),
    dbc.CardBody(cards, style={"overflow": "auto", "maxHeight": "53vh"})
])

# navigation section
gpt_analysis = """
The updated daily active fire data for Indonesia from September 11th to September 17th, 2023, reveals several critical environmental trends and concerns. Notably, there is a substantial spike in active fires on September 15th and 16th, with 5,275 and 5,400 fires respectively, possibly indicating a severe escalation in forest and land fires. These dates align with the typical dry season in Indonesia, suggesting a heightened risk of wildfires during this period. Sumatra Selatan, Nusa Tenggara Timur, and Papua provinces have alarmingly high fire counts, with 4,507, 4,089, and 1,748 fires, respectively, underscoring the need for targeted interventions and improved fire management practices in these regions. The data underscores the urgency of implementing proactive measures to prevent and mitigate wildfires, protect valuable ecosystems, and address the broader issue of deforestation and land-use practices contributing to these fires.
"""

nav = dbc.Nav(
    [
        dbc.NavItem(dbc.NavLink("Data with Alvin", disabled=True)),
        dbc.NavItem(dbc.NavLink("GitHub", href="https://bit.ly/48wt3mv", target="_blank")),
        dbc.NavItem(dbc.NavLink("Twitter", href="https://bit.ly/3RqSyPY", target="_blank"))
    ]
)

card_side_bar = dbc.Card(
    dbc.CardBody([
        dbc.Row([
            dbc.Col([
                html.P("Timeframe: ")
            ], width=5),
            dbc.Col(
                dcc.Dropdown(
                    id="filter_time_period",
                    options=[
                        {"label": "Last 7 Days", "value":7},
                        {"label": "Last 15 Days", "value":15},
                        {"label": "Last 30 Days", "value":30},
                        ],
                    value=7, #default value
                    clearable=False,
                    optionHeight=25
                ), width=7
            )
        ]),

        # dbc.Row([
        #     dbc.Col([
        #         html.P("Source: ")
        #     ], width=5),
        #     dbc.Col(
        #         dcc.Dropdown(
        #             id="filter_sensor_source",
        #             options=[
        #                 {"label": "NASA VIIRS S-NPP", "value":"S-NPP"},
        #                 ],
        #             value="S-NPP", #default value
        #             clearable=False,
        #             optionHeight=25
        #         ), width=7
        #     )
        # ]),

        html.Hr(),
        html.P(gpt_analysis, style={"text-align":"justify", "text-justify":"inter-word"})
    ], style={"height":"57vh", "overflow": "auto"})
)

# density map section
card_map = dbc.Card([
    dbc.CardHeader("Density Map"),
    dbc.CardBody([dcc.Loading(
        id="loading",
        type="cube",
        fullscreen=False,
        children=[dcc.Graph(id="density_map", figure={}, style={"height": "50vh"})]
    )])
])

# line chart section
card_line_chart = dbc.Card([
    dbc.CardHeader("Frequency of Detected Fires by Day"),
    dbc.CardBody([dcc.Loading(
        id="loading-2",
        type="cube",
        fullscreen=False,
        children=[dcc.Graph(id="line_chart_viirs", figure={}, style={"height": "30vh"})]
    )])
])

# top 10 provinces section
card_top_prov = dbc.Card([
    dbc.CardHeader("Top 10 Provinces by Active Fires"),
    dbc.CardBody([dcc.Loading(
        id="loading-3",
        type="cube",
        fullscreen=False,
        children=[dcc.Graph(id="top_10_prov", figure={}, style={"height": "30vh"})]
    )])
])

# top 10 districts section
card_top_district = dbc.Card([
    dbc.CardHeader(f"Top 10 Districts by Active Fires"),
    dbc.CardBody([dcc.Loading(
        id="loading-4",
        type="cube",
        fullscreen=False,
        children=[dcc.Graph(id="top_10_districts", figure={}, style={"height": "30vh"})]
    )])
])

# data source section
card_data_source = dbc.Card([
    dbc.CardHeader("Data Source"),
    dbc.CardBody(dbc.Carousel(
        items=[
            {"key":"FIRMS", "src":"/assets/images/firms-nasa.png"},
            {"key":"Google News", "src":"/assets/images/google_news.svg"},
            {"key":"KLHK", "src":"/assets/images/logo-klhk.svg"},
        ],
    controls=False,
    indicators=False,
    interval=2000,
    ride="carousel",
    id="data_source",
    style={"height":"30vh", "align-self":"center"}
    ))
])

# NRT air quality index section
query = """
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

air_quality = fetch_last_data(query=query, uri_connection=CONNECTION_URI)
air_quality = air_quality.to_pandas()

air_quality["province"] = air_quality["province"].replace({
    "Dki Jakarta":"DKI Jakarta", "Ntt":"NTT", "Ntb":"NTB", "Nad":"Aceh"
})

aqi_cards = []
for i, row in air_quality.iterrows():
    aqi = row["air_quality_index"]
    category = row.get("category", "Unknown")  # handle missing values
    address = row["address"]
    updated_at = row["updated_at"]
    city = row["city"]

    color_mapping = {
        "Tidak Sehat": "danger",
        "Sedang": "warning",
        "Baik": "success",
        "Berbahaya": "secondary",
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
                html.P(f"Location: {address}",
                       className="card-text"),
                html.Small(
                    f"Updated at (local time): {updated_at}",
                    className="card-text text-muted",
                ),
            ]
        )
        ],
        color=color,
        className="mb-3",
        style={"maxWidth": "500px"},
        outline=False
    )

    aqi_cards.append(card)

card_air_quality = dbc.Card([
    dbc.CardHeader("Near Real-Time Air Quality Index"),
    dbc.CardBody(aqi_cards, style={"overflow": "auto", "maxHeight": "53vh"})
])


# ------------------- BUILD APP LAYOUT -------------------
app.layout = dbc.Container([
    # ----- first row layout -----
    # contains title and navigation links
    dbc.Row([
      dbc.Col([
          html.Div(html.H2("Indonesia Comprehensive Environmental Monitoring Dashboard"))
      ], width=9, style={"height":"5vh"}, ),
      dbc.Col(nav, width=3, style={"height":"5vh"}),
      dcc.Store(id='store_data')
    ]),

    # ----- second row layout -----
    # contains side bar, main map, articles cards, nad social media
    dbc.Row([
        # # first column (side bar)
        dbc.Col([card_side_bar], width=2),

        # second column (density map)
        dbc.Col([card_map], width=5),

        # third column (articles)
        # dbc.Col(cards, width=3, style={"overflow":"auto"}),
        dbc.Col(html.Div(card_articles), width=3),

        # fourth column (air quality)
        dbc.Col(html.Div(card_air_quality), width=2)
    ], className="g-0"),


    # ----- third row layout -----
    # contains daily line chart, top-5 province, top-5 district/kabkot, carousel
    dbc.Row([
        # first column (daily line chart)
        dbc.Col([card_line_chart], width=4),

        # second column (top-5 province)
        dbc.Col([card_top_prov], width=3),

        # third column (top-5 kabkot)
        dbc.Col([card_top_district], width=3),

        # fourth column (carousel information)
        dbc.Col([card_data_source], width=2),
    ], className="g-0")
    # # stores the result data
    # dcc.Store(id='result-data')
], 
fluid=True
)


# ------------------- CALLBACKS -------------------
# ----- Callback density map -----
@app.callback(
    Output("density_map", "figure"),
    Output("store_data", "data"),
    Input("filter_time_period", "value")
)
def update_density_map(filter_time_period):
    fig, data = generate_density_map(n_day=filter_time_period, uri_connection=CONNECTION_URI)

    return fig, data

# ----- Callback number of daily detected fire -----
@app.callback(
    Output("line_chart_viirs", "figure"),
    Input("store_data", "data")

)
def update_line_chart(jsonified_data):
    fig = generate_line_chart(jsonified_data)
    return fig


# ----- Callback top-10 province -----
@app.callback(
    Output("top_10_prov", "figure"),
    Input("store_data", "data")

)
def update_bar_chart(jsonified_data):
    fig = generate_top_prov(jsonified_data)
    return fig

# ----- Callback top-10 district -----
@app.callback(
    Output("top_10_districts", "figure"),
    Input("store_data", "data")

)
def update_bar_chart(jsonified_data):
    fig = generate_top_kabkot(jsonified_data)
    return fig


if __name__ == '__main__':
    app.run_server(debug=True)