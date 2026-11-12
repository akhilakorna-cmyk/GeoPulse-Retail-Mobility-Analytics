
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(
    page_title="GeoPulse Analytics",
    page_icon="📍",
    layout="wide"
)

# ---------------- PAGE DESIGN ----------------

st.markdown("""
<style>
.stApp {
    background-color: #0b1220;
    color: white;
}
[data-testid="stMetric"] {
    background-color: #162438;
    padding: 18px;
    border-radius: 12px;
    border: 1px solid #24445c;
}
h1, h2, h3 {
    color: #20d6c0;
}
</style>
""", unsafe_allow_html=True)

st.title("📍 GeoPulse Analytics")
st.subheader("Hyper-Local Retail Mobility Analytics")

st.info(
    "DEMO MODE — This dashboard uses synthetic sample data, "
    "not real customer mobility records."
)

# ---------------- SAMPLE DATA ----------------

@st.cache_data
def load_data():
    np.random.seed(42)

    stores = [
        ("S001", "Central Mall", "Nellore", 14.4426, 79.9865),
        ("S002", "City Plaza", "Nellore", 14.4500, 79.9900),
        ("S003", "Retail Hub", "Nellore", 14.4350, 79.9800),
        ("S004", "Market Square", "Nellore", 14.4600, 79.9950),
        ("S005", "Shopping Point", "Nellore", 14.4300, 79.9750)
    ]

    rows = []

    dates = pd.date_range("2026-10-01", periods=30)

    for store_id, name, city, lat, lon in stores:
        for date in dates:
            for hour in range(9, 22):
                peak = 1.0 + 2.0 * np.exp(
                    -((hour - 18) ** 2) / 12
                )

                visitors = max(
                    0,
                    int(np.random.poisson(peak * 12))
                )

                rows.append({
                    "store_id": store_id,
                    "store_name": name,
                    "city": city,
                    "date": date,
                    "hour": hour,
                    "visitors": visitors,
                    "latitude": lat,
                    "longitude": lon
                })

    return pd.DataFrame(rows)


df = load_data()

# ---------------- SIDEBAR FILTERS ----------------

st.sidebar.title("Dashboard Filters")

selected_stores = st.sidebar.multiselect(
    "Select Stores",
    df["store_name"].unique(),
    default=df["store_name"].unique()
)

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(df["date"].min().date(), df["date"].max().date())
)

if len(selected_dates) == 2:
    start_date, end_date = selected_dates

    filtered = df[
        (df["store_name"].isin(selected_stores)) &
        (df["date"].dt.date >= start_date) &
        (df["date"].dt.date <= end_date)
    ]
else:
    filtered = df[
        df["store_name"].isin(selected_stores)
    ]

if filtered.empty:
    st.warning("No data available for the selected filters.")
    st.stop()

# ---------------- KPI SECTION ----------------

st.header("Executive Overview")

total_visitors = filtered["visitors"].sum()
total_stores = filtered["store_id"].nunique()
average_visitors = filtered["visitors"].mean()

peak_hour = (
    filtered.groupby("hour")["visitors"]
    .sum()
    .idxmax()
)

c1, c2, c3, c4 = st.columns(4)

c1.metric("Total Visitors", f"{total_visitors:,}")
c2.metric("Total Stores", total_stores)
c3.metric("Average Footfall", f"{average_visitors:.1f}")
c4.metric("Peak Hour", f"{peak_hour}:00")

# ---------------- DAILY FOOTFALL ----------------

st.header("Daily Footfall Analysis")

daily = (
    filtered.groupby("date", as_index=False)["visitors"]
    .sum()
)

fig_daily = px.line(
    daily,
    x="date",
    y="visitors",
    markers=True,
    title="Daily Customer Footfall"
)

fig_daily.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0b1220",
    plot_bgcolor="#162438"
)

st.plotly_chart(fig_daily, width="stretch")

# ---------------- PEAK HOURS ----------------

st.header("Peak Visiting Hours")

hourly = (
    filtered.groupby("hour", as_index=False)["visitors"]
    .sum()
)

fig_hour = px.bar(
    hourly,
    x="hour",
    y="visitors",
    title="Visitors by Hour",
    color="visitors",
    color_continuous_scale="Teal"
)

fig_hour.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0b1220",
    plot_bgcolor="#162438"
)

st.plotly_chart(fig_hour, width="stretch")

# ---------------- STORE PERFORMANCE ----------------

st.header("Store Performance")

store_data = (
    filtered.groupby("store_name", as_index=False)["visitors"]
    .sum()
    .sort_values("visitors", ascending=False)
)

fig_store = px.bar(
    store_data,
    x="store_name",
    y="visitors",
    color="visitors",
    title="Store-wise Customer Footfall",
    color_continuous_scale="Teal"
)

fig_store.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0b1220",
    plot_bgcolor="#162438"
)

st.plotly_chart(fig_store, width="stretch")

# ---------------- GEOGRAPHICAL ANALYSIS ----------------

st.header("Geographical Footfall Analysis")

location_data = (
    filtered.groupby(
        ["store_name", "latitude", "longitude"],
        as_index=False
    )["visitors"].sum()
)

fig_map = px.scatter_map(
    location_data,
    lat="latitude",
    lon="longitude",
    size="visitors",
    color="visitors",
    hover_name="store_name",
    zoom=12,
    map_style="open-street-map",
    title="Retail Store Footfall Locations"
)

st.plotly_chart(fig_map, width="stretch")

# ---------------- BUSINESS INSIGHTS ----------------

st.header("Business Insights")

best_store = store_data.iloc[0]["store_name"]

st.success(
    f"Highest footfall store: {best_store}"
)

st.info(
    f"Peak customer visiting hour: {peak_hour}:00"
)

st.write(
    "Retail managers can use these insights to plan "
    "staffing, promotions and store operations."
)

# ---------------- DATA TABLE ----------------

st.header("Retail Footfall Data")

st.dataframe(filtered, width="stretch")

csv = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    "Download Footfall Report",
    csv,
    "geopulse_footfall_report.csv",
    "text/csv"
)

st.caption(
    "GeoPulse | Hyper-Local Retail Mobility Analytics | "
    "Synthetic demonstration data"
)
