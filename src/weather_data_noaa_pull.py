import requests
import pandas as pd
from datetime import datetime, timedelta
import time
from dotenv import load_dotenv
import os


# CONFIG
load_dotenv()

TOKEN = os.getenv("NOAA_TOKEN")


import os
import requests
import pandas as pd
import numpy as np
from io import StringIO

# -----------------------------
# Station IDs (USAF + WBAN)
# -----------------------------
stations = {
    "KDFW": "72259003927",
    "KIAH": "72243012960",
    "KSAT": "72253012921",
    "KLBB": "72267023042",
    "KAMA": "72363023047",
    "KABI": "72266013962",
}

years = [2023, 2024, 2025]

base_url = "https://www.ncei.noaa.gov/data/global-hourly/access"

output_dir = "weather_clean"
os.makedirs(output_dir, exist_ok=True)


# -----------------------------
# NOAA Parser
# -----------------------------


def parse_noaa(df):

    # ---- temperature ----
    tmp = df["TMP"].str.split(",", expand=True)
    df["temp_c"] = pd.to_numeric(tmp[0], errors="coerce") / 10.0

    # ---- wind ----
    wnd = df["WND"].str.split(",", expand=True)
    df["wind_dir_deg"] = pd.to_numeric(wnd[0], errors="coerce")
    df["wind_speed_mps"] = pd.to_numeric(wnd[3], errors="coerce") / 10.0

    # ---- cloud cover (GF1) ----
    if "GF1" in df.columns:
        gf = df["GF1"].str.split(",", expand=True)
        df["cloud_okta"] = pd.to_numeric(gf[0], errors="coerce")
        df["cloud_fraction"] = df["cloud_okta"] / 8.0  # 0-1 scale
    else:
        df["cloud_fraction"] = np.nan

    # clean bad values
    df.loc[df["temp_c"] > 60, "temp_c"] = np.nan
    df.loc[df["temp_c"] < -60, "temp_c"] = np.nan
    df.loc[df["wind_speed_mps"] > 75, "wind_speed_mps"] = np.nan
    df.loc[df["cloud_fraction"] > 1, "cloud_fraction"] = np.nan

    return df


# -----------------------------
# Download + Process
# -----------------------------
for station_name, station_id in stations.items():

    print(f"\nProcessing {station_name}")

    all_years = []

    for year in years:

        url = f"{base_url}/{year}/{station_id}.csv"
        print("Downloading:", url)

        r = requests.get(url)

        if r.status_code != 200:
            print("Missing:", year)
            continue

        df = pd.read_csv(StringIO(r.text))

        all_years.append(df)

    # merge years
    df = pd.concat(all_years)

    # parse date
    df["DATE"] = pd.to_datetime(df["DATE"])
    df = df.set_index("DATE")

    # parse TMP/WND
    df = parse_noaa(df)

    # keep only useful columns
    df = df[["temp_c", "wind_speed_mps", "wind_dir_deg", "cloud_fraction"]]

    # resample hourly
    df_hourly = df.resample("1H").mean()

    # save
    outfile = f"{output_dir}/{station_name}_hourly_2023_2025.csv"
    df_hourly.to_csv(outfile)

    print("Saved:", outfile)


print("\nDone.")
