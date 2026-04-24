import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ── CONFIG ─────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚴",
    layout="wide"
)

# ── CUSTOM DARK STYLE ──────────────────────────────
st.markdown("""
<style>
.stApp {
    background-color: #0E1117;
    color: #EAEAEA;
}
section[data-testid="stMetric"] {
    background-color: #1A1F2B;
    padding: 15px;
    border-radius: 12px;
    transition: 0.3s;
}
section[data-testid="stMetric"]:hover {
    transform: scale(1.05);
}
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ──────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "main_data.csv")
    df = pd.read_csv(path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

try:
    df = load_data()
except:
    st.error("❌ File main_data.csv tidak ditemukan")
    st.stop()

# ── PREPROCESS ─────────────────────────────────────
season_map  = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
weather_map = {1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain"}

df["season_label"] = df["season"].map(season_map)
df["weather_label"] = df["weathersit"].map(weather_map)
df["year"] = df["yr"].map({0: 2011, 1: 2012})

df["temp_c"] = df["temp"] * 41
df["hum_pct"] = df["hum"] * 100

def segment(cnt):
    if cnt < 2000:
        return "Low Usage"
    elif cnt <= 5000:
        return "Medium Usage"
    return "High Usage"

df["usage_segment"] = df["cnt"].apply(segment)

# ── SIDEBAR ────────────────────────────────────────
with st.sidebar:
    st.title("🚴 Bike Dashboard")

    with st.expander("📅 Filter Waktu", True):
        years = sorted(df["year"].unique())
        selected_years = st.multiselect("Tahun", years, years)

        date_range = st.date_input(
            "Tanggal",
            [df["dteday"].min(), df["dteday"].max()]
        )

    with st.expander("🌦️ Filter Kondisi"):
        seasons = df["season_label"].unique()
        selected_seasons = st.multiselect("Musim", seasons, seasons)

# ── FILTER ─────────────────────────────────────────
filtered = df[
    (df["year"].isin(selected_years)) &
    (df["season_label"].isin(selected_seasons))
]

if len(date_range) == 2:
    filtered = filtered[
        (filtered["dteday"] >= pd.Timestamp(date_range[0])) &
        (filtered["dteday"] <= pd.Timestamp(date_range[1]))
    ]

# ── HEADER ─────────────────────────────────────────
st.title("🚴 Bike Sharing Dashboard")
st.caption("Analisis penyewaan sepeda Washington D.C.")

# ── METRICS ────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)

total = filtered["cnt"].sum()
avg = filtered["cnt"].mean()

with c1:
    st.metric("Total", f"{total:,.0f}")

with c2:
    st.metric("Rata-rata", f"{avg:,.0f}")

with c3:
    st.metric("Max", f"{filtered['cnt'].max():,.0f}")

with c4:
    casual_pct = filtered["casual"].sum() / total * 100 if total else 0
    st.metric("Casual %", f"{casual_pct:.1f}%")

st.divider()

# ── INSIGHT ────────────────────────────────────────
if avg > 5000:
    st.success("📈 Penyewaan tinggi (peak season)")
elif avg > 3000:
    st.info("📊 Penyewaan stabil")
else:
    st.warning("📉 Penyewaan rendah")

# ── TREN BULANAN ───────────────────────────────────
st.subheader("📈 Tren Bulanan")

monthly = filtered.groupby(["year", "mnth"])["cnt"].mean().reset_index()

fig = px.line(
    monthly,
    x="mnth",
    y="cnt",
    color="year",
    markers=True
)

fig.update_layout(template="plotly_dark")
st.plotly_chart(fig, use_container_width=True)

# ── MUSIM ──────────────────────────────────────────
st.subheader("🌤️ Pengaruh Musim")

season_avg = filtered.groupby("season_label")["cnt"].mean().reset_index()

fig2 = px.bar(
    season_avg,
    x="season_label",
    y="cnt",
    color="season_label",
    text="cnt"
)

fig2.update_layout(template="plotly_dark")
st.plotly_chart(fig2, use_container_width=True)

# ── CUACA ──────────────────────────────────────────
st.subheader("🌦️ Pengaruh Cuaca")

weather_avg = filtered.groupby("weather_label")["cnt"].mean().reset_index()

fig3 = px.bar(
    weather_avg,
    x="weather_label",
    y="cnt",
    color="weather_label",
    text="cnt"
)

fig3.update_layout(template="plotly_dark")
st.plotly_chart(fig3, use_container_width=True)

# ── HEATMAP ────────────────────────────────────────
st.subheader("🌡️ Heatmap Musim vs Cuaca")

pivot = filtered.pivot_table(
    values="cnt",
    index="season_label",
    columns="weather_label",
    aggfunc="mean"
)

fig4 = px.imshow(
    pivot,
    text_auto=True,
    aspect="auto",
    color_continuous_scale="YlOrRd"
)

fig4.update_layout(template="plotly_dark")
st.plotly_chart(fig4, use_container_width=True)

# ── SEGMENTASI ─────────────────────────────────────
st.subheader("📊 Segmentasi")

seg = filtered["usage_segment"].value_counts().reset_index()
seg.columns = ["segment", "count"]

fig5 = px.pie(
    seg,
    names="segment",
    values="count"
)

fig5.update_layout(template="plotly_dark")
st.plotly_chart(fig5, use_container_width=True)

# ── INTERAKTIF FILTER SEGMENT ──────────────────────
selected_segment = st.selectbox(
    "Filter Segment",
    ["All", "Low Usage", "Medium Usage", "High Usage"]
)

if selected_segment != "All":
    filtered = filtered[filtered["usage_segment"] == selected_segment]

# ── TABLE ──────────────────────────────────────────
with st.expander("📋 Lihat Data"):
    st.dataframe(filtered)

# ── FOOTER ─────────────────────────────────────────
st.caption("© 2024 Dashboard Analisis Data")
