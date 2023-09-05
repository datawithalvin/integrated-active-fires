# import libraries
import polars as pl

from src.procedures import fetch_air_quality_data, cleaning_aqms_data
from dotenv import dotenv_values

config = dotenv_values("./.env")

# ------------------------------****************--------------------------------------#
def main():
    """
    Fetches air quality data, cleans it, and appends the cleaned data to the database.

    This function fetches air quality data from an API, cleans the data,
    and appends the cleaned data to a database table.
    """
    try:
        # Fetch air quality data and clean it
        aqms_pl = fetch_air_quality_data()
        if aqms_pl is None:
            print("Failed to fetch air quality data.")
            return
        aqms_pl = cleaning_aqms_data(aqms_pl)
        if aqms_pl is None:
            print("Failed to clean air quality data.")
            return

        # Append the cleaned data to the database
        CONNECTION_URI = config.get("CONNECTION_URI")
        aqms_pl.write_database(table_name="air_quality_idn", connection=CONNECTION_URI, if_exists="append")

        with pl.Config(tbl_cols=10):
            print(aqms_pl)

    except Exception as e:
        print(f"An error occurred in the main pipeline: {e}")


# ------------------------------****************--------------------------------------#
if __name__ == "__main__":
    main()
