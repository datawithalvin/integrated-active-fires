# import libraries
import polars as pl
import pandas as pd
import datetime
import requests

from src.procedures import fetch_viirs_data, fetch_last_data, cleaning_fetched_data
from dotenv import dotenv_values

config = dotenv_values("./.env")

# ------------------------------****************--------------------------------------#
def main():
    endpoint = "https://sipongi.menlhk.go.id/api/aqms"

    r = requests.get(endpoint, 
                     headers={'Accept': 'application/json'})

    aqms_json = r.json()

    aqms_df = pd.json_normalize(aqms_json["features"])

    # Select the desired columns
    columns_to_select = ["properties.alamat", "geometry.coordinates", "properties.kota", "properties.provinsi", "properties.val", "properties.nilai", "properties.cat"]
    aqms_df = aqms_df[columns_to_select]

    # Rename the columns
    aqms_df.columns = ["alamat", "coordinates", "kota", "provinsi", "val", "nilai", "cat"]

    # # print(aqms_json)
    # # print(f"Response: {r.json()}")

    # aqms_df = pl.read_json(aqms_json)

    print(aqms_df)


# ------------------------------****************--------------------------------------#
if __name__ == "__main__":
    main()
