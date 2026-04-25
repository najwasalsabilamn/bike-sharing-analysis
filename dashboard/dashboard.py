import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ── Konfigurasi halaman ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Styling (biar lebih clean & modern) ──────────────────────────────────────
st.markdown("""
<style>
.block-container {
    padding-top: 2rem;
    padding-bottom: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

h1, h2, h3 {
    font-weight: 600;
}

[data-testid="stMetricValue"] {
    font-size: 1.6rem;
}

[data-testid="stMetricLabel"] {
    font-size: 0.85rem;
    color: gray;
}
</style>
""", unsafe_allow_html=True)

sns.set_theme(style="whitegrid")
plt.rcParams["figure.dpi"] = 100

# ── Load data ────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "main_data.csv")
    df = pd.read_csv(path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

try:
    main_df = load_data()
except FileNotFoundError:
    st.error("File `main_data.csv` tidak ditemukan.")
    st.stop()

# ── Mapping ──────────────────────────────────────────────────────────────────
season_map  = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
weather_map = {1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain"}
weekday_map = {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"}

main_df["season_label"]  = main_df["season"].map(season_map)
main_df["weather_label"] = main_df["weathersit"].map(weather_map)
main_df["weekday_label"] = main_df["weekday"].map(weekday_map)
main_df["year"] = main_df["yr"].map({0: 2011, 1: 2012})
main_df["temp_c"] = main_df["temp"] * 41
main_df["hum_pct"] = main_df["hum"] * 100

def segment_usage(cnt):
    if cnt < 2000:
        return "Low"
    elif cnt <= 5000:
        return "Medium"
    return "High"

main_df["usage_segment"] = main_df["cnt"].apply(segment_usage)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Bike Sharing")
    st.markdown("---")

    selected_years = st.multiselect(
        "Year",
        sorted(main_df["year"].unique()),
        default=sorted(main_df["year"].unique())
    )

    selected_seasons = st.multiselect(
        "Season",
        sorted(main_df["season_label"].unique()),
        default=sorted(main_df["season_label"].unique())
    )

    date_range = st.date_input(
        "Date Range",
        [main_df["dteday"].min(), main_df["dteday"].max()]
    )

# ── Filter ───────────────────────────────────────────────────────────────────
filtered = main_df[
    (main_df["year"].isin(selected_years)) &
    (main_df["season_label"].isin(selected_seasons))
]

if len(date_range) == 2:
    filtered = filtered[
        (filtered["dteday"] >= pd.Timestamp(date_range[0])) &
        (filtered["dteday"] <= pd.Timestamp(date_range[1]))
    ]

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("## Bike Sharing Dashboard")
st.caption("Analisis penyewaan sepeda di Washington D.C. (2011–2012)")

# ── Metrics ──────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4, gap="large")

with m1:
    st.metric("Total Trips", f"{filtered['cnt'].sum():,.0f}")

with m2:
    st.metric("Avg / Day", f"{filtered['cnt'].mean():,.0f}")

with m3:
    st.metric("Peak Day", f"{filtered['cnt'].max():,.0f}")

with m4:
    casual_pct = filtered["casual"].sum() / filtered["cnt"].sum() * 100 if filtered["cnt"].sum() > 0 else 0
    st.metric("Casual Users", f"{casual_pct:.1f}%")

st.divider()

# ── Monthly Trend ────────────────────────────────────────────────────────────
st.markdown("### Monthly Trend")

monthly = filtered.groupby(["year", "mnth"])["cnt"].mean().reset_index()

fig, ax = plt.subplots(figsize=(12, 4))
for yr, color in [(2011, "#3b82f6"), (2012, "#f97316")]:
    sub = monthly[monthly["year"] == yr]
    if not sub.empty:
        ax.plot(sub["mnth"], sub["cnt"], marker="o", linewidth=2.5,
                color=color, label=str(yr))
        ax.fill_between(sub["mnth"], sub["cnt"], alpha=0.08, color=color)

ax.set_xticks(range(1, 13))
ax.set_xticklabels(["Jan","Feb","Mar","Apr","May","Jun",
                    "Jul","Aug","Sep","Oct","Nov","Dec"])
ax.set_ylabel("Avg Rentals")
ax.legend(frameon=False)
ax.spines[["top", "right"]].set_visible(False)

st.pyplot(fig)
plt.close()

st.divider()

# ── Season & Weather ─────────────────────────────────────────────────────────
st.markdown("### Season & Weather Impact")

c1, c2 = st.columns(2, gap="large")

with c1:
    s_agg = filtered.groupby("season_label")["cnt"].mean().reset_index()
    fig2, ax2 = plt.subplots()
    ax2.bar(s_agg["season_label"], s_agg["cnt"], color="#60a5fa")
    ax2.set_title("Average by Season")
    ax2.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig2)
    plt.close()

with c2:
    w_agg = filtered.groupby("weather_label")["cnt"].mean().reset_index()
    fig3, ax3 = plt.subplots()
    ax3.bar(w_agg["weather_label"], w_agg["cnt"], color="#fbbf24")
    ax3.set_title("Average by Weather")
    ax3.tick_params(axis="x", rotation=20)
    ax3.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig3)
    plt.close()

st.divider()

# ── Heatmap ──────────────────────────────────────────────────────────────────
st.markdown("### Season × Weather")

pivot = filtered.pivot_table(
    values="cnt",
    index="season_label",
    columns="weather_label",
    aggfunc="mean"
)

fig4, ax4 = plt.subplots()
sns.heatmap(pivot, annot=True, fmt=".0f", cmap="YlOrRd", ax=ax4)
st.pyplot(fig4)
plt.close()

st.divider()

# ── Segmentation ─────────────────────────────────────────────────────────────
st.markdown("### Usage Segmentation")

c3, c4 = st.columns([1, 2], gap="large")

with c3:
    counts = filtered["usage_segment"].value_counts()
    fig5, ax5 = plt.subplots()
    ax5.pie(counts, labels=counts.index, autopct="%1.1f%%")
    st.pyplot(fig5)
    plt.close()

with c4:
    seg_tab = pd.crosstab(filtered["season_label"], filtered["usage_segment"])
    fig6, ax6 = plt.subplots()
    seg_tab.plot(kind="bar", stacked=True, ax=ax6)
    ax6.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig6)
    plt.close()

st.divider()

# ── Summary Table ────────────────────────────────────────────────────────────
st.markdown("### Summary Table")

with st.expander("Show statistical summary"):
    summary = filtered.groupby("usage_segment")[["cnt", "casual", "registered", "temp_c", "hum_pct"]].mean().round(1)
    st.dataframe(summary, use_container_width=True)

st.caption("Data: Capital Bikeshare (2011–2012)")
