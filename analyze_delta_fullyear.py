from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


DELTA_NAVY = "#003366"
MONTH_ORDER = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


def load_data() -> pd.DataFrame:
    project_dir = Path(__file__).parent
    file_path = project_dir / "delta_2024_full_year.csv"

    if not file_path.exists():
        raise FileNotFoundError(
            f"Could not find {file_path.name}. Run combine_data.py first."
        )

    df = pd.read_csv(file_path, low_memory=False)
    return df.dropna(subset=["ArrDelay"]).copy()


def print_stats(df: pd.DataFrame) -> None:
    total_flights = len(df)
    avg_delay = df["ArrDelay"].mean()

    monthly_avg = (
        df.groupby("MonthName", as_index=False)["ArrDelay"].mean().rename(columns={"ArrDelay": "AvgArrDelay"})
    )
    monthly_avg["MonthName"] = pd.Categorical(monthly_avg["MonthName"], categories=MONTH_ORDER, ordered=True)
    monthly_avg = monthly_avg.sort_values("MonthName")

    worst_row = monthly_avg.loc[monthly_avg["AvgArrDelay"].idxmax()]
    best_row = monthly_avg.loc[monthly_avg["AvgArrDelay"].idxmin()]

    print(f"Total Delta flights for full year 2024: {total_flights}")
    print(f"Average arrival delay for the full year: {avg_delay:.2f} minutes")
    print(
        f"Month with WORST average delay: {worst_row['MonthName']} "
        f"({worst_row['AvgArrDelay']:.2f} minutes)"
    )
    print(
        f"Month with BEST average delay: {best_row['MonthName']} "
        f"({best_row['AvgArrDelay']:.2f} minutes)"
    )


def chart_delayed_airports(df: pd.DataFrame, output_path: Path) -> None:
    top_airports = (
        df.groupby("Origin", as_index=False)["ArrDelay"]
        .mean()
        .sort_values("ArrDelay", ascending=False)
        .head(10)
    )

    plt.figure(figsize=(12, 7))
    bars = plt.bar(top_airports["Origin"], top_airports["ArrDelay"], color=DELTA_NAVY)
    plt.title("Delta Airlines - Most Delayed Airports - Full Year 2024", fontsize=14, pad=12)
    plt.xlabel("Origin Airport")
    plt.ylabel("Average Arrival Delay (minutes)")
    plt.grid(axis="y", linestyle="--", alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, f"{height:.1f}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def chart_delay_causes(df: pd.DataFrame, output_path: Path) -> None:
    cause_columns = ["CarrierDelay", "WeatherDelay", "NASDelay", "LateAircraftDelay"]
    cause_totals = df[cause_columns].fillna(0).sum()
    colors = [DELTA_NAVY, "#336699", "#5B84B1", "#88A9CC"]

    plt.figure(figsize=(9, 9))
    plt.pie(
        cause_totals.values,
        labels=cause_columns,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops={"edgecolor": "white", "linewidth": 1},
        textprops={"fontsize": 10},
    )
    plt.title("What's Causing Delta's Delays? - Full Year 2024", fontsize=14, pad=14)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def chart_busiest_routes(df: pd.DataFrame, output_path: Path) -> None:
    routes = (df["Origin"].astype(str) + " -> " + df["Dest"].astype(str)).rename("Route")
    top_routes = routes.value_counts().head(10)

    plt.figure(figsize=(13, 7))
    bars = plt.bar(top_routes.index, top_routes.values, color=DELTA_NAVY)
    plt.title("Delta's Busiest Routes - Full Year 2024", fontsize=14, pad=12)
    plt.xlabel("Route")
    plt.ylabel("Number of Flights")
    plt.xticks(rotation=35, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.3)

    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width() / 2, height, f"{int(height)}", ha="center", va="bottom", fontsize=9)

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def chart_monthly_trend(df: pd.DataFrame, output_path: Path) -> None:
    monthly_avg = df.groupby("MonthName", as_index=False)["ArrDelay"].mean()
    monthly_avg["MonthName"] = pd.Categorical(monthly_avg["MonthName"], categories=MONTH_ORDER, ordered=True)
    monthly_avg = monthly_avg.sort_values("MonthName")

    plt.figure(figsize=(12, 6))
    plt.plot(monthly_avg["MonthName"], monthly_avg["ArrDelay"], color=DELTA_NAVY, marker="o", linewidth=2)
    plt.title("Delta's Average Delay by Month - 2024", fontsize=14, pad=12)
    plt.xlabel("Month")
    plt.ylabel("Average Arrival Delay (minutes)")
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.xticks(rotation=35, ha="right")

    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def main() -> None:
    project_dir = Path(__file__).parent
    df = load_data()

    print_stats(df)

    chart_delayed_airports(df, project_dir / "chart1_delayed_airports_fullyear.png")
    chart_delay_causes(df, project_dir / "chart2_delay_causes_fullyear.png")
    chart_busiest_routes(df, project_dir / "chart3_busiest_routes_fullyear.png")
    chart_monthly_trend(df, project_dir / "chart4_monthly_trend.png")

    print("All charts saved!")


if __name__ == "__main__":
    main()
