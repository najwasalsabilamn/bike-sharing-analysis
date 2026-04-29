import streamlit as st
import pandas as pd
import plotly.express as px
import os

# ── CONFIG ─────────────────────────────
st.set_page_config(layout="wide")

# ── STYLE ─────────────────────────────
st.markdown("""
<style>
body {
    background-color: #0B0F19;
}
.block-container {
    padding-top: 2rem;
}

/* CARD */
.card {
    background: #111827;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.4);
}

/* TITLE */
.title {
    font-size: 40px;
    font-weight: 700;
    color: white;
}

/* SUB */
.sub {
    color: #9CA3AF;
    margin-bottom: 20px;
}

/* METRIC */
.metric {
    font-size: 28px;
    font-weight: bold;
}

/* SECTION */
.section {
    margin-top: 30px;
    margin-bottom: 10px;
    font-size: 22px;
    font-weight: 600;
    color: white;
}
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────
@st.cache_data
def load():
    path = os.path.join(os.path.dirname(__file__), "main_data.csv")
    df = pd.read_csv(path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

df = load()

# ── PREPROCESS ────────────────────────
df["year"] = df["yr"].map({0: 2011, 1: 2012})
df["season"] = df["season"].map({1:"Spring",2:"Summer",3:"Fall",4:"Winter"})
df["weather"] = df["weathersit"].map({1:"Clear",2:"Cloudy",3:"Rain"})

# ── SIDEBAR ──────────────────────────
with st.sidebar:
    st.title("🚴 Filter")

    year = st.multiselect("Year", df["year"].unique(), df["year"].unique())
    season = st.multiselect("Season", df["season"].unique(), df["season"].unique())

filtered = df[(df["year"].isin(year)) & (df["season"].isin(season))]

# ── HEADER ───────────────────────────
st.markdown('<div class="title">🚴 Bike Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Clean & Modern Data Visualization</div>', unsafe_allow_html=True)

# ── METRICS ──────────────────────────
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("Total")
    st.markdown(f'<div class="metric">{filtered["cnt"].sum():,.0f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("Average")
    st.markdown(f'<div class="metric">{filtered["cnt"].mean():,.0f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("Max")
    st.markdown(f'<div class="metric">{filtered["cnt"].max():,.0f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── TREND ────────────────────────────
st.markdown('<div class="section">📈 Monthly Trend</div>', unsafe_allow_html=True)

monthly = filtered.groupby("mnth")["cnt"].mean().reset_index()

fig = px.line(monthly, x="mnth", y="cnt", markers=True)
fig.update_layout(
    template="plotly_dark",
    plot_bgcolor="#111827",
    paper_bgcolor="#111827",
)

st.plotly_chart(fig, use_container_width=True)

# ── SEASON ───────────────────────────
col4, col5 = st.columns(2)

with col4:
    st.markdown('<div class="section">🌤️ Season</div>', unsafe_allow_html=True)
    season_avg = filtered.groupby("season")["cnt"].mean().reset_index()
    fig2 = px.bar(season_avg, x="season", y="cnt", color="season")
    fig2.update_layout(template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

with col5:
    st.markdown('<div class="section">🌧️ Weather</div>', unsafe_allow_html=True)
    weather_avg = filtered.groupby("weather")["cnt"].mean().reset_index()
    fig3 = px.bar(weather_avg, x="weather", y="cnt", color="weather")
    fig3.update_layout(template="plotly_dark")
    st.plotly_chart(fig3, use_container_width=True)

# ── PIE ──────────────────────────────
st.markdown('<div class="section">📊 Usage Distribution</div>', unsafe_allow_html=True)

seg = filtered["cnt"].apply(lambda x: "Low" if x<2000 else "Medium" if x<5000 else "High")
seg = seg.value_counts().reset_index()
seg.columns = ["segment","count"]

fig4 = px.pie(seg, names="segment", values="count")
fig4.update_layout(template="plotly_dark")

st.plotly_chart(fig4, use_container_width=True)
