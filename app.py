from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st


DELTA_COLOR = "#003366"
AA_COLOR = "#CC0000"
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


@st.cache_data
def load_data() -> pd.DataFrame:
    csv_path = Path(__file__).parent / "AA_vs_DL_2024_master.csv"
    if not csv_path.exists():
        raise FileNotFoundError("AA_vs_DL_2024_master.csv not found in project folder.")
    df = pd.read_csv(csv_path, low_memory=False)
    df["Month"] = pd.to_numeric(df["Month"], errors="coerce")
    df["MonthName"] = df["Month"].map(MONTH_NAMES)
    return df


def apply_filters(df: pd.DataFrame, airline_filter: str, month_filter: str) -> pd.DataFrame:
    filtered = df.copy()

    if airline_filter == "Delta only":
        filtered = filtered[filtered["Reporting_Airline"] == "DL"]
    elif airline_filter == "AA only":
        filtered = filtered[filtered["Reporting_Airline"] == "AA"]

    if month_filter != "All months":
        month_num = {v: k for k, v in MONTH_NAMES.items()}[month_filter]
        filtered = filtered[filtered["Month"] == month_num]

    return filtered


def main() -> None:
    st.set_page_config(page_title="Delta vs AA Dashboard", layout="wide")
    st.title("Delta vs American Airlines - 2024 Flight Performance Dashboard")
    st.markdown(
        "### Analysis of 900,000+ real flights from US Bureau of Transportation Statistics"
    )

    df = load_data()

    st.sidebar.header("Filters")
    airline_filter = st.sidebar.selectbox(
        "Select Airline",
        ["Both", "Delta only", "AA only"],
    )
    month_filter = st.sidebar.selectbox(
        "Select Month",
        ["All months"] + [MONTH_NAMES[m] for m in range(1, 13)],
    )

    filtered_df = apply_filters(df, airline_filter, month_filter)
    filtered_non_null_delay = filtered_df.dropna(subset=["ArrDelay"])

    total_flights = len(filtered_df)
    delta_filtered = filtered_non_null_delay[
        filtered_non_null_delay["Reporting_Airline"] == "DL"
    ]
    aa_filtered = filtered_non_null_delay[
        filtered_non_null_delay["Reporting_Airline"] == "AA"
    ]
    delta_avg_delay = delta_filtered["ArrDelay"].mean() if not delta_filtered.empty else None
    aa_avg_delay = aa_filtered["ArrDelay"].mean() if not aa_filtered.empty else None

    cause_cols = ["CarrierDelay", "WeatherDelay", "NASDelay", "LateAircraftDelay"]
    cause_totals = filtered_non_null_delay[cause_cols].fillna(0).sum()
    total_causes = cause_totals.sum()
    weather_pct = (cause_totals["WeatherDelay"] / total_causes * 100) if total_causes > 0 else 0.0

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Flights Analyzed", f"{total_flights:,}")
    c2.metric(
        "Delta Average Delay (minutes)",
        f"{delta_avg_delay:.2f}" if delta_avg_delay is not None else "N/A",
    )
    c3.metric(
        "AA Average Delay (minutes)",
        f"{aa_avg_delay:.2f}" if aa_avg_delay is not None else "N/A",
    )
    c4.metric("Weather causes only X% of delays", f"{weather_pct:.1f}%")

    st.markdown("---")

    # Chart 1: Average delay by month line chart
    st.subheader("Average Delay by Month")
    month_order_df = pd.DataFrame({"Month": list(range(1, 13)), "MonthName": [MONTH_NAMES[m] for m in range(1, 13)]})
    monthly_delay = (
        filtered_non_null_delay.groupby(["Month", "Reporting_Airline"], as_index=False)["ArrDelay"]
        .mean()
        .merge(month_order_df, on="Month", how="right")
    )

    fig1, ax1 = plt.subplots(figsize=(10, 4))
    fig1.patch.set_facecolor("white")
    ax1.set_facecolor("white")
    if airline_filter in ("Both", "Delta only"):
        delta_line = monthly_delay[monthly_delay["Reporting_Airline"] == "DL"].sort_values("Month")
        ax1.plot(delta_line["MonthName"], delta_line["ArrDelay"], marker="o", color=DELTA_COLOR, label="Delta")
    if airline_filter in ("Both", "AA only"):
        aa_line = monthly_delay[monthly_delay["Reporting_Airline"] == "AA"].sort_values("Month")
        ax1.plot(aa_line["MonthName"], aa_line["ArrDelay"], marker="o", color=AA_COLOR, label="American")
    ax1.set_ylabel("Average ArrDelay (minutes)")
    ax1.tick_params(axis="x", rotation=35)
    ax1.grid(axis="y", linestyle="--", alpha=0.3)
    ax1.legend()
    st.pyplot(fig1)

    # Chart 2: Delay causes pie charts (Delta vs AA)
    st.subheader("Delay Causes")
    fig2, (ax2_delta, ax2_aa) = plt.subplots(1, 2, figsize=(12, 6))
    fig2.patch.set_facecolor("white")
    ax2_delta.set_facecolor("white")
    ax2_aa.set_facecolor("white")
    pie_colors = [DELTA_COLOR, AA_COLOR, "#4477AA", "#AA4444"]
    delta_cause_totals = delta_filtered[cause_cols].fillna(0).sum()
    aa_cause_totals = aa_filtered[cause_cols].fillna(0).sum()

    if delta_cause_totals.sum() > 0:
        ax2_delta.pie(
            delta_cause_totals.values,
            labels=cause_cols,
            autopct="%1.1f%%",
            startangle=130,
            colors=pie_colors,
            wedgeprops={"edgecolor": "white"},
        )
        ax2_delta.set_title("Delta Delay Causes")
    else:
        ax2_delta.text(0.5, 0.5, "No Delta data", ha="center", va="center")
        ax2_delta.set_title("Delta Delay Causes")

    if aa_cause_totals.sum() > 0:
        ax2_aa.pie(
            aa_cause_totals.values,
            labels=cause_cols,
            autopct="%1.1f%%",
            startangle=130,
            colors=pie_colors,
            wedgeprops={"edgecolor": "white"},
        )
        ax2_aa.set_title("AA Delay Causes")
    else:
        ax2_aa.text(0.5, 0.5, "No AA data", ha="center", va="center")
        ax2_aa.set_title("AA Delay Causes")

    st.pyplot(fig2)
    st.markdown(
        "<p style='font-size:22px; font-weight:700;'>"
        "79.8% of all delays in 2024 were controllable by the airline. "
        "Only 5.1% were weather-related."
        "</p>",
        unsafe_allow_html=True,
    )

    # Chart 3: Top 10 delayed airports bar chart
    st.subheader("Top 10 Delayed Airports (Origin)")
    top_airports = (
        filtered_non_null_delay.groupby("Origin", as_index=False)["ArrDelay"]
        .mean()
        .sort_values("ArrDelay", ascending=False)
        .head(10)
    )
    fig3, ax3 = plt.subplots(figsize=(10, 4))
    fig3.patch.set_facecolor("white")
    ax3.set_facecolor("white")
    if airline_filter == "AA only":
        bar_color = AA_COLOR
    else:
        bar_color = DELTA_COLOR
    ax3.bar(top_airports["Origin"], top_airports["ArrDelay"], color=bar_color)
    ax3.set_ylabel("Average ArrDelay (minutes)")
    ax3.grid(axis="y", linestyle="--", alpha=0.3)
    st.pyplot(fig3)


if __name__ == "__main__":
    main()
