import tempfile
import zipfile
from pathlib import Path

import pandas as pd


KEEP_COLUMNS = [
    "Year",
    "Month",
    "Reporting_Airline",
    "Origin",
    "Dest",
    "ArrDelay",
    "CarrierDelay",
    "WeatherDelay",
    "NASDelay",
    "LateAircraftDelay",
    "Cancelled",
]

AIRLINE_NAME_MAP = {
    "DL": "Delta Airlines",
    "AA": "American Airlines",
}


def read_csv_from_zip(zip_path: Path, extract_dir: Path) -> pd.DataFrame:
    with zipfile.ZipFile(zip_path, "r") as zip_ref:
        zip_ref.extractall(extract_dir)
        csv_files = [name for name in zip_ref.namelist() if name.lower().endswith(".csv")]

    if not csv_files:
        raise FileNotFoundError(f"No CSV found inside {zip_path.name}")

    csv_path = extract_dir / csv_files[0]
    return pd.read_csv(csv_path, low_memory=False)


def main() -> None:
    project_dir = Path(__file__).parent
    monthly_frames: list[pd.DataFrame] = []

    with tempfile.TemporaryDirectory() as temp_root:
        temp_root_path = Path(temp_root)

        for month in range(1, 13):
            zip_path = project_dir / f"flight_data_2024_{month}.zip"
            if not zip_path.exists():
                raise FileNotFoundError(f"Missing file: {zip_path.name}")

            month_extract_dir = temp_root_path / f"month_{month}"
            month_extract_dir.mkdir(parents=True, exist_ok=True)

            month_df = read_csv_from_zip(zip_path, month_extract_dir)
            month_df = month_df[month_df["Reporting_Airline"].isin(["DL", "AA"])].copy()
            month_df = month_df[KEEP_COLUMNS]
            month_df["Airline_Name"] = month_df["Reporting_Airline"].map(AIRLINE_NAME_MAP)

            monthly_frames.append(month_df)

    combined_df = pd.concat(monthly_frames, ignore_index=True)

    output_path = project_dir / "AA_vs_DL_2024_master.csv"
    combined_df.to_csv(output_path, index=False)

    delta_count = int((combined_df["Reporting_Airline"] == "DL").sum())
    american_count = int((combined_df["Reporting_Airline"] == "AA").sum())
    total_count = len(combined_df)

    print("Dataset complete!")
    print(f"Total Delta flights: {delta_count}")
    print(f"Total American Airlines flights: {american_count}")
    print(f"Combined total: {total_count}")


if __name__ == "__main__":
    main()
