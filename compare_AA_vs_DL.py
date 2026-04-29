from pathlib import Path
from typing import Union

import matplotlib.pyplot as plt
import pandas as pd


DELTA_COLOR = "#003366"
AA_COLOR = "#CC0000"
MONTH_ORDER = list(range(1, 13))
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
CAUSE_COLUMNS = ["CarrierDelay", "WeatherDelay", "NASDelay", "LateAircraftDelay"]


def load_data() -> pd.DataFrame:
    project_dir = Path(__file__).parent
    input_path = project_dir / "AA_vs_DL_2024_master.csv"

    if not input_path.exists():
        raise FileNotFoundError(f"Missing input file: {input_path.name}")

    df = pd.read_csv(input_path, low_memory=False)
    return df.dropna(subset=["ArrDelay"]).copy()


def compute_airline_stats(df: pd.DataFrame, airline_code: str) -> dict[str, Union[float, str, int]]:
    airline_df = df[df["Reporting_Airline"] == airline_code].copy()
    total_flights = len(airline_df)
    avg_arr_delay = airline_df["ArrDelay"].mean()
    pct_delayed_over_15 = (airline_df["ArrDelay"] > 15).mean() * 100
    pct_cancelled = airline_df["Cancelled"].fillna(0).mean() * 100

    cause_sums = airline_df[CAUSE_COLUMNS].fillna(0).sum()
    all_causes_total = cause_sums.sum()
    if all_causes_total > 0:
        pct_carrier = (cause_sums["CarrierDelay"] / all_causes_total) * 100
        pct_weather = (cause_sums["WeatherDelay"] / all_causes_total) * 100
    else:
        pct_carrier = 0.0
        pct_weather = 0.0

    month_avg = airline_df.groupby("Month", as_index=False)["ArrDelay"].mean()
    best_month_num = int(month_avg.loc[month_avg["ArrDelay"].idxmin(), "Month"])
    worst_month_num = int(month_avg.loc[month_avg["ArrDelay"].idxmax(), "Month"])

    return {
        "Total flights": total_flights,
        "Average arrival delay (minutes)": round(avg_arr_delay, 2),
        "% flights delayed > 15 min": round(pct_delayed_over_15, 2),
        "% delays caused by Carrier": round(pct_carrier, 2),
        "% delays caused by Weather": round(pct_weather, 2),
        "% flights Cancelled": round(pct_cancelled, 2),
        "Best month (lowest avg delay)": MONTH_NAMES[best_month_num],
        "Worst month (highest avg delay)": MONTH_NAMES[worst_month_num],
    }


def print_comparison_table(df: pd.DataFrame) -> None:
    delta_stats = compute_airline_stats(df, "DL")
    aa_stats = compute_airline_stats(df, "AA")
    comparison_df = pd.DataFrame({"Delta Airlines": delta_stats, "American Airlines": aa_stats})
    print("AA vs DL 2024 comparison:")
    print(comparison_df)


def chart1_avg_monthly_delay(df: pd.DataFrame, output_path: Path) -> None:
    monthly_avg = (
        df.groupby(["Month", "Reporting_Airline"], as_index=False)["ArrDelay"].mean()
        .pivot(index="Month", columns="Reporting_Airline", values="ArrDelay")
        .reindex(MONTH_ORDER)
    )
    monthly_avg = monthly_avg.rename(columns={"DL": "Delta", "AA": "American"})

    x = range(len(monthly_avg.index))
    width = 0.38

    plt.figure(figsize=(14, 7))
    plt.bar([i - width / 2 for i in x], monthly_avg["Delta"], width=width, color=DELTA_COLOR, label="Delta")
    plt.bar([i + width / 2 for i in x], monthly_avg["American"], width=width, color=AA_COLOR, label="American")
    plt.title("Delta vs American Airlines - Average Monthly Delay 2024", fontsize=14, pad=12)
    plt.xlabel("Month")
    plt.ylabel("Average Arrival Delay (minutes)")
    plt.xticks(list(x), [MONTH_NAMES[m] for m in monthly_avg.index], rotation=30, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def chart2_delay_cause_breakdown(df: pd.DataFrame, output_path: Path) -> None:
    airline_cause_avg = df.groupby("Reporting_Airline")[CAUSE_COLUMNS].mean()
    delta_vals = airline_cause_avg.loc["DL", CAUSE_COLUMNS].values
    aa_vals = airline_cause_avg.loc["AA", CAUSE_COLUMNS].values

    x = range(len(CAUSE_COLUMNS))
    width = 0.38

    plt.figure(figsize=(12, 7))
    plt.bar([i - width / 2 for i in x], delta_vals, width=width, color=DELTA_COLOR, label="Delta")
    plt.bar([i + width / 2 for i in x], aa_vals, width=width, color=AA_COLOR, label="American")
    plt.title("What's Causing Delays - Delta vs AA 2024", fontsize=14, pad=12)
    plt.xlabel("Delay Cause")
    plt.ylabel("Average Delay Minutes per Flight")
    plt.xticks(list(x), CAUSE_COLUMNS, rotation=20, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def chart3_cancellation_rate_by_month(df: pd.DataFrame, output_path: Path) -> None:
    monthly_cancel = (
        df.groupby(["Month", "Reporting_Airline"], as_index=False)["Cancelled"].mean()
        .pivot(index="Month", columns="Reporting_Airline", values="Cancelled")
        .reindex(MONTH_ORDER)
        * 100
    )
    monthly_cancel = monthly_cancel.rename(columns={"DL": "Delta", "AA": "American"})

    x = range(len(monthly_cancel.index))
    width = 0.38

    plt.figure(figsize=(14, 7))
    plt.bar([i - width / 2 for i in x], monthly_cancel["Delta"], width=width, color=DELTA_COLOR, label="Delta")
    plt.bar([i + width / 2 for i in x], monthly_cancel["American"], width=width, color=AA_COLOR, label="American")
    plt.title("Cancellation Rate by Month - Delta vs AA 2024", fontsize=14, pad=12)
    plt.xlabel("Month")
    plt.ylabel("Cancellation Rate (%)")
    plt.xticks(list(x), [MONTH_NAMES[m] for m in monthly_cancel.index], rotation=30, ha="right")
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def chart4_hub_performance(df: pd.DataFrame, output_path: Path) -> None:
    hubs = ["ATL", "DFW", "LAX", "JFK", "LGA"]
    hub_df = df[df["Origin"].isin(hubs)].copy()
    hub_avg = (
        hub_df.groupby(["Origin", "Reporting_Airline"], as_index=False)["ArrDelay"].mean()
        .pivot(index="Origin", columns="Reporting_Airline", values="ArrDelay")
        .reindex(hubs)
    )
    hub_avg = hub_avg.rename(columns={"DL": "Delta", "AA": "American"}).fillna(0)

    x = range(len(hub_avg.index))
    width = 0.38

    plt.figure(figsize=(11, 7))
    plt.bar([i - width / 2 for i in x], hub_avg["Delta"], width=width, color=DELTA_COLOR, label="Delta")
    plt.bar([i + width / 2 for i in x], hub_avg["American"], width=width, color=AA_COLOR, label="American")
    plt.title("Hub Performance - Delta vs AA 2024", fontsize=14, pad=12)
    plt.xlabel("Airport")
    plt.ylabel("Average Arrival Delay (minutes)")
    plt.xticks(list(x), hub_avg.index)
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def chart5_controlled_vs_uncontrolled(df: pd.DataFrame, output_path: Path) -> None:
    airline_cause_sum = df.groupby("Reporting_Airline")[CAUSE_COLUMNS].sum()
    controllable = airline_cause_sum["CarrierDelay"] + airline_cause_sum["LateAircraftDelay"]
    uncontrollable = airline_cause_sum["WeatherDelay"] + airline_cause_sum["NASDelay"]
    total = controllable + uncontrollable

    controllable_pct = (controllable / total * 100).fillna(0)
    uncontrollable_pct = (uncontrollable / total * 100).fillna(0)

    labels = ["Delta", "American"]
    x = range(len(labels))
    controlled_vals = [controllable_pct["DL"], controllable_pct["AA"]]
    uncontrolled_vals = [uncontrollable_pct["DL"], uncontrollable_pct["AA"]]

    plt.figure(figsize=(9, 7))
    plt.bar(x, controlled_vals, color=DELTA_COLOR, label="Controllable (Carrier + LateAircraft)")
    plt.bar(x, uncontrolled_vals, bottom=controlled_vals, color=AA_COLOR, label="Uncontrollable (Weather + NAS)")
    plt.title("Controllable vs Uncontrollable Delays - Delta vs AA 2024", fontsize=14, pad=12)
    plt.xlabel("Airline")
    plt.ylabel("Share of Delay Causes (%)")
    plt.xticks(list(x), labels)
    plt.ylim(0, 100)
    plt.grid(axis="y", linestyle="--", alpha=0.3)
    plt.legend()
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()


def main() -> None:
    project_dir = Path(__file__).parent
    df = load_data()

    print_comparison_table(df)

    chart1_avg_monthly_delay(df, project_dir / "compare_chart1_avg_delay.png")
    chart2_delay_cause_breakdown(df, project_dir / "compare_chart2_delay_causes.png")
    chart3_cancellation_rate_by_month(df, project_dir / "compare_chart3_cancellations.png")
    chart4_hub_performance(df, project_dir / "compare_chart4_hubs.png")
    chart5_controlled_vs_uncontrolled(df, project_dir / "compare_chart5_controlled_vs_uncontrolled.png")

    print("All comparison charts saved!")


if __name__ == "__main__":
    main()
