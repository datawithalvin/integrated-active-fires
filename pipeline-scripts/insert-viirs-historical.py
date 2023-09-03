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

from src.config import TOKEN, SUPABASE_KEY, SUPABASE_URL

# **************************** -------------------------------- ****************************

hist_df = pl.read_csv("./data/viirs-yearly-summary/*.csv")
print(hist_df.columns)