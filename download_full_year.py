import time
from pathlib import Path
from urllib.request import urlretrieve


MONTH_NAMES = {
    1: "January",
    2: "February",
    3: "March",
    4: "April",
    5: "May",
    6: "June",
    7: "July",
    8: "August",
    9: "September",
    10: "October",
    11: "November",
    12: "December",
}


def main() -> None:
    base_url = (
        "https://transtats.bts.gov/PREZIP/"
        "On_Time_Reporting_Carrier_On_Time_Performance_1987_present_2024_{month}.zip"
    )
    project_dir = Path(__file__).parent

    for month in range(1, 13):
        month_name = MONTH_NAMES[month]
        download_url = base_url.format(month=month)
        output_file = project_dir / f"flight_data_2024_{month}.zip"

        print(f"Downloading {month_name} 2024...", end=" ", flush=True)
        urlretrieve(download_url, output_file)
        print("done")

        if month < 12:
            time.sleep(2)

    print("All 12 months downloaded!")


if __name__ == "__main__":
    main()
