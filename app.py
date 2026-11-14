
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ---------------- PAGE CONFIGURATION ----------------

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

[data-testid="stSidebar"] {
    background-color: #111d30;
}
</style>
""", unsafe_allow_html=True)

# ---------------- HEADER ----------------

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
    options=sorted(df["store_name"].unique()),
    default=sorted(df["store_name"].unique())
)

min_date = df["date"].min().date()
max_date = df["date"].max().date()

selected_dates = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# ---------------- FILTER DATA ----------------

if len(selected_dates) == 2:

    start_date, end_date = selected_dates

    filtered = df[
        (df["store_name"].isin(selected_stores)) &
        (df["date"].dt.date >= start_date) &
        (df["date"].dt.date <= end_date)
    ]

else:
    filtered = df[
        df["store_name"].isin(selected_stores) &
        (df["date"].dt.date == selected_dates[0])
    ]

if filtered.empty:

    st.warning(
        "No data available for the selected filters. "
        "Please select at least one store and a valid date range."
    )

    st.stop()

# ---------------- EXECUTIVE OVERVIEW ----------------

st.header("📊 Executive Overview")

total_visitors = filtered["visitors"].sum()

total_stores = filtered["store_id"].nunique()

average_visitors = filtered["visitors"].mean()

peak_hour = int(
    filtered.groupby("hour")["visitors"]
    .sum()
    .idxmax()
)

c1, c2, c3, c4 = st.columns(4)

c1.metric(
    "Total Visitors",
    f"{total_visitors:,}"
)

c2.metric(
    "Total Stores",
    total_stores
)

c3.metric(
    "Average Footfall",
    f"{average_visitors:.1f}"
)

c4.metric(
    "Peak Hour",
    f"{peak_hour}:00"
)

# ---------------- DAILY FOOTFALL ----------------

st.header("📈 Daily Footfall Analysis")

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
    plot_bgcolor="#162438",
    xaxis_title="Date",
    yaxis_title="Total Visitors"
)

st.plotly_chart(
    fig_daily,
    width="stretch"
)

# ---------------- PEAK VISITING HOURS ----------------

st.header("⏰ Peak Visiting Hours")

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
    color_continuous_scale="Teal",
    text_auto=True
)

fig_hour.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0b1220",
    plot_bgcolor="#162438",
    xaxis_title="Hour",
    yaxis_title="Total Visitors"
)

st.plotly_chart(
    fig_hour,
    width="stretch"
)

# ---------------- STORE PERFORMANCE ----------------

st.header("🏬 Store Performance")

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
    color_continuous_scale="Teal",
    text_auto=True
)

fig_store.update_layout(
    template="plotly_dark",
    paper_bgcolor="#0b1220",
    plot_bgcolor="#162438",
    xaxis_title="Store Name",
    yaxis_title="Total Visitors"
)

st.plotly_chart(
    fig_store,
    width="stretch"
)

# ---------------- STORE PERFORMANCE COMPARISON ----------------

st.header("⚖️ Store Performance Comparison")

store_options = sorted(filtered["store_name"].unique())

if len(store_options) >= 2:

    col1, col2 = st.columns(2)

    with col1:

        store_a = st.selectbox(
            "Select First Store",
            store_options,
            key="compare_store_a"
        )

    with col2:

        store_b = st.selectbox(
            "Select Second Store",
            store_options,
            index=1,
            key="compare_store_b"
        )

    comparison = (
        filtered[
            filtered["store_name"].isin([store_a, store_b])
        ]
        .groupby("store_name", as_index=False)["visitors"]
        .sum()
    )

    fig_compare = px.bar(
        comparison,
        x="store_name",
        y="visitors",
        color="store_name",
        title="Compare Customer Footfall",
        text_auto=True
    )

    fig_compare.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0b1220",
        plot_bgcolor="#162438",
        xaxis_title="Store",
        yaxis_title="Total Visitors"
    )

    st.plotly_chart(
        fig_compare,
        width="stretch"
    )

    value_a = filtered.loc[
        filtered["store_name"] == store_a,
        "visitors"
    ].sum()

    value_b = filtered.loc[
        filtered["store_name"] == store_b,
        "visitors"
    ].sum()

    m1, m2, m3 = st.columns(3)

    m1.metric(
        store_a,
        f"{value_a:,}"
    )

    m2.metric(
        store_b,
        f"{value_b:,}"
    )

    m3.metric(
        "Footfall Difference",
        f"{abs(value_a - value_b):,}"
    )

else:

    st.info(
        "Select at least two stores to compare performance."
    )

# ---------------- GEOGRAPHICAL ANALYSIS ----------------

st.header("🌍 Geographical Footfall Analysis")

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

st.plotly_chart(
    fig_map,
    width="stretch"
)

# ---------------- BUSINESS INSIGHTS ----------------

st.header("💡 Business Insights")

best_store = store_data.iloc[0]["store_name"]

best_store_visitors = int(
    store_data.iloc[0]["visitors"]
)

st.success(
    f"Highest footfall store: {best_store} "
    f"({best_store_visitors:,} visitors)"
)

st.info(
    f"Peak customer visiting hour: {peak_hour}:00"
)

st.write(
    "Retail managers can use these insights to plan "
    "staffing, promotions, inventory and store operations."
)

# ---------------- DATA TABLE ----------------

st.header("📋 Retail Footfall Data")

st.dataframe(
    filtered,
    width="stretch",
    hide_index=True
)

# ---------------- CSV DOWNLOAD ----------------

csv = filtered.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="📥 Download Footfall Report",
    data=csv,
    file_name="geopulse_footfall_report.csv",
    mime="text/csv"
)

# ---------------- FOOTER ----------------

st.divider()

st.caption(
    "GeoPulse | Hyper-Local Retail Mobility Analytics | "
    "Synthetic Demonstration Data | 2026"
)