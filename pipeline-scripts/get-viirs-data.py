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


# ------------------------------****************--------------------------------------#

def main():
    """Main function to execute the processing pipeline"""
    # # Build connection
    # connection = connect_to_db("election")

    token = TOKEN 
    today = datetime.date.today()
    yesterday = str(today - datetime.timedelta(days=1))
    day_range = "2"

    viirs_data = fetch_viirs_data(today=yesterday, day_range=day_range, token=token)
    print(viirs_data)
    # print(start_date)

# ------------------------------****************--------------------------------------#
if __name__ == "__main__":
    main()