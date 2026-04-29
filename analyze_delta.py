from pathlib import Path

import pandas as pd


def main() -> None:
    project_dir = Path(__file__).parent
    unzipped_dir = project_dir / "flight_data_unzipped"

    csv_files = sorted(unzipped_dir.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(
            f"No CSV file found in folder: {unzipped_dir}. "
            "Run explore_data.py first to unzip the dataset."
        )

    csv_path = csv_files[0]
    df = pd.read_csv(csv_path, low_memory=False)

    delta_df = df[df["Reporting_Airline"] == "DL"].copy()
    delta_df = delta_df.dropna(subset=["ArrDelay"])

    keep_columns = [
        "Year",
        "Month",
        "Origin",
        "Dest",
        "ArrDelay",
        "CarrierDelay",
        "WeatherDelay",
        "NASDelay",
        "LateAircraftDelay",
        "Cancelled",
    ]
    delta_df = delta_df[keep_columns]

    total_delta_flights = len(delta_df)
    avg_arr_delay = delta_df["ArrDelay"].mean()

    # Airport-level delay by average arrival delay, minimum 1 record by default.
    top_delayed_airports = (
        delta_df.groupby("Origin", as_index=False)["ArrDelay"]
        .mean()
        .sort_values("ArrDelay", ascending=False)
        .head(5)
    )

    print(f"Total Delta flights (with non-empty ArrDelay): {total_delta_flights}")
    print(f"Average Delta arrival delay (minutes): {avg_arr_delay:.2f}")
    print("\nTop 5 origin airports where Delta is most delayed:")
    print(top_delayed_airports.to_string(index=False))


if __name__ == "__main__":
    main()
