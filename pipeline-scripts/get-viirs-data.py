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

from src.procedures import fetch_viirs_data
from dotenv import dotenv_values

config = dotenv_values("./.env")
# ------------------------------****************--------------------------------------#

def main():
    """Main function to execute the processing pipeline"""
    # # Build connection
    # connection = connect_to_db("election")

    token = config.get("TOKEN")
    today = datetime.date.today()
    yesterday = str(today - datetime.timedelta(days=1))
    day_range = "1"

    viirs_data = fetch_viirs_data(today=yesterday, day_range=day_range, token=token)
    print(viirs_data)
    print(token)

# ------------------------------****************--------------------------------------#
if __name__ == "__main__":
    main()