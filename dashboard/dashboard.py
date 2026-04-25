import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os

# ── CONFIG ───────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚴",
    layout="wide",
)

# ── CUSTOM CSS (BIAR KELIATAN PRO) ───────────────────────────────────────────
st.markdown("""
<style>

/* Background */
body {
    background-color: #f5f7fb;
}

/* Main container */
.block-container {
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
}

/* Card style */
.card {
    background: white;
    padding: 20px;
    border-radius: 16px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.05);
    margin-bottom: 20px;
}

/* Metric styling */
[data-testid="stMetric"] {
    background: white;
    padding: 15px;
    border-radius: 14px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

/* Title */
h1, h2, h3 {
    font-weight: 600;
}

</style>
""", unsafe_allow_html=True)

sns.set_theme(style="whitegrid")

# ── LOAD DATA ────────────────────────────────────────────────────────────────
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
    st.error("File main_data.csv tidak ditemukan")
    st.stop()

# ── PREPROCESS ───────────────────────────────────────────────────────────────
df["season_label"]  = df["season"].map({1:"Spring",2:"Summer",3:"Fall",4:"Winter"})
df["weather_label"] = df["weathersit"].map({1:"Clear",2:"Mist",3:"Rain",4:"Heavy"})
df["year"] = df["yr"].map({0:2011,1:2012})

def segment(x):
    if x < 2000: return "Low"
    elif x <= 5000: return "Medium"
    return "High"

df["segment"] = df["cnt"].apply(segment)

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("Bike Sharing")

    years = st.multiselect("Year", df["year"].unique(), default=df["year"].unique())
    seasons = st.multiselect("Season", df["season_label"].unique(), default=df["season_label"].unique())

# ── FILTER ───────────────────────────────────────────────────────────────────
filtered = df[
    (df["year"].isin(years)) &
    (df["season_label"].isin(seasons))
]

# ── HEADER CARD ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="card">
    <h2>Bike Sharing Dashboard</h2>
    <p style="color:gray;">Analisis penyewaan sepeda (2011–2012)</p>
</div>
""", unsafe_allow_html=True)

# ── METRICS ──────────────────────────────────────────────────────────────────
m1, m2, m3, m4 = st.columns(4)

m1.metric("Total Trips", f"{filtered['cnt'].sum():,.0f}")
m2.metric("Avg / Day", f"{filtered['cnt'].mean():,.0f}")
m3.metric("Peak", f"{filtered['cnt'].max():,.0f}")
m4.metric("Casual %", f"{filtered['casual'].sum()/filtered['cnt'].sum()*100:.1f}%")

# ── MONTHLY TREND ────────────────────────────────────────────────────────────
monthly = filtered.groupby(["year","mnth"])["cnt"].mean().reset_index()

st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("#### Monthly Trend")

fig, ax = plt.subplots(figsize=(12,4))
for yr, color in [(2011,"#3b82f6"),(2012,"#f97316")]:
    sub = monthly[monthly["year"]==yr]
    ax.plot(sub["mnth"], sub["cnt"], marker="o", color=color, label=yr)

ax.legend()
ax.spines[["top","right"]].set_visible(False)
st.pyplot(fig)
plt.close()

st.markdown('</div>', unsafe_allow_html=True)

# ── SEASON & WEATHER ─────────────────────────────────────────────────────────
c1, c2 = st.columns(2)

with c1:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Season")

    s = filtered.groupby("season_label")["cnt"].mean()
    fig, ax = plt.subplots()
    ax.bar(s.index, s.values)
    ax.spines[["top","right"]].set_visible(False)
    st.pyplot(fig)
    plt.close()

    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Weather")

    w = filtered.groupby("weather_label")["cnt"].mean()
    fig, ax = plt.subplots()
    ax.bar(w.index, w.values)
    ax.tick_params(axis='x', rotation=20)
    ax.spines[["top","right"]].set_visible(False)
    st.pyplot(fig)
    plt.close()

    st.markdown('</div>', unsafe_allow_html=True)

# ── HEATMAP ──────────────────────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("#### Heatmap")

pivot = filtered.pivot_table(values="cnt", index="season_label", columns="weather_label")
fig, ax = plt.subplots()
sns.heatmap(pivot, annot=True, cmap="YlOrRd", ax=ax)

st.pyplot(fig)
plt.close()

st.markdown('</div>', unsafe_allow_html=True)

# ── SEGMENT ──────────────────────────────────────────────────────────────────
c3, c4 = st.columns([1,2])

with c3:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Segment")

    counts = filtered["segment"].value_counts()
    fig, ax = plt.subplots()
    ax.pie(counts, labels=counts.index, autopct="%1.1f%%")
    st.pyplot(fig)
    plt.close()

    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.markdown("#### Segment by Season")

    tab = pd.crosstab(filtered["season_label"], filtered["segment"])
    tab.plot(kind="bar", stacked=True, ax=plt.gca())
    plt.gca().spines[["top","right"]].set_visible(False)

    st.pyplot(plt.gcf())
    plt.close()

    st.markdown('</div>', unsafe_allow_html=True)

# ── TABLE ────────────────────────────────────────────────────────────────────
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("#### Summary")

summary = filtered.groupby("segment")[["cnt","casual","registered"]].mean().round(1)
st.dataframe(summary, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)
