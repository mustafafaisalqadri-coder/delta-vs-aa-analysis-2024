from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DELTA_NAVY = "#003366"


def load_cleaned_delta_data() -> pd.DataFrame:
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
    return delta_df[keep_columns]


def create_chart1_delayed_airports(delta_df: pd.DataFrame, out_path: Path) -> None:
    top_airports = (
        delta_df.groupby("Origin", as_index=False)["ArrDelay"]
        .mean()
        .sort_values("ArrDelay", ascending=False)
        .head(10)
    )

    plt.figure(figsize=(12, 7))
    bars = plt.bar(top_airports["Origin"], top_airports["ArrDelay"], color=DELTA_NAVY)
    plt.title("Delta Airlines - Most Delayed Departure Airports - Jan 2024", fontsize=14, pad=12)
    plt.xlabel("Origin Airport")
    plt.ylabel("Average Arrival Delay (minutes)")
    plt.grid(axis="y", linestyle="--", alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height:.1f}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


def create_chart2_delay_causes(delta_df: pd.DataFrame, out_path: Path) -> None:
    cause_columns = ["CarrierDelay", "WeatherDelay", "NASDelay", "LateAircraftDelay"]
    cause_totals = delta_df[cause_columns].fillna(0).sum()

    labels = ["CarrierDelay", "WeatherDelay", "NASDelay", "LateAircraftDelay"]
    colors = [DELTA_NAVY, "#4C78A8", "#72A0C1", "#A5C6DD"]

    plt.figure(figsize=(9, 9))
    plt.pie(
        cause_totals.values,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops={"edgecolor": "white", "linewidth": 1},
        textprops={"fontsize": 10},
    )
    plt.title("What's Causing Delta's Delays?", fontsize=14, pad=14)
    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


def create_chart3_busiest_routes(delta_df: pd.DataFrame, out_path: Path) -> None:
    routes = (delta_df["Origin"].astype(str) + " → " + delta_df["Dest"].astype(str)).rename("Route")
    top_routes = routes.value_counts().head(10)

    plt.figure(figsize=(13, 7))
    bars = plt.bar(top_routes.index, top_routes.values, color=DELTA_NAVY)
    plt.title("Delta's Busiest Routes - Jan 2024", fontsize=14, pad=12)
    plt.xlabel("Route")
    plt.ylabel("Number of Flights")
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.xticks(rotation=35, ha="right")

    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{int(height)}",
            ha="center",
            va="bottom",
            fontsize=9,
        )

    plt.tight_layout()
    plt.savefig(out_path, dpi=300, bbox_inches="tight")
    plt.close()


def main() -> None:
    project_dir = Path(__file__).parent
    delta_df = load_cleaned_delta_data()

    create_chart1_delayed_airports(delta_df, project_dir / "chart1_delayed_airports.png")
    create_chart2_delay_causes(delta_df, project_dir / "chart2_delay_causes.png")
    create_chart3_busiest_routes(delta_df, project_dir / "chart3_busiest_routes.png")

    print("All 3 charts saved!")


if __name__ == "__main__":
    main()
