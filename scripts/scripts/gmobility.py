import os
import pandas as pd
from datetime import datetime

URL = "https://www.gstatic.com/covid19/mobility/Global_Mobility_Report.csv"

CURRENT_DIR = os.path.dirname(__file__)
INPUT_PATH = os.path.join(CURRENT_DIR, "../input/gmobility/")
OUTPUT_PATH = os.path.join(CURRENT_DIR, '../../public/data/gmobility/')
CSV_PATH = os.path.join(INPUT_PATH, 'latest.csv')

def download_csv():
    os.system('curl --silent -f -o %(CSV_PATH)s -L %(URL)s' % {
        'CSV_PATH': CSV_PATH,
        'URL': URL
    })

def export_grapher():

    cols = [
        "country_region",
        "sub_region_1",
        "sub_region_2",
        "metro_area",
        "iso_3166_2_code",
        "census_fips_code",
        "date",
        "retail_and_recreation_percent_change_from_baseline",
        "grocery_and_pharmacy_percent_change_from_baseline",
        "parks_percent_change_from_baseline",
        "transit_stations_percent_change_from_baseline",
        "workplaces_percent_change_from_baseline",
        "residential_percent_change_from_baseline"
    ]

    df = pd.read_csv(CSV_PATH, usecols=cols)

    # Convert date column to days of the year
    df['date'] = pd.to_datetime(df['date'], format="%Y/%m/%d", utc=True)
    df['date'] = df['date'].dt.dayofyear

    # Standardise country names to OWID country names
    country_mapping = pd.read_csv(os.path.join(INPUT_PATH, "gmobility_country_standardized.csv"))
    df = country_mapping.merge(df, on="country_region")

    # Remove subnational data, keeping only country figures
    filter_cols = ["sub_region_1", "sub_region_2", "metro_area", "iso_3166_2_code", "census_fips_code"]
    country_mobility = df[df[filter_cols].isna().all(1)]

    # Delete columns
    country_mobility = country_mobility.drop(columns=["country_region", "sub_region_1", "sub_region_2", "metro_area", "census_fips_code", "iso_3166_2_code"])

    # Assign new column names
    rename_dict = {
        "date": "Year",
        "retail_and_recreation_percent_change_from_baseline": "Retail & Recreation",
        "grocery_and_pharmacy_percent_change_from_baseline": "Grocery & Pharmacy",
        "parks_percent_change_from_baseline": "Parks",
        "transit_stations_percent_change_from_baseline": "Transit Stations",
        "workplaces_percent_change_from_baseline": "Workplaces",
        "residential_percent_change_from_baseline": "Residential"
    }

    # Rename columns
    country_mobility = country_mobility.rename(columns=rename_dict)

    # Save to files
    os.system('mkdir -p %s' % os.path.abspath(OUTPUT_PATH))
    country_mobility.to_csv(os.path.join(OUTPUT_PATH, 'Google Mobility Trends (2020).csv'), index=False)

if __name__ == '__main__':
    download_csv()
    export_grapher()
