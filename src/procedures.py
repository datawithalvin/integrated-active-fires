import polars as pl
import pandas as pd
import requests
import datetime
import time

import geopandas as gpd
from shapely.geometry import Point

from gnews import GNews
from newspaper import Article

# ----------------------------------------------------- ******************************** -----------------------------------------------------
def fetch_viirs_data(today: str, day_range: str, token: str) -> pl.DataFrame:
    """
    Retrieves VIIRS active fires data from the NASA FIRMS API for a given date and date range.

    Parameters:
    - today (str): The specific date for which the data is to be retrieved, in the format "YYYY-MM-DD".
    - day_range (str): The range of days for which the data is to be retrieved, e.g., "3" for the last 3 days.
    - token (str): The token obtained from the FIRMS API.

    Returns:
    - pl.DataFrame: A Polars DataFrame containing the VIIRS active fires data if the retrieval is successful, 
                    or None if an error occurred during retrieval.
    """

    try:
        host = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/"

        source = "VIIRS_SNPP_NRT"
        country = "IDN"

        url = (host + token + "/" + source + "/" + country + "/" + day_range + "/" + today)
        viirs_df = pl.read_csv(url)
        
        return viirs_df

    except requests.RequestException as e:
        print(f"An error occurred while making the HTTP request: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
# ----------------------------------------------------- ******************************** -----------------------------------------------------
def extract_administrative(df: pl.DataFrame) -> pd.DataFrame:

    # cast to pandas dataframe
    # load administrative boundaries
    viirs = df.to_pandas()
    file_path = "./data/IndonesianCitiesDistrictsUpdated.json"
    adm_df = gpd.read_file(file_path)

    # Zip lat-lon as tuple, convert to Points object
    viirs["coords"] = list(zip(viirs["longitude"], viirs["latitude"]))
    viirs["coords"] = viirs["coords"].apply(Point)

    # Turn into geodataframe, perform spatial join
    points = gpd.GeoDataFrame(viirs, geometry="coords")
    joined_df = gpd.tools.sjoin(points, adm_df, predicate="within", how='left')

    return joined_df

# ----------------------------------------------------- ******************************** -----------------------------------------------------
def fetch_last_data(query: str, uri_connection: str) -> pl.DataFrame:
    """
    Retrieves the most recently updated data from the database based on the provided SQL query.

    Parameters:
    - query (str): The SQL query string used to fetch the data.
    - uri_connection (str): The connection URI to the Supabase database.

    Returns:
    - pl.DataFrame: A DataFrame containing the last updated data retrieved from the database.
    """
    try:
        last_data = pl.read_database_uri(query=query, uri=uri_connection)
        return last_data
    
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

# ----------------------------------------------------- ******************************** -----------------------------------------------------
def cleaning_fetched_data(df: pd.DataFrame) -> pl.DataFrame:
    """
    Cleans the newly fetched data by dropping unnecessary columns, adding a new column,
    and casting columns to align with the data types of the last fetched data from the database.

    Parameters:
    - df (pd.DataFrame): A Pandas DataFrame containing the fetched data to be cleaned.

    Returns:
    - pl.DataFrame: A cleaned Polars DataFrame with aligned column data types.
    """

    try:
        # # Add a new 'type' column with default value None
        # df = df.with_columns(
        #     type=pl.lit(None)
        # )

        # # Select and cast specific columns to align with the desired data types
        # df = df.select(
        #     pl.col("latitude").cast(pl.Float64),
        #     pl.col("longitude").cast(pl.Float64),
        #     pl.col("bright_ti4").cast(pl.Float32).alias("brightness"),
        #     pl.col("scan").cast(pl.Float32),
        #     pl.col("track").cast(pl.Float32),
        #     pl.col("acq_date").str.strptime(pl.Date, "%Y-%m-%d"),
        #     pl.col("acq_time").cast(pl.Int32),
        #     pl.col("satellite").cast(pl.Utf8),
        #     pl.col("instrument").cast(pl.Utf8),
        #     pl.col("confidence").cast(pl.Utf8),
        #     pl.col("version").cast(pl.Utf8),
        #     pl.col("bright_ti5").cast(pl.Float32).alias("bright_t31"),
        #     pl.col("frp").cast(pl.Float32),
        #     pl.col("daynight").cast(pl.Utf8),
        #     pl.col("type").cast(pl.Int32)
        # )

        # change datetype format
        df["acq_date"] = pd.to_datetime(df["acq_date"]).dt.strftime('%Y-%m-%d')

        # replace values
        df["confidence"] = df["confidence"].replace({
            "n":"Nominal", "h":"High", "l":"Low"
        })

        df["daynight"] = df["daynight"].replace({
            "D":"Day", "N":"Night"
        })

        # Rename some columns, drop the unnecessary ones for the analysis
        df = df.rename(columns={
            "id":"second_adm", "provinsi":"first_adm", "bright_ti4":"brightness"
        })

        df = df.drop(["country_id", "scan", "track", "bright_ti5", "coords", "index_right"], axis=1)


        pl_df = pl.from_pandas(df)
        pl_df = pl_df.with_columns(
            pl.col("acq_date").str.strptime(pl.Date, "%Y-%m-%d")
        )

        return pl_df

    except Exception as e:
        print(f"An error occurred while cleaning the data: {e}")
        return None

# ----------------------------------------------------- ******************************** -----------------------------------------------------
def fetch_air_quality_data() -> pl.DataFrame:
    """
    Fetches air quality data from the provided API endpoint, processes it, and returns a Polars DataFrame.

    Returns:
    - pl.DataFrame: A Polars DataFrame containing the processed air quality data.
    """
    try:
        # Set endpoint, request it and extract the JSON object by parsing it into a Pandas DataFrame
        endpoint = "https://sipongi.menlhk.go.id/api/aqms"
        r = requests.get(endpoint, headers={'Accept': 'application/json'})
        aqms_json = r.json()
        aqms_df = pd.json_normalize(aqms_json["features"])

        # Select the desired columns, and rename them
        columns_to_select = ["properties.alamat", "geometry.coordinates", "properties.kota", "properties.provinsi", "properties.nilai", "properties.cat", "properties.waktu"]
        aqms_df = aqms_df[columns_to_select]
        aqms_df.columns = ["address", "coordinates", "city", "province", "air_quality_index", "category", "updated_at"]
        aqms_df["latitude"] = aqms_df["coordinates"].apply(lambda x: x[1])
        aqms_df["longitude"] = aqms_df["coordinates"].apply(lambda x: x[0])
        aqms_df.drop(columns=["coordinates"], inplace=True)

        # Add a new "fetched_date" column with today's date
        today_date = datetime.date.today()
        aqms_df["fetched_date"] = today_date

        aqms_df.dropna(subset=["air_quality_index"], inplace=True)

        # Convert to a Polars DataFrame
        pl_aqms = pl.from_pandas(aqms_df)

        return pl_aqms

    except Exception as e:
        print(f"An error occurred while fetching air quality data: {e}")
        return None

# ----------------------------------------------------- ******************************** -----------------------------------------------------
def cleaning_aqms_data(df: pl.DataFrame) -> pl.DataFrame:
    """
    Cleans the provided air quality data Polars DataFrame by reordering columns,
    renaming columns, and converting data types.

    Parameters:
    - df (pl.DataFrame): The Polars DataFrame containing air quality data to be cleaned.

    Returns:
    - pl.DataFrame: A cleaned Polars DataFrame with reordered columns, renamed columns,
      and converted data types.
    """
    try:
        # Reorder, rename, and cast data types of the columns
        df = df.select(
            pl.col("latitude").cast(pl.Utf8).alias("lat_sensor"),
            pl.col("longitude").cast(pl.Utf8).alias("lon_sensor"),
            pl.col("address"),
            pl.col("city").str.to_titlecase(),
            pl.col("province").str.to_titlecase(),
            pl.col("air_quality_index").cast(pl.Int16),
            pl.col("category").str.to_titlecase().cast(pl.Categorical),
            pl.col("updated_at").str.to_datetime("%Y-%m-%d %H:%M:%S"),
            pl.col("fetched_date"),
        )

        return df

    except Exception as e:
        print(f"An error occurred while cleaning the data: {e}")
        return None

# ----------------------------------------------------- ******************************** -----------------------------------------------------

def fetch_articles(keywords_list: list, max_results: int, day_range: int) -> pd.DataFrame:
    """
    Fetches news articles using the Google News API for a list of keywords,
    extracts relevant information, and returns a concatenated DataFrame.

    Parameters:
    - keywords_list (list): List of keywords to search for in the news articles.
    - max_results (int): Maximum number of news articles to retrieve for each keyword.
    - day_range (int): Number of days in the past to search for news articles.

    Returns:
    - pd.DataFrame: A concatenated DataFrame containing relevant information from the retrieved articles.
    """
    concatenated_df = pd.DataFrame()

    try:
        for keywords in keywords_list:
            # Initialize the Google News client
            google_news = GNews(language='id', country="Indonesia", max_results=max_results)
            today = datetime.datetime.now().date()

            start_date = (today - datetime.timedelta(days=day_range))
            end_date = today
            google_news.start_date = start_date
            google_news.end_date = end_date

            # Get news articles based on keywords
            get_news = google_news.get_news(keywords)

            # Parse the article data into a DataFrame
            articles_df = pd.DataFrame(get_news)

            # Check if the necessary columns are present in the DataFrame
            column_names = ["publisher", "title", "description", "published date", "url"]
            if all(col in articles_df.columns for col in column_names):
                articles_df = articles_df[column_names]
            else:
                return None

            # Extract full text and image URLs of the articles
            articles = []
            images = []

            for url in articles_df["url"]:
                try:
                    # Download the article content and extract the text
                    get_article = Article(url)
                    get_article.download()
                    get_article.parse()
                    full_text = get_article.text

                    # Try to get the image URL and append it to the list
                    image = list(get_article.images)[0] if get_article.images else None
                    # image = get_article.top_image
                    images.append(image)

                    articles.append(full_text)

                except Exception as e:
                    # If there is an error, append an error message to the summary list and set the image URL to None
                    print(f"Error downloading article from {url}: {e}")
                    articles.append("Error: article download failed")
                    images.append(None)

                # Sleep for a short time to avoid being blocked by the website
                time.sleep(1)

            # Add the full text and image URL columns to the DataFrame
            articles_df["article_text"] = articles
            articles_df['image'] = images

            def count_words(text):
                words = text.split()
                return len(words)
            
            articles_df['word_count'] = articles_df['article_text'].apply(count_words)
            articles_df = articles_df[articles_df['word_count'] >= 2]
            articles_df = articles_df.drop(columns=['word_count'])
            
            articles_df["keywords"] = keywords

            # Concatenate the current dataframe with the previous ones
            concatenated_df = pd.concat([concatenated_df, articles_df], ignore_index=True)

        return concatenated_df

    except Exception as e:
        print(f"An error occurred while fetching articles: {e}")
        return None

# ----------------------------------------------------- ******************************** -----------------------------------------------------
def cleaning_articles(df: pd.DataFrame) -> pl.DataFrame:
    """
    Cleans and transforms a DataFrame containing news articles.

    This function performs the following cleaning and transformation tasks:
    - Removes newline characters and backslashes from the article text.
    - Renames columns.
    - Selects desired columns.
    - Converts published time to datetime.
    - Extracts the date from the published time.
    - Reorders columns.

    Parameters:
    - df (pd.DataFrame): The input DataFrame containing news articles.

    Returns:
    - pl.DataFrame: A cleaned and transformed Polars DataFrame.
    """
    try:
        # Clean the full text column
        df["article_text"] = df["article_text"].replace("\n", "", regex=True)
        df["article_text"] = df["article_text"].replace("\r", "", regex=True)
        df["article_text"] = df["article_text"].replace(r"\\", "", regex=True)

        # Rename columns and select desired columns for the final DataFrame
        df = df.rename(columns={"published date": "published_time"})
        df = df[["keywords", "publisher", "title", "article_text", "url", "published_time", "image"]]
        df["publisher"] = df["publisher"].apply(lambda x: x["title"])

        # Convert published time to datetime
        df["published_time"] = pd.to_datetime(df["published_time"])

        # Extract the date from the published time
        df["published_date"] = df["published_time"].dt.date

        # Reorder columns
        df = df[["keywords", "title", "article_text", "url", "image", "publisher", "published_time", "published_date"]]
        df = df[~(df["article_text"]=="Error: article download failed")]

        # Convert to a Polars DataFrame
        pl_df = pl.from_pandas(df)

        pl_df = pl_df.sort(by="published_time", descending=True)

        return pl_df

    except Exception as e:
        print(f"An error occurred while cleaning articles: {e}")
        return None

# ----------------------------------------------------- ******************************** -----------------------------------------------------
