import polars as pl
import pandas as pd
import io
import requests
import datetime
import os
from supabase import create_client, Client

from dotenv import dotenv_values

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
def cleaning_fetched_data(df: pl.DataFrame) -> pl.DataFrame:
    """
    Cleans the newly fetched data by dropping unnecessary columns, adding a new column,
    and casting columns to align with the data types of the last fetched data from the database.

    Parameters:
    - df (pl.DataFrame): A Polars DataFrame containing the fetched data to be cleaned.

    Returns:
    - pl.DataFrame: A cleaned Polars DataFrame with aligned column data types.
    """

    try:
        # Add a new 'type' column with default value None
        df = df.with_columns(
            type=pl.lit(None)
        )

        # Select and cast specific columns to align with the desired data types
        df = df.select(
            pl.col("latitude").cast(pl.Float64),
            pl.col("longitude").cast(pl.Float64),
            pl.col("bright_ti4").cast(pl.Float32).alias("brightness"),
            pl.col("scan").cast(pl.Float32),
            pl.col("track").cast(pl.Float32),
            pl.col("acq_date").str.strptime(pl.Date, "%Y-%m-%d"),
            pl.col("acq_time").cast(pl.Int32),
            pl.col("satellite").cast(pl.Utf8),
            pl.col("instrument").cast(pl.Utf8),
            pl.col("confidence").cast(pl.Utf8),
            pl.col("version").cast(pl.Utf8),
            pl.col("bright_ti5").cast(pl.Float32).alias("bright_t31"),
            pl.col("frp").cast(pl.Float32),
            pl.col("daynight").cast(pl.Utf8),
            pl.col("type").cast(pl.Int32)
        )

        return df

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
