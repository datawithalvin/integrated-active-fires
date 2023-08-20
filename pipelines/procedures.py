import polars as pl
import io
import requests as reqs
import datetime

from config import TOKEN
# ----------------------------------------------------- ******************************** -----------------------------------------------------
def fetch_viirs_data(today: str, day_range: str, token: str) -> pl.DataFrame:
    """
    Retrieves VIIRS active fires data from the NASA FIRMS API for a given date and range.

    Parameters:
    - today (str): The specific date for which the data is to be retrieved, in the format "YYYY-MM-DD".
    - day_range (str): The range of days for which the data is to be retrieved.
    - token (str): The token from FIRMS API.

    Returns:
    - pl.DataFrame: A Polars DataFrame containing the VIIRS data if successful, or None if an error occurred.

    Examples:
    >>> get_viirs_data("2023-08-19", "1")
    """

    try:
        host = "https://firms.modaps.eosdis.nasa.gov/api/country/csv/"
        source = "VIIRS_NOAA20_NRT/"
        country = "IDN/"

        url = (host + token + "/" + source + country + day_range + "/" + today)

        get_data = reqs.get(url)
        get_data.raise_for_status() # Raises an HTTPError if the HTTP request returned an unsuccessful status code

        csv_content = io.StringIO(get_data.text)
        viirs_df = pl.read_csv(csv_content)
        
        return viirs_df

    except reqs.RequestException as e:
        print(f"An error occurred while making the HTTP request: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None
    
# ----------------------------------------------------- ******************************** -----------------------------------------------------
# try to call the function
# today = str(datetime.date.today())
today = "2023-08-19"
day_range = "1"

viirs_df = fetch_viirs_data(today, day_range, TOKEN)

print(viirs_df)