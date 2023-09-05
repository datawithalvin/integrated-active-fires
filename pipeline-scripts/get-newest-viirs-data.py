# import libraries
import polars as pl
import datetime

from src.procedures import fetch_viirs_data, fetch_last_data, cleaning_fetched_data
from dotenv import dotenv_values

config = dotenv_values("./.env")

# ------------------------------****************--------------------------------------#
def main():
    """
    Main function to execute the processing pipeline.

    This function retrieves VIIRS active fire data from the NASA FIRMS API,
    cleans the data, retrieves the most recently updated data from the database,
    concatenates both dataframes, removes duplicates, and appends the final dataframe
    into the database.
    """
    try:
        # Retrieves VIIRS active fire data from the NASA FIRMS API
        token = config.get("TOKEN")

        today = datetime.date.today()
        yesterday = str(today - datetime.timedelta(days=1))
        day_range = "2"

        viirs_data = fetch_viirs_data(today=yesterday, day_range=day_range, token=token)
        viirs_data = cleaning_fetched_data(viirs_data)  # Cleaning the dataframe

        # Retrieves the most recently updated data from the database
        CONNECTION_URI = config.get("CONNECTION_URI")
        query = """
            SELECT * 
            FROM viirs_snpp_raw 
            WHERE acq_date > CURRENT_DATE - INTERVAL '2 day'"""

        last_data = fetch_last_data(query=query, uri_connection=CONNECTION_URI)
        last_data = last_data.drop(["id"])  # Drop unused column to avoid conflicts when appending

        # Concatenate both dataframes, remove duplicates, and maintain order
        concat_viirs = pl.concat([last_data, viirs_data], how="vertical_relaxed")
        concat_viirs = concat_viirs.unique(keep="none", maintain_order=False)

        # Append the final dataframe into the database
        concat_viirs.write_database(table_name="viirs_snpp_raw", connection=CONNECTION_URI, if_exists="append")
        with pl.Config(tbl_cols=20):
            print(concat_viirs)
            print(viirs_data)

    except Exception as e:
        print(f"An error occurred in the main pipeline: {e}")

# ------------------------------****************--------------------------------------#
if __name__ == "__main__":
    main()
