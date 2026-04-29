import shutil
import tempfile
import zipfile
from pathlib import Path

import pandas as pd


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

KEEP_COLUMNS = [
    "Year",
    "Month",
    "MonthName",
    "Origin",
    "Dest",
    "ArrDelay",
    "CarrierDelay",
    "WeatherDelay",
    "NASDelay",
    "LateAircraftDelay",
    "Cancelled",
    "Reporting_Airline",
]


def read_csv_from_zip(zip_path: Path, temp_dir: Path) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(temp_dir)
        csv_files = [name for name in zip_ref.namelist() if name.lower().endswith(".csv")]

    if not csv_files:
        raise FileNotFoundError(f"No CSV found inside {zip_path.name}")

    csv_path = temp_dir / csv_files[0]
    return pd.read_csv(csv_path, low_memory=False)


def main() -> None:
    project_dir = Path(__file__).parent
    all_delta_months: list[pd.DataFrame] = []

    with tempfile.TemporaryDirectory() as temp_root:
        temp_root_path = Path(temp_root)

        for month in range(1, 13):
            month_name = MONTH_NAMES[month]
            zip_path = project_dir / f"flight_data_2024_{month}.zip"

            if not zip_path.exists():
                raise FileNotFoundError(f"Missing file: {zip_path.name}")

            month_temp_dir = temp_root_path / f"month_{month}"
            month_temp_dir.mkdir(parents=True, exist_ok=True)

            month_df = read_csv_from_zip(zip_path, month_temp_dir)
            month_df["MonthName"] = month_name

            month_df = month_df[month_df["Reporting_Airline"] == "DL"].copy()
            month_df = month_df[KEEP_COLUMNS]
            all_delta_months.append(month_df)

            print(f"{month_name} done - {len(month_df)} Delta flights added")

            shutil.rmtree(month_temp_dir, ignore_errors=True)

    full_year_df = pd.concat(all_delta_months, ignore_index=True)
    output_path = project_dir / "delta_2024_full_year.csv"
    full_year_df.to_csv(output_path, index=False)

    print(
        f"Master dataset created - {len(full_year_df)} total Delta flights saved to "
        f"{output_path.name}"
    )


if __name__ == "__main__":
    main()
