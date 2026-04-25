import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import os

# ── Konfigurasi halaman ──────────────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚴",
    layout="wide",
    initial_sidebar_state="expanded",
)

sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams["figure.dpi"] = 100

# ── Helper: load data ────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    base = os.path.dirname(__file__)
    path = os.path.join(base, "main_data.csv")
    df = pd.read_csv(path)
    df["dteday"] = pd.to_datetime(df["dteday"])
    return df

# ── Load & preprocess ────────────────────────────────────────────────────────
try:
    main_df = load_data()
except FileNotFoundError:
    st.error("❌ File `main_data.csv` tidak ditemukan di folder `dashboard/`.")
    st.stop()

# Mapping label — pakai nama kolom ASLI dari day.csv
season_map  = {1: "Spring", 2: "Summer", 3: "Fall", 4: "Winter"}
weather_map = {1: "Clear", 2: "Mist/Cloudy", 3: "Light Rain/Snow", 4: "Heavy Rain"}
weekday_map = {0: "Sun", 1: "Mon", 2: "Tue", 3: "Wed", 4: "Thu", 5: "Fri", 6: "Sat"}

# FIX: kolom cuaca di day.csv namanya 'weathersit', bukan 'weather'
col_map = {
    "season_label":  ("season",     season_map),
    "weather_label": ("weathersit", weather_map),
    "weekday_label": ("weekday",    weekday_map),
}
for new_col, (src_col, mapping) in col_map.items():
    if src_col in main_df.columns and new_col not in main_df.columns:
        main_df[new_col] = main_df[src_col].map(mapping)

if "year" not in main_df.columns and "yr" in main_df.columns:
    main_df["year"] = main_df["yr"].map({0: 2011, 1: 2012})
if "temp_c" not in main_df.columns and "temp" in main_df.columns:
    main_df["temp_c"] = main_df["temp"] * 41
if "hum_pct" not in main_df.columns and "hum" in main_df.columns:
    main_df["hum_pct"] = main_df["hum"] * 100

def segment_usage(cnt):
    if cnt < 2000:
        return "Low Usage"
    elif cnt <= 5000:
        return "Medium Usage"
    return "High Usage"

main_df["usage_segment"] = main_df["cnt"].apply(segment_usage)

# ── Sidebar filter ───────────────────────────────────────────────────────────
with st.sidebar:
    st.title("🚴 Bike Sharing\nDashboard")
    st.markdown("---")

    years = sorted(main_df["year"].unique().tolist())
    selected_years = st.multiselect("Pilih Tahun", years, default=years)

    seasons = sorted(main_df["season_label"].unique().tolist())
    selected_seasons = st.multiselect("Pilih Musim", seasons, default=seasons)

    date_min = main_df["dteday"].min().date()
    date_max = main_df["dteday"].max().date()
    date_range = st.date_input("Rentang Tanggal", [date_min, date_max],
                               min_value=date_min, max_value=date_max)

    st.markdown("---")
    st.caption("Sumber: Capital Bikeshare, Washington D.C. (2011–2012)")

# Filter data
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
st.title("🚴 Analisis Penyewaan Sepeda – Capital Bikeshare")
st.markdown("Dashboard ini menampilkan hasil analisis data penyewaan sepeda di Washington D.C., 2011–2012.")

# ── Metric cards ─────────────────────────────────────────────────────────────
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Penyewaan", f"{filtered['cnt'].sum():,.0f}")
with col2:
    st.metric("Rata-rata/Hari", f"{filtered['cnt'].mean():,.0f}")
with col3:
    st.metric("Penyewaan Tertinggi", f"{filtered['cnt'].max():,.0f}")
with col4:
    casual_pct = filtered["casual"].sum() / filtered["cnt"].sum() * 100 if filtered["cnt"].sum() > 0 else 0
    st.metric("% Pengguna Kasual", f"{casual_pct:.1f}%")

st.markdown("---")

# ── Tren Bulanan ─────────────────────────────────────────────────────────────
st.subheader("📈 Tren Penyewaan Bulanan")
monthly = filtered.groupby(["year", "mnth"])["cnt"].mean().reset_index()

fig, ax = plt.subplots(figsize=(12, 4))
for yr, color in [(2011, "#1565C0"), (2012, "#E65100")]:
    sub = monthly[monthly["year"] == yr]
    if not sub.empty:
        ax.plot(sub["mnth"], sub["cnt"], marker="o", linewidth=2.5,
                color=color, label=str(yr))
        ax.fill_between(sub["mnth"], sub["cnt"], alpha=0.1, color=color)

ax.set_xticks(range(1, 13))
ax.set_xticklabels(["Jan","Feb","Mar","Apr","Mei","Jun",
                    "Jul","Agu","Sep","Okt","Nov","Des"], fontsize=9)
ax.set_ylabel("Rata-rata Penyewaan/Hari")
ax.legend()
ax.spines[["top", "right"]].set_visible(False)
st.pyplot(fig)
plt.close()

# ── Musim & Cuaca ─────────────────────────────────────────────────────────────
st.subheader("🌤️ Pengaruh Musim & Cuaca (Pertanyaan 1)")
c1, c2 = st.columns(2)

with c1:
    season_order   = ["Spring", "Summer", "Fall", "Winter"]
    palette_season = {"Spring": "#4CAF50", "Summer": "#FF9800", "Fall": "#F44336", "Winter": "#2196F3"}
    s_agg = (filtered.groupby("season_label")["cnt"].mean()
             .reindex([s for s in season_order if s in filtered["season_label"].unique()])
             .reset_index())
    fig2, ax2 = plt.subplots(figsize=(5.5, 4))
    bars = ax2.bar(s_agg["season_label"], s_agg["cnt"],
                   color=[palette_season.get(s, "gray") for s in s_agg["season_label"]],
                   edgecolor="white", linewidth=1.5)
    for bar, val in zip(bars, s_agg["cnt"]):
        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 50,
                 f"{val:,.0f}", ha="center", fontweight="bold", fontsize=9)
    ax2.set_title("Rata-rata Penyewaan per Musim", fontweight="bold")
    ax2.set_ylabel("Unit/Hari")
    ax2.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig2)
    plt.close()

with c2:
    weather_order   = ["Clear", "Mist/Cloudy", "Light Rain/Snow"]
    palette_weather = {"Clear": "#FFD700", "Mist/Cloudy": "#90A4AE", "Light Rain/Snow": "#64B5F6"}
    # FIX: filter Heavy Rain dulu, baru groupby
    w_filtered = filtered[filtered["weather_label"].isin(weather_order)]
    w_agg = (w_filtered.groupby("weather_label")["cnt"].mean()
             .reindex([w for w in weather_order if w in w_filtered["weather_label"].unique()])
             .reset_index())
    fig3, ax3 = plt.subplots(figsize=(5.5, 4))
    bars3 = ax3.bar(w_agg["weather_label"], w_agg["cnt"],
                    color=[palette_weather.get(w, "gray") for w in w_agg["weather_label"]],
                    edgecolor="white", linewidth=1.5)
    for bar, val in zip(bars3, w_agg["cnt"]):
        ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 30,
                 f"{val:,.0f}", ha="center", fontweight="bold", fontsize=9)
    ax3.set_title("Rata-rata Penyewaan per Cuaca", fontweight="bold")
    ax3.set_ylabel("Unit/Hari")
    ax3.tick_params(axis="x", labelsize=8)
    ax3.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig3)
    plt.close()

# ── Heatmap Musim × Cuaca ─────────────────────────────────────────────────────
st.subheader("🌡️ Heatmap: Musim × Kondisi Cuaca")
hm_filtered = filtered[filtered["weather_label"].isin(weather_order)]
pivot_data = (hm_filtered
              .groupby(["season_label", "weather_label"])["cnt"].mean()
              .unstack()
              .reindex(index=[s for s in season_order if s in filtered["season_label"].unique()],
                       columns=[w for w in weather_order if w in hm_filtered["weather_label"].unique()]))
if not pivot_data.empty:
    fig4, ax4 = plt.subplots(figsize=(8, 3.5))
    sns.heatmap(pivot_data, annot=True, fmt=".0f", cmap="YlOrRd",
                linewidths=0.5, ax=ax4, annot_kws={"size": 11})
    ax4.set_xlabel("Kondisi Cuaca")
    ax4.set_ylabel("Musim")
    ax4.tick_params(axis="x", rotation=10)
    ax4.tick_params(axis="y", rotation=0)
    st.pyplot(fig4)
    plt.close()

# ── Segmentasi ────────────────────────────────────────────────────────────────
st.markdown("---")
st.subheader("📊 Segmentasi Penggunaan (Analisis Lanjutan)")
seg_order  = ["Low Usage", "Medium Usage", "High Usage"]
seg_colors = ["#EF9A9A", "#FFD54F", "#A5D6A7"]

c3, c4 = st.columns([1, 2])
with c3:
    counts = filtered["usage_segment"].value_counts().reindex(seg_order, fill_value=0)
    fig5, ax5 = plt.subplots(figsize=(4, 4))
    ax5.pie(counts, labels=[f"{s}\n({v})" for s, v in zip(seg_order, counts)],
            colors=seg_colors, autopct="%1.1f%%", startangle=90,
            wedgeprops={"edgecolor": "white", "linewidth": 2})
    ax5.set_title("Distribusi Segmen", fontweight="bold")
    st.pyplot(fig5)
    plt.close()

with c4:
    seg_season_tab = pd.crosstab(filtered["season_label"], filtered["usage_segment"])
    seg_season_tab = seg_season_tab.reindex(
        index=[s for s in season_order if s in seg_season_tab.index],
        columns=[s for s in seg_order if s in seg_season_tab.columns],
        fill_value=0
    )
    fig6, ax6 = plt.subplots(figsize=(7, 4))
    bottom = np.zeros(len(seg_season_tab))
    for col, color in zip(seg_order, seg_colors):
        if col in seg_season_tab.columns:
            vals = seg_season_tab[col].values
            ax6.bar(seg_season_tab.index, vals, bottom=bottom, color=color, label=col, edgecolor="white")
            for i, (v, b) in enumerate(zip(vals, bottom)):
                if v > 2:
                    ax6.text(i, b + v/2, str(v), ha="center", va="center",
                             fontsize=9, fontweight="bold")
            bottom += vals
    ax6.set_title("Jumlah Hari per Segmen & Musim", fontweight="bold")
    ax6.set_ylabel("Jumlah Hari")
    ax6.legend(fontsize=9)
    ax6.spines[["top", "right"]].set_visible(False)
    st.pyplot(fig6)
    plt.close()

# ── Tabel ringkasan ────────────────────────────────────────────────────────────
st.markdown("---")
with st.expander("📋 Lihat Ringkasan Data Statistik"):
    summary = filtered.groupby("usage_segment")[["cnt", "casual", "registered", "temp_c", "hum_pct"]].mean().round(1)
    st.dataframe(summary.style.background_gradient(cmap="YlGn", subset=["cnt"]))

st.markdown("---")
st.caption("© 2024 Proyek Analisis Data | Belajar Fundamental Analisis Data – Dicoding Indonesia")
