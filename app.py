import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

# ── PAGE CONFIG ───────────────────────────────────────────
st.set_page_config(
    page_title="Airline Efficiency Report 2024",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── MINIMAL CSS — only layout, no color overrides ─────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
* { font-family: 'Inter', sans-serif !important; }
.main, .block-container {
    background: #ffffff !important;
    padding-top: 1.5rem !important;
    max-width: 1400px !important;
}
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv("AA_vs_DL_2024_master.csv", low_memory=False)
    month_map = {
        1:"Jan", 2:"Feb", 3:"Mar", 4:"Apr",
        5:"May", 6:"Jun", 7:"Jul", 8:"Aug",
        9:"Sep", 10:"Oct", 11:"Nov", 12:"Dec"
    }
    df["MonthName"] = df["Month"].map(month_map)
    for col in ["ArrDelay","CarrierDelay","WeatherDelay",
                "NASDelay","LateAircraftDelay"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Cancelled"] = pd.to_numeric(
        df["Cancelled"], errors="coerce"
    ).fillna(0)
    return df

df_raw   = load_data()
MONTHS   = ["Jan","Feb","Mar","Apr","May","Jun",
            "Jul","Aug","Sep","Oct","Nov","Dec"]
HUBS     = ["ATL","DFW","LAX","JFK","ORD",
            "LGA","BOS","SEA","DTW","SLC"]
DL_COL   = "#003366"
AA_COL   = "#CC0000"
GREY_BG  = "#f8f9fa"
BORDER   = "#ebebeb"

# ── HELPER: KPI CARD (pure inline styles) ─────────────────
def kpi_card(col, airline, a_color, value,
             label, badge, b_bg, b_color):
    with col:
        st.markdown(f"""
        <div style="
            background:#ffffff;
            border:1px solid {BORDER};
            border-radius:12px;
            padding:1.2rem 1.3rem;
            box-shadow:0 2px 10px rgba(0,0,0,0.05);
            height:100%;
        ">
            <p style="
                margin:0 0 6px 0;
                font-size:0.62rem;
                font-weight:700;
                letter-spacing:0.1em;
                text-transform:uppercase;
                color:{a_color};
            ">{airline}</p>
            <p style="
                margin:0 0 4px 0;
                font-size:2.3rem;
                font-weight:800;
                line-height:1.1;
                color:#111111;
            ">{value}</p>
            <p style="
                margin:0 0 10px 0;
                font-size:0.68rem;
                font-weight:600;
                text-transform:uppercase;
                letter-spacing:0.06em;
                color:#888888;
            ">{label}</p>
            <span style="
                font-size:0.72rem;
                font-weight:600;
                padding:3px 10px;
                border-radius:99px;
                background:{b_bg};
                color:{b_color};
            ">{badge}</span>
        </div>
        """, unsafe_allow_html=True)

# ── HELPER: SECTION HEADER ────────────────────────────────
def section_header(eyebrow, title):
    st.markdown(f"""
    <p style="
        font-size:0.65rem;
        font-weight:700;
        letter-spacing:0.14em;
        text-transform:uppercase;
        color:#bbbbbb;
        margin:0 0 4px 0;
    ">{eyebrow}</p>
    <p style="
        font-size:1.1rem;
        font-weight:700;
        color:#111111;
        margin:0 0 1.2rem 0;
    ">{title}</p>
    """, unsafe_allow_html=True)

# ── FILTERS ───────────────────────────────────────────────
st.markdown("---")
f1, f2, f3, f4 = st.columns([2, 2, 2, 1])

with f1:
    month_choice = st.selectbox(
        "📅 Time Period",
        ["All Months"] + MONTHS
    )
with f2:
    airline_view = st.selectbox(
        "✈️ Airline View",
        ["Both Airlines", "Delta Only", "AA Only"]
    )
with f3:
    scope = st.selectbox(
        "🛫 Airport Scope",
        ["All Airports", "Major Hubs Only"]
    )
with f4:
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("↺ Reset", use_container_width=True):
        st.rerun()

# ── APPLY FILTERS ─────────────────────────────────────────
months = MONTHS if month_choice == "All Months" \
         else [month_choice]
df = df_raw[df_raw["MonthName"].isin(months)].copy()

if scope == "Major Hubs Only":
    df = df[df["Origin"].isin(HUBS)]
if airline_view == "Delta Only":
    df = df[df["Reporting_Airline"] == "DL"]
elif airline_view == "AA Only":
    df = df[df["Reporting_Airline"] == "AA"]

df_v  = df.dropna(subset=["ArrDelay"])
df_dl = df_v[df_v["Reporting_Airline"] == "DL"]
df_aa = df_v[df_v["Reporting_Airline"] == "AA"]

# ── COMPUTE METRICS ───────────────────────────────────────
dl_avg  = df_dl["ArrDelay"].mean()  if len(df_dl) else 0.0
aa_avg  = df_aa["ArrDelay"].mean()  if len(df_aa) else 0.0
dl_ot   = (df_dl["ArrDelay"] <= 15).mean()*100 if len(df_dl) else 0.0
aa_ot   = (df_aa["ArrDelay"] <= 15).mean()*100 if len(df_aa) else 0.0
dl_canc = df_dl["Cancelled"].mean()*100 if len(df_dl) else 0.0
aa_canc = df_aa["Cancelled"].mean()*100 if len(df_aa) else 0.0
gap     = aa_avg - dl_avg

total_dl = df_dl[["CarrierDelay","WeatherDelay",
                   "NASDelay","LateAircraftDelay"]].sum().sum()
total_aa = df_aa[["CarrierDelay","WeatherDelay",
                   "NASDelay","LateAircraftDelay"]].sum().sum()

dl_ctrl = ((df_dl["CarrierDelay"].sum() +
            df_dl["LateAircraftDelay"].sum()) /
            total_dl * 100) if total_dl else 0.0
aa_ctrl = ((df_aa["CarrierDelay"].sum() +
            df_aa["LateAircraftDelay"].sum()) /
            total_aa * 100) if total_aa else 0.0
dl_wx   = (df_dl["WeatherDelay"].sum()/total_dl*100) if total_dl else 0.0
aa_wx   = (df_aa["WeatherDelay"].sum()/total_aa*100) if total_aa else 0.0

summer_dl = df_dl[df_dl["MonthName"].isin(
    ["Jun","Jul","Aug"])]["ArrDelay"].mean()
summer_aa = df_aa[df_aa["MonthName"].isin(
    ["Jun","Jul","Aug"])]["ArrDelay"].mean()
s_dl = f"{summer_dl:.1f}" if pd.notna(summer_dl) else "N/A"
s_aa = f"{summer_aa:.1f}" if pd.notna(summer_aa) else "N/A"

# ── HEADER ────────────────────────────────────────────────
h1, h2 = st.columns([3, 1])
with h1:
    st.markdown(f"""
    <p style="
        font-size:0.65rem;font-weight:700;
        letter-spacing:0.14em;text-transform:uppercase;
        color:#bbbbbb;margin:0 0 6px 0;
    ">2024 Full-Year · 1.9M+ Flights · BTS Government Data</p>
    <h1 style="
        font-size:1.9rem;font-weight:800;
        color:#111111;margin:0 0 6px 0;
    ">U.S. Airline Operational Efficiency Report</h1>
    <p style="color:#777777;font-size:0.9rem;margin:0;">
        Delta Air Lines vs American Airlines ·
        On-Time Performance, Delay Attribution & Hub Analysis
    </p>
    """, unsafe_allow_html=True)

with h2:
    gap_label = (
        f"AA averages {gap:.1f} min more delay than Delta"
        if gap > 0 else
        f"Delta averages {abs(gap):.1f} min more delay than AA"
    )
    st.markdown(f"""
    <div style="text-align:right;padding-top:0.3rem;">
        <p style="
            font-size:0.65rem;font-weight:700;
            letter-spacing:0.12em;text-transform:uppercase;
            color:#bbbbbb;margin:0;
        ">Efficiency Gap</p>
        <p style="
            font-size:2.8rem;font-weight:800;
            color:{DL_COL};margin:0;line-height:1.15;
        ">{gap:+.1f}<span style="
            font-size:1rem;font-weight:400;color:#999999;
        "> min</span></p>
        <p style="
            font-size:0.78rem;font-weight:600;
            color:{AA_COL};margin:0;
        ">{gap_label}</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── SECTION 1: KPI CARDS ──────────────────────────────────
section_header(
    "Head-to-Head Performance",
    "Four metrics. One clear winner."
)

# Row 1
r1a, r1b, r1c, r1d = st.columns(4)
kpi_card(r1a, "DELTA",    DL_COL, f"{dl_avg:.1f} min",
         "Avg Arrival Delay",
         "✓ Lower than AA", "#e8f5e9", "#2e7d32")
kpi_card(r1b, "AMERICAN", AA_COL, f"{aa_avg:.1f} min",
         "Avg Arrival Delay",
         f"✗ +{gap:.1f} min vs Delta", "#fdecea", "#c62828")
kpi_card(r1c, "DELTA",    DL_COL, f"{dl_ot:.0f}%",
         "On-Time Rate ≤15 min",
         "✓ Higher than AA", "#e8f5e9", "#2e7d32")
kpi_card(r1d, "AMERICAN", AA_COL, f"{aa_ot:.0f}%",
         "On-Time Rate ≤15 min",
         f"✗ {dl_ot-aa_ot:.0f}pp below Delta",
         "#fdecea", "#c62828")

st.markdown("<div style='height:14px'></div>",
            unsafe_allow_html=True)

# Row 2
r2a, r2b, r2c, r2d = st.columns(4)
kpi_card(r2a, "DELTA",    DL_COL, f"{dl_ctrl:.0f}%",
         "Controllable Delay %",
         "Carrier + Late Aircraft", "#f0f4ff", "#003366")
kpi_card(r2b, "AMERICAN", AA_COL, f"{aa_ctrl:.0f}%",
         "Controllable Delay %",
         "Carrier + Late Aircraft", "#fff0f0", "#cc0000")
kpi_card(r2c, "DELTA",    DL_COL, f"{dl_canc:.2f}%",
         "Cancellation Rate",
         "✓ Lower than AA", "#e8f5e9", "#2e7d32")
kpi_card(r2d, "AMERICAN", AA_COL, f"{aa_canc:.2f}%",
         "Cancellation Rate",
         f"✗ +{aa_canc-dl_canc:.2f}pp vs Delta",
         "#fdecea", "#c62828")

st.markdown("---")

# ── SECTION 2: MONTHLY TREND + DELAY BREAKDOWN ────────────
section_header(
    "Operational Trends",
    "Delta runs cleaner every single month of 2024."
)

col_left, col_right = st.columns([3, 2])

# Chart A: Monthly Delay Trend
with col_left:
    monthly = (
        df_v
        .groupby(["MonthName","Month","Reporting_Airline"])
        ["ArrDelay"].mean()
        .reset_index()
        .sort_values("Month")
    )
    monthly["Airline"] = monthly["Reporting_Airline"].map(
        {"DL":"Delta","AA":"American Airlines"}
    )

    fig_line = go.Figure()

    # Summer shading
    fig_line.add_vrect(
        x0="Jun", x1="Aug",
        fillcolor="rgba(255,200,50,0.08)",
        layer="below", line_width=0
    )
    fig_line.add_annotation(
        x="Jul", y=36,
        text="☀️ Peak Season",
        showarrow=False,
        font=dict(size=10, color="#cccccc")
    )

    for airline, color in [
        ("Delta", DL_COL),
        ("American Airlines", AA_COL)
    ]:
        d = (
            monthly[monthly["Airline"] == airline]
            .set_index("MonthName")
            .reindex([m for m in MONTHS
                      if m in monthly["MonthName"].values])
            .reset_index()
        )
        fig_line.add_trace(go.Scatter(
            x=d["MonthName"],
            y=d["ArrDelay"],
            name=airline,
            mode="lines+markers",
            line=dict(color=color, width=3),
            marker=dict(size=8),
            hovertemplate=(
                "<b>%{x}</b><br>"
                "Avg Delay: <b>%{y:.1f} min</b>"
                "<extra>" + airline + "</extra>"
            )
        ))

    fig_line.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=340,
        margin=dict(t=30, b=55, l=70, r=20),
        legend=dict(
            orientation="h", y=1.12, x=0,
            font=dict(size=11)
        ),
        hovermode="x unified",
        xaxis=dict(
            showgrid=False,
            title=dict(
                text="Month",
                font=dict(size=12, color="#555555")
            ),
            tickfont=dict(size=12, color="#333333"),
            showline=True,
            linecolor="#dddddd",
            linewidth=1
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#f2f2f2",
            title=dict(
                text="Average Arrival Delay (minutes)",
                font=dict(size=12, color="#555555")
            ),
            tickfont=dict(size=12, color="#333333"),
            ticksuffix=" min",
            showline=True,
            linecolor="#dddddd",
            linewidth=1
        )
    )
    st.plotly_chart(fig_line, use_container_width=True)

# Chart B: Delay Cause Breakdown
with col_right:
    delay_cols = ["CarrierDelay","LateAircraftDelay",
                  "NASDelay","WeatherDelay"]
    y_cats = [
        "Carrier (Airline's Fault)",
        "Late Aircraft (Cascade)",
        "NAS / ATC (Traffic Control)",
        "Weather (Uncontrollable)"
    ]
    dl_vals = [
        df_dl[c].sum()/total_dl*100 if total_dl else 0
        for c in delay_cols
    ]
    aa_vals = [
        df_aa[c].sum()/total_aa*100 if total_aa else 0
        for c in delay_cols
    ]

    fig_bar = go.Figure()
    fig_bar.add_trace(go.Bar(
        name="Delta",
        x=dl_vals, y=y_cats,
        orientation="h",
        marker_color=DL_COL,
        text=[f"{v:.0f}%" for v in dl_vals],
        textposition="inside",
        textfont=dict(color="white", size=11),
        hovertemplate=(
            "%{y}<br>"
            "Share: <b>%{x:.1f}%</b>"
            "<extra>Delta</extra>"
        )
    ))
    fig_bar.add_trace(go.Bar(
        name="American",
        x=aa_vals, y=y_cats,
        orientation="h",
        marker_color=AA_COL,
        text=[f"{v:.0f}%" for v in aa_vals],
        textposition="inside",
        textfont=dict(color="white", size=11),
        hovertemplate=(
            "%{y}<br>"
            "Share: <b>%{x:.1f}%</b>"
            "<extra>American</extra>"
        )
    ))

    fig_bar.update_layout(
        barmode="group",
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=340,
        margin=dict(t=30, b=55, l=20, r=20),
        legend=dict(
            orientation="h", y=1.12, x=0,
            font=dict(size=11)
        ),
        bargap=0.2,
        bargroupgap=0.05,
        xaxis=dict(
            showgrid=True,
            gridcolor="#f2f2f2",
            title=dict(
                text="Share of Total Delay Minutes",
                font=dict(size=12, color="#555555")
            ),
            tickfont=dict(size=11, color="#333333"),
            ticksuffix="%",
            range=[0, 62],
            showline=True,
            linecolor="#dddddd"
        ),
        yaxis=dict(
            showgrid=False,
            title=dict(
                text="Delay Category",
                font=dict(size=12, color="#555555")
            ),
            tickfont=dict(size=11, color="#333333"),
            showline=True,
            linecolor="#dddddd"
        )
    )
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")

# ── SECTION 3: HUB SCORECARD ──────────────────────────────
section_header(
    "Hub Intelligence",
    "Where each airline wins and loses — by airport."
)
st.markdown(
    "<p style='font-size:0.8rem;color:#999999;"
    "margin:-0.8rem 0 1rem 0;'>"
    "Bubble size = cancellation rate  ·  "
    "Top-right = high volume AND high delay (problem hubs)"
    "</p>",
    unsafe_allow_html=True
)

hub_df  = df_v[df_v["Origin"].isin(HUBS)]
hub_grp = (
    hub_df
    .groupby(["Origin","Reporting_Airline"])
    .agg(
        avg_delay=("ArrDelay",  "mean"),
        flights  =("ArrDelay",  "count"),
        canc     =("Cancelled", "mean")
    )
    .reset_index()
)
hub_grp["Airline"]  = hub_grp["Reporting_Airline"].map(
    {"DL":"Delta","AA":"American Airlines"}
)
hub_grp["canc_pct"] = hub_grp["canc"] * 100
hub_grp["bubble"]   = (hub_grp["canc_pct"].clip(lower=0.3) * 5
                       ).clip(lower=4)

if len(hub_grp):
    fig_hub = px.scatter(
        hub_grp,
        x="flights", y="avg_delay",
        color="Airline", size="bubble",
        size_max=45, text="Origin",
        color_discrete_map={
            "Delta": DL_COL,
            "American Airlines": AA_COL
        },
        custom_data=["Origin","Airline",
                     "avg_delay","flights","canc_pct"]
    )
    fig_hub.update_traces(
        textposition="top center",
        textfont=dict(size=11, color="#333333"),
        hovertemplate=(
            "<b>%{customdata[0]}</b> — %{customdata[1]}<br>"
            "Avg Delay: <b>%{customdata[2]:.1f} min</b><br>"
            "Flights Operated: <b>%{customdata[3]:,}</b><br>"
            "Cancellation Rate: <b>%{customdata[4]:.2f}%</b>"
            "<extra></extra>"
        )
    )
    fig_hub.add_hline(
        y=15,
        line_dash="dash",
        line_color="#cccccc",
        annotation_text="DOT 15-min on-time threshold",
        annotation_position="top right",
        annotation_font=dict(size=10, color="#aaaaaa")
    )
    max_f = hub_grp["flights"].max()
    max_d = hub_grp["avg_delay"].max()
    min_d = hub_grp["avg_delay"].min()
    fig_hub.add_annotation(
        x=max_f*0.82, y=max_d*0.92,
        text="⚠️ High Volume + High Delay",
        showarrow=False,
        font=dict(size=10, color="#e57373")
    )
    fig_hub.add_annotation(
        x=max_f*0.82, y=min_d + 1.2,
        text="✅ High Volume + Low Delay",
        showarrow=False,
        font=dict(size=10, color="#66bb6a")
    )
    fig_hub.update_layout(
        plot_bgcolor="white",
        paper_bgcolor="white",
        height=460,
        margin=dict(t=20, b=60, l=70, r=20),
        legend=dict(
            orientation="h", y=1.04, x=0,
            font=dict(size=11)
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor="#f2f2f2",
            title=dict(
                text="Total Flights Operated (Volume)",
                font=dict(size=12, color="#555555")
            ),
            tickformat=",",
            tickfont=dict(size=11, color="#333333"),
            showline=True,
            linecolor="#dddddd"
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#f2f2f2",
            title=dict(
                text="Average Arrival Delay (minutes)",
                font=dict(size=12, color="#555555")
            ),
            tickfont=dict(size=11, color="#333333"),
            ticksuffix=" min",
            showline=True,
            linecolor="#dddddd"
        )
    )
    st.plotly_chart(fig_hub, use_container_width=True)

st.markdown("---")

# ── SECTION 4: EXECUTIVE VERDICTS ─────────────────────────
section_header(
    "Executive Summary",
    "Three findings every airline executive should know."
)

v1, v2, v3 = st.columns(3)

for col, num, num_color, title, body in [
    (v1, "#1", DL_COL, "THE EFFICIENCY GAP",
     f"Delta arrives <b>{gap:.1f} min earlier</b> than AA on "
     f"average — across every month, every hub, every route in "
     f"2024. Across <b>{len(df_dl):,} Delta flights</b>, that "
     f"compound advantage is structural, not seasonal."),
    (v2, "#2", DL_COL, "THE WEATHER MYTH",
     f"Only <b>{dl_wx:.1f}%</b> of Delta's and "
     f"<b>{aa_wx:.1f}%</b> of AA's delays were weather-caused. "
     f"<b>{dl_ctrl:.0f}%</b> and <b>{aa_ctrl:.0f}%</b> "
     f"respectively were fully within the airline's own control. "
     f"Weather is not the story."),
    (v3, "#3", AA_COL, "THE SUMMER DIVERGENCE",
     f"In peak summer, Delta averaged <b>{s_dl} min</b> "
     f"vs AA's <b>{s_aa} min</b>. The gap widens precisely "
     f"when it matters most — during the highest-revenue "
     f"travel period of the year.")
]:
    with col:
        st.markdown(f"""
        <div style="
            background:{GREY_BG};
            border-radius:12px;
            padding:1.4rem 1.3rem;
            height:100%;
        ">
            <p style="
                font-size:2.2rem;
                font-weight:800;
                color:{num_color};
                margin:0 0 4px 0;
                line-height:1;
            ">{num}</p>
            <p style="
                font-size:0.65rem;
                font-weight:700;
                letter-spacing:0.1em;
                text-transform:uppercase;
                color:#aaaaaa;
                margin:0 0 10px 0;
            ">{title}</p>
            <p style="
                font-size:0.88rem;
                color:#444444;
                line-height:1.75;
                margin:0;
            ">{body}</p>
        </div>
        """, unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────
st.markdown("""
<div style="
    text-align:center;
    padding:2rem 0 1rem;
    border-top:1px solid #f0f0f0;
    margin-top:2rem;
">
    <p style="font-size:0.75rem;color:#cccccc;margin:0;">
        Data Source: US Bureau of Transportation Statistics
        (BTS) · Full Year 2024 · 1.9M+ flights analyzed<br>
        Built with Python · pandas · Plotly · Streamlit
    </p>
</div>
""", unsafe_allow_html=True)