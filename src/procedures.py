import polars as pl
import pandas as pd
import io
import requests as reqs
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

    except reqs.RequestException as e:
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


# ----------------------------------------------------- ******************************** -----------------------------------------------------


# ----------------------------------------------------- ******************************** -----------------------------------------------------
