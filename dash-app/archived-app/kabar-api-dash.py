import datetime
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import dash_bootstrap_components as dbc

from src.procedures import generate_density_map, fetch_last_data, generate_line_chart, generate_top_prov, generate_top_kabkot

from dotenv import dotenv_values

config = dotenv_values("./.env")
CONNECTION_URI = config.get("CONNECTION_URI")

# Instantiate Dash App ------------------------------------------------------
app = dash.Dash(__name__, 
                external_stylesheets=[dbc.themes.DARKLY], 
                title="Kabar Api",
                meta_tags=[{"name": "viewport", "content": "width=device-width, initial-scale=1", 'charSet':'“UTF-8”'}])
server = app.server


# Sidebar component ------------------------------------------------------
sidebar = dbc.Card(
    dbc.CardBody([
        html.H4("Kabar Api"),
        html.Hr(),
        html.P("Pilih Timeframe: "),
        dcc.Dropdown(
            id="select_timeframe",
            options=
                [
                    {"label": "7 Hari Terakhir", "value":7},
                    {"label": "15 Hari Terakhir", "value":15},
                    {"label": "30 Hari Terakhir", "value":30},
                ],
            value=7, #default value
            clearable=False,
            optionHeight=25
            ),
        html.Hr(),
        # dbc.Nav(
        #     [
        #         dbc.NavItem(dbc.NavLink("GitHub", href="https://bit.ly/48wt3mv", target="_blank")),
        #         dbc.NavItem(dbc.NavLink("Twitter", href="https://bit.ly/3RqSyPY", target="_blank")),
        #         dbc.NavItem(dbc.NavLink("Data with Alvin", disabled=True))
        #     ], vertical=True
        # )
    ]),
    style={
        "position":"fixed",
        "top":0,
        "left":0,
        "bottom":0,
        # "padding": "2rem 1rem"
        }
)


# Big numbers component ------------------------------------------------------
# total active fire in last n days
card_n_fires = dbc.Card([
    html.H4("230495"),
    html.Small("Titik Api Terdeteksi 7 Hari Terakhir")
    # dbc.CardBody([dcc.Loading(
    #     id="loading-5",
    #     type="cube",
    #     fullscreen=False,
    #     children=[dcc.Graph(id="top_10_districts", figure={}, style={"height": "10vh"})]
    # )])
])

card_confidence = dbc.Card([
    html.Small("Titik Api dengan High-Confidence Level"),
    html.H4("10482")
])

card_burn_area = dbc.Card([
    html.Small("Luas Karhutla Jan-Agu 2023 (databoks)"),
    dbc.Row([
        dbc.Col(html.H4("267.935,59")),
        dbc.Col(html.Small("ha", style={"text-align":"left"}))]),
])






# Layout ------------------------------------------------------
app.layout = dbc.Container([

    # First Row -------
    dbc.Row([
        # First Row, First Column (Sidebar) -------
        dbc.Col(sidebar, width={"size":2 ,"order":"first"}),

        # First Row, Second Column (Big Numbers) -------
        dbc.Col([card_n_fires], width=3),
        dbc.Col([card_confidence], width=3),
        dbc.Col([card_burn_area], width=3),

    ])



],
fluid=True
)





# Runs the app ------------------------------------------------------------
if __name__ == '__main__':
    app.run_server(debug=True)









# # ------------------- INITIALIZE CARDS -------------------
# # articles section
# query = f"""
#     SELECT title, url, image, published_time
#     FROM articles
#     WHERE published_date > CURRENT_DATE - INTERVAL '2 day'
#     """

# articles = fetch_last_data(query=query, uri_connection=CONNECTION_URI)
# articles = articles.to_pandas()

# cards = []
# for i, row in articles.iterrows():
#     image = row["image"]
#     title = row["title"]
#     url = row["url"]
#     publish = row["published_time"]

#     card = dbc.Card(
#         [
#             dbc.Row(
#                 [
#                     dbc.Col(
#                         dbc.CardImg(
#                             src=image,
#                             className="img-fluid rounded-start",
#                         ),
#                         className="col-md-3",
#                     ),
#                     dbc.Col(
#                         dbc.CardBody(
#                             [
#                                 html.H5(f"{title}"),
#                                 html.Small(
#                                     f"Published time: {publish}",
#                                     className="card-text text-muted",
#                                 ),
#                                 dbc.Button(
#                                     "Read Article",
#                                     href=f"{url}",
#                                     external_link=True,
#                                     color="secondary",
#                                     target="_blank"
#                                 )
#                             ]
#                         ),
#                         className="col-md-9",
#                     ),
#                 ],
#                 className="g-0 d-flex align-items-center",
#             )
#         ],
#         className="mb-3",
#         style={"maxWidth": "540px"},
#         color="danger",
#         outline=True
#     )
#     cards.append(card)

# card_articles = dbc.Card([
#     dbc.CardHeader("Artikel Terkait"),
#     dbc.CardBody(cards, style={"overflow": "auto", "maxHeight": "32vh"})
# ])

# # navigation section
# nav = dbc.Nav(
#     [
#         dbc.NavItem(dbc.NavLink("Data with Alvin", disabled=True)),
#         dbc.NavItem(dbc.NavLink("GitHub", href="https://bit.ly/48wt3mv", target="_blank")),
#         dbc.NavItem(dbc.NavLink("Twitter", href="https://bit.ly/3RqSyPY", target="_blank")),
#         dbc.NavItem(dbc.NavLink("Buy Me a Coffee", href="", target="_blank"))
#     ]
# )

# radioitems = html.Div(
#     [
#         dbc.Label("Pilih Timeframe:"),
#         dbc.RadioItems(
#             options=[
#                 {"label": "7 Hari Terakhir", "value": 7},
#                 {"label": "15 Hari Terakhir", "value": 15},
#                 {"label": "30 Hari Terakhir", "value": 30},
#             ],
#             value=7,
#             id="radioitems-input",
#         ),
#     ]
# )


# # density map section
# card_map = dbc.Card([
#     dbc.CardHeader(children=[
#         dbc.Row([
#             dbc.Col(html.Header("Peta Persebaran Titik Panas"), width=4),
#             # dbc.Col(html.Header("Timeframe:"), width={"size":4, "offset":1}, style={"text-align":"right"}),
#             # dbc.Col(
#             #     dcc.Dropdown(
#             #     id="filter_time_period",
#             #     options=[
#             #         {"label": "Last 7 Days", "value":7},
#             #         {"label": "Last 15 Days", "value":15},
#             #         {"label": "Last 30 Days", "value":30},
#             #         ],
#             #     value=7, #default value
#             #     clearable=False,
#             #     optionHeight=25,
#             #     # style={"display": "inline-block"}
#             # ), width=3)

#         ])
#     ]),
#     dbc.CardBody([dcc.Loading(
#         id="loading",
#         type="cube",
#         fullscreen=False,
#         children=[dcc.Graph(id="density_map", figure={}, style={"height": "50vh"})]
#     )])
# ])

# # line chart section
# card_line_chart = dbc.Card([
#     dbc.CardHeader("Jumlah Titik Api Harian Terdeteksi Tingkat Nasional"),
#     dbc.CardBody([dcc.Loading(
#         id="loading-2",
#         type="cube",
#         fullscreen=False,
#         children=[dcc.Graph(id="line_chart_viirs", figure={}, style={"height": "20vh"})]
#     )])
# ])

# # top 5 provinces section
# card_top_prov = dbc.Card([
#     dbc.CardHeader("Top-5 Provinsi"),
#     dbc.CardBody([dcc.Loading(
#         id="loading-3",
#         type="cube",
#         fullscreen=False,
#         children=[dcc.Graph(id="top_10_prov", figure={}, style={"height": "23vh"})]
#     )])
# ])

# # top 5 kabkot section
# card_top_district = dbc.Card([
#     dbc.CardHeader(f"Top-5 Kabupaten/Kota"),
#     dbc.CardBody([dcc.Loading(
#         id="loading-4",
#         type="cube",
#         fullscreen=False,
#         children=[dcc.Graph(id="top_10_districts", figure={}, style={"height": "23vh"})]
#     )])
# ])


# # total active fire in last n days
# card_n_fires = dbc.Card([
#     html.H4("230495", style={"height": "2vh"}, className="text-center"),
#     html.Small("Titik Api Terdeteksi 7 Hari Terakhir", style={"height": "2vh"}, className="text-center")
#     # dbc.CardBody([dcc.Loading(
#     #     id="loading-5",
#     #     type="cube",
#     #     fullscreen=False,
#     #     children=[dcc.Graph(id="top_10_districts", figure={}, style={"height": "10vh"})]
#     # )])
# ], color="danger", inverse=True)

# card_confidence = dbc.Card([
#     html.H4("10482", style={"height": "2vh"}, className="text-center"),
#     html.Small("Titik Api dengan High-Confidence Level", style={"height": "2vh"}, className="text-center")
# ], color="danger", inverse=True)

# card_burn_area = dbc.Card([
#     dbc.Row([
#         dbc.Col(html.H4("267.935,59", style={"height": "2vh", "text-align":"right"}), width=8),
#         dbc.Col(html.Small("ha", style={"height": "2vh", "text-align":"left"}), width=2)]),
#     html.Small("Luas Karhutla Jan-Agu 2023 (databoks)", style={"height": "2vh"}, className="text-center")
# ], color="danger", inverse=True)




# # NRT air quality index section
# query = """
#     WITH RANKED_DATA AS (
#     SELECT 
#         address, city, province, air_quality_index, category, updated_at, 
#         ROW_NUMBER() OVER (PARTITION BY address, city, province ORDER BY updated_at DESC) AS rn
#     FROM 
#         air_quality_idn
#     WHERE 
#         DATE(updated_at) = CURRENT_DATE
#     )
#     SELECT 
#         *
#     FROM 
#         RANKED_DATA
#     WHERE 
#         rn = 1
#     ORDER BY 
#         air_quality_index DESC
# """

# air_quality = fetch_last_data(query=query, uri_connection=CONNECTION_URI)
# air_quality = air_quality.to_pandas()

# air_quality["province"] = air_quality["province"].replace({
#     "Dki Jakarta":"DKI Jakarta", "Ntt":"NTT", "Ntb":"NTB", "Nad":"Aceh"
# })

# aqi_cards = []
# for i, row in air_quality.iterrows():
#     aqi = row["air_quality_index"]
#     category = row.get("category", "Unknown")  # handle missing values
#     address = row["address"]
#     updated_at = row["updated_at"]
#     city = row["city"]

#     color_mapping = {
#         "Tidak Sehat": "danger",
#         "Sedang": "warning",
#         "Baik": "success",
#         "Berbahaya": "secondary",
#         "Unknown": "info"  # for unexpected or missing values
#     }

#     color = color_mapping.get(category, "info")  # default to 'info' if category is not recognized

#     card = dbc.Card(
#         [
#         # dbc.CardHeader(f"{city} | AQI: {aqi} | Category: {category}", style={"background": f"{color}"}),
#         dbc.CardBody(
#             [
#                 html.H6(f"{city} | AQI: {aqi} | {category}"),
#                 html.Hr(),
#                 html.P(f"Location: {address}",
#                        className="card-text"),
#                 html.Small(
#                     f"Updated at: {updated_at} (local time)",
#                     className="card-text text-muted",
#                 ),
#             ]
#         )
#         ],
#         color=color,
#         className="mb-3",
#         style={"maxWidth": "500px"},
#         outline=False
#     )

#     aqi_cards.append(card)

# card_air_quality = dbc.Card([
#     dbc.CardHeader("Near Real-Time Kualitas Udara (AQI)"),
#     dbc.CardBody(aqi_cards, style={"overflow": "auto"})
# ], style={"height": "27vh"})

# # ------------------- BUILD APP LAYOUT -------------------
# app.layout = dbc.Container([
#     # ----- first row layout -----
#     # contains title and navigation links
#     dbc.Row([
#       dbc.Col([
#           html.Div(html.H2("Kabar Api"), style={"text-align": "left"})
#       ], width={"size":4, "offset":1, "order":"first"}, style={"height":"5vh"}, ),
#       dbc.Col([card_n_fires], width=2),
#       dbc.Col([card_confidence], width=2),
#       dbc.Col([card_burn_area], width=2),
#     #   dbc.Col(nav, width={"size": 5, "offset":1, "order":"second"}, style={"height":"5vh"}),
#       dcc.Store(id='store_data')
#     ], className="g-0"),

#     # ----- second row layout -----
#     # contains side bar, main map, articles cards, nad social media
#     dbc.Row([

#         dbc.Col([radioitems], width=1), 
#         dbc.Col([card_map], width={"size":5}),

#         # second column (top 5 prov, top 5 district, daily fire count)
#         dbc.Col([
#             dbc.Row(
#                 [dbc.Col([card_top_prov], width=6),
#                 dbc.Col([card_top_district], width=6)], className="g-0"
#             ),
#             dbc.Row(
#                 [dbc.Col([card_line_chart], width=6),
#                  dbc.Col([card_air_quality], width=6)], className="g-0"
#             )
#         ], width=5)

#     ], className="g-0"),


#     # ----- third row layout -----
#     # contains daily line chart, top-5 province, top-5 district/kabkot, carousel
#     dbc.Row([

#         # second column
#         dbc.Col([card_articles], width={"size":3, "offset":1}),


#         # third
#         # dbc.Col([card_air_quality], width=7),
#     ], className="g-0")
#     # # stores the result data
#     # dcc.Store(id='result-data')
# ], 
# fluid=True
# )




# # ------------------- CALLBACKS -------------------
# # ----- Callback density map -----
# @app.callback(
#     Output("density_map", "figure"),
#     Output("store_data", "data"),
#     Input("radioitems-input", "value")
# )
# def update_density_map(filter_time_period):
#     fig, data = generate_density_map(n_day=filter_time_period, uri_connection=CONNECTION_URI)

#     return fig, data

# # ----- Callback number of daily detected fire -----
# @app.callback(
#     Output("line_chart_viirs", "figure"),
#     Input("store_data", "data")

# )
# def update_line_chart(jsonified_data):
#     fig = generate_line_chart(jsonified_data)
#     return fig


# # ----- Callback top-5 province -----
# @app.callback(
#     Output("top_10_prov", "figure"),
#     Input("store_data", "data")

# )
# def update_bar_chart(jsonified_data):
#     fig = generate_top_prov(jsonified_data)
#     return fig

# # ----- Callback top-5 district -----
# @app.callback(
#     Output("top_10_districts", "figure"),
#     Input("store_data", "data")

# )
# def update_bar_chart(jsonified_data):
#     fig = generate_top_kabkot(jsonified_data)
#     return fig


# if __name__ == '__main__':
#     app.run_server(debug=True)




# copy_kabar_api = """
# Kabar Api merupakan platform dashboard terintegrasi yang menampilkan informasi aktual mengenai kebakaran hutan, kebakaran lahan, dan kualitas udara di hampir seluruh wilayah Indonesia. 
# Dengan memanfaatkan teknologi dan data dari sumber berkualitas seperti VIIRS SNPP NASA, Google News, dan KLHK, Kabar Api berkomitmen untuk memberikan gambaran mendalam dan komprehensif tentang situasi lingkungan di Indonesia.
# """

# copy_kabar_api2 = """
# Kabar Api memahami bagaimana pentingnya informasi cepat dan tepat di era digital saat ini, terutama mengenai isu-isu lingkungan yang berdampak langsung pada kehidupan kita sehari-hari. 
# Oleh karena itu, Kabar Api terus berupaya mengembangkan berbagai fitur tambahan untuk meningkatkan pengalaman pengguna dan memastikan informasi yang disajikan selalu relevan juga akurat.
# """

# card_empty = dbc.Card(
#     [
#         dbc.CardHeader("Tentang Kabar Api"),
#         dbc.CardBody([
#             html.H5(copy_kabar_api),
#             html.H5(copy_kabar_api2)
#         ], style={"height": "33vh"})
#     ]
# )
