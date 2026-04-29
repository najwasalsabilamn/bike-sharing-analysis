import streamlit as st
import pandas as pd
import plotly.express as px
import os

st.set_page_config(layout="wide")

# ── STYLE SUPER CLEAN ─────────────────────────────
st.markdown("""
<style>
/* Background gradient */
.stApp {
    background: linear-gradient(135deg, #0f172a, #020617);
    color: white;
}

/* Container spacing */
.block-container {
    padding-top: 2rem;
}

/* Glass card */
.glass {
    background: rgba(255, 255, 255, 0.05);
    backdrop-filter: blur(12px);
    border-radius: 16px;
    padding: 20px;
    box-shadow: 0 8px 32px rgba(0,0,0,0.4);
}

/* Title */
.title {
    font-size: 42px;
    font-weight: 700;
}

/* Subtitle */
.sub {
    color: #94A3B8;
    margin-bottom: 30px;
}

/* Metric */
.metric {
    font-size: 30px;
    font-weight: bold;
}
</style>
""", unsafe_allow_html=True)

# ── LOAD DATA ─────────────────────────────────────
@st.cache_data
def load():
    path = os.path.join(os.path.dirname(__file__), "main_data.csv")
    df = pd.read_csv(path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

df = load()

# ── PREPROCESS ────────────────────────────────────
df["year"] = df["yr"].map({0: 2011, 1: 2012})
df["season"] = df["season"].map({1:"Spring",2:"Summer",3:"Fall",4:"Winter"})
df["weather"] = df["weathersit"].map({1:"Clear",2:"Cloudy",3:"Rain"})

# ── SIDEBAR ───────────────────────────────────────
with st.sidebar:
    st.title("⚙️ Filter")
    year = st.multiselect("Year", df["year"].unique(), df["year"].unique())
    season = st.multiselect("Season", df["season"].unique(), df["season"].unique())

filtered = df[(df["year"].isin(year)) & (df["season"].isin(season))]

# ── HEADER ────────────────────────────────────────
st.markdown('<div class="title">🚴 Bike Dashboard</div>', unsafe_allow_html=True)
st.markdown('<div class="sub">Modern analytics interface</div>', unsafe_allow_html=True)

# ── METRIC CARDS ──────────────────────────────────
c1, c2, c3 = st.columns(3)

with c1:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.write("Total")
    st.markdown(f'<div class="metric">{filtered["cnt"].sum():,.0f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.write("Average")
    st.markdown(f'<div class="metric">{filtered["cnt"].mean():,.0f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

with c3:
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.write("Max")
    st.markdown(f'<div class="metric">{filtered["cnt"].max():,.0f}</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# ── TREND ─────────────────────────────────────────
st.markdown("### 📈 Trend")

monthly = filtered.groupby("mnth")["cnt"].mean().reset_index()

fig = px.line(monthly, x="mnth", y="cnt", markers=True)

fig.update_layout(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)"
)

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── ROW 2 ─────────────────────────────────────────
col4, col5 = st.columns(2)

with col4:
    st.markdown("### 🌤️ Season")
    season_avg = filtered.groupby("season")["cnt"].mean().reset_index()
    fig2 = px.bar(season_avg, x="season", y="cnt", color="season")
    fig2.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col5:
    st.markdown("### 🌧️ Weather")
    weather_avg = filtered.groupby("weather")["cnt"].mean().reset_index()
    fig3 = px.bar(weather_avg, x="weather", y="cnt", color="weather")
    fig3.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")
    st.markdown('<div class="glass">', unsafe_allow_html=True)
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ── PIE ───────────────────────────────────────────
st.markdown("### 📊 Usage")

seg = filtered["cnt"].apply(lambda x: "Low" if x<2000 else "Medium" if x<5000 else "High")
seg = seg.value_counts().reset_index()
seg.columns = ["segment","count"]

fig4 = px.pie(seg, names="segment", values="count")
fig4.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)")

st.markdown('<div class="glass">', unsafe_allow_html=True)
st.plotly_chart(fig4, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)
