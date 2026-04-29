import pandas as pd
import requests
import os

print("Starting data download...")

# This is the real BTS website link for 2024 flight data
url = "https://transtats.bts.gov/PREZIP/On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_1.zip"

# We'll save the file here
zip_filename = "flight_data.zip"

print("Downloading from US Government BTS website...")
print("This may take 1-2 minutes - the file is large!")

response = requests.get(url, stream=True)

with open(zip_filename, 'wb') as f:
    for chunk in response.iter_content(chunk_size=8192):
        f.write(chunk)

print("Download complete!")
print("File saved as: flight_data.zip")