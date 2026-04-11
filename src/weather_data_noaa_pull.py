import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv
import os


# CONFIG
load_dotenv()

TOKEN = os.getenv("NOAA_TOKEN")


stations = {
    "KDFW": "72259003927",
    "KIAH": "72243012960",
    "KSAT": "72253012921",
    "KELP": "72270023183",
    "KAMA": "72363023047",
    "KMAF": "72265023044"
}

import requests
import os

# Output folder
output_dir = "C:\\Renewable-PowerGrid-Risk\\data\\raw\\"
os.makedirs(output_dir, exist_ok=True)

# Station mapping (USAF+WBAN)
stations = {
    "KDFW": "72259003927",
    "KIAH": "72243012960",
    "KSAT": "72253012921",
    "KELP": "72270023183",
    "KAMA": "72363023047",
    "KMAF": "72265023044"
}

years = [2023, 2024, 2025]

base_url = "https://www.ncei.noaa.gov/data/global-hourly/access"

for station_name, station_id in stations.items():
    for year in years:
        url = f"{base_url}/{year}/{station_id}.csv"
        filename = f"{output_dir}/{station_name}_{year}.csv"

        print(f"Downloading {station_name} {year} ...")

        r = requests.get(url)

        if r.status_code == 200:
            with open(filename, "wb") as f:
                f.write(r.content)
            print(f"Saved: {filename}")
        else:
            print(f"Missing: {station_name} {year}")