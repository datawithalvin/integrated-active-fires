# import libraries
import pandas as pd
import polars as pl
import io
import requests
import json
import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
import time

from src.config import TOKEN
from src.procedures import fetch_viirs_data


# # **************************** -------------------------------- ****************************
# token = "27c92ae57b057f905cf4c522a4cb7a15"
# host = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/"

# source = "VIIRS_SNPP_NRT"
# country = "IDN"
# today = "2023-08-31"
# day_range = "2"

# url = (host + token + "/" + source + "/" + country + "/" + day_range + "/" + today)
# # url1 = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/27c92ae57b057f905cf4c522a4cb7a15/VIIRS_SNPP_NRT/IDN/1/2023-08-31"

# print(url)
# # print(url1)
# get_data = requests.get(url)

# if get_data.status_code == 200:
#     csv_content = get_data.text
#     csv_content = io.StringIO(get_data.text)
#     viirs_df = pl.read_csv(csv_content, truncate_ragged_lines=True)
#     print(viirs_df)
# else:
#     print(f"Failed to fetch data, status code: {get_data.status_code}")


# token = TOKEN 
# today = "2023-08-31"
# day_range = "2"

# viirs_data = fetch_viirs_data(today=today, day_range=day_range, token=token)
# print(viirs_data)


# ------------------------------****************--------------------------------------#

def main():
    """Main function to execute the processing pipeline"""
    # # Build connection
    # connection = connect_to_db("election")

    token = TOKEN 
    today = datetime.date.today()
    yesterday = str(today - datetime.timedelta(days=1))
    day_range = "7"

    viirs_data = fetch_viirs_data(today=yesterday, day_range=day_range, token=token)
    print(viirs_data)
    # print(start_date)

# ------------------------------****************--------------------------------------#
if __name__ == "__main__":
    main()