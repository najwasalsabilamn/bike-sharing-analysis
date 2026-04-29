import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

plt.rcParams.update({
    'axes.spines.top': False,
    'axes.spines.right': False,
})

CLUSTER_COLORS = {
    'Low Usage': '#EF9A9A',
    'Medium Usage': '#FFE082',
    'High Usage': '#A5D6A7'
}

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    day_df  = pd.read_csv('dashboard/main_data.csv')
    hour_df = pd.read_csv('data/hour.csv')

    season_map  = {1:'Spring',2:'Summer',3:'Fall',4:'Winter'}
    weather_map = {1:'Clear',2:'Mist',3:'Light Rain',4:'Heavy Rain'}
    weekday_map = {0:'Sun',1:'Mon',2:'Tue',3:'Wed',4:'Thu',5:'Fri',6:'Sat'}
    yr_map      = {0:'2011',1:'2012'}

    for df in [day_df, hour_df]:
        df['dteday'] = pd.to_datetime(df['dteday'])
        df['year'] = df['dteday'].dt.year
        df['month'] = df['dteday'].dt.month
        df['season_label'] = df['season'].map(season_map)
        df['weather_label'] = df['weathersit'].map(weather_map)
        df['weekday_label'] = df['weekday'].map(weekday_map)
        df['yr_label'] = df['yr'].map(yr_map)

    # clustering
    p33 = day_df['cnt'].quantile(0.33)
    p67 = day_df['cnt'].quantile(0.67)

    day_df['usage_cluster'] = pd.cut(
        day_df['cnt'],
        bins=[0, p33, p67, day_df['cnt'].max()+1],
        labels=['Low Usage','Medium Usage','High Usage']
    )

    return day_df, hour_df

day_df, hour_df = load_data()

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.title("🚲 Bike Sharing")
selected_yr = st.sidebar.selectbox("Tahun", ['Semua','2011','2012'])
selected_season = st.sidebar.selectbox(
    "Musim",
    ['Semua'] + list(day_df['season_label'].unique())
)

# ============================================================
# FILTER
# ============================================================
filtered_day = day_df.copy()
filtered_hour = hour_df.copy()

if selected_yr != 'Semua':
    filtered_day = filtered_day[filtered_day['yr_label']==selected_yr]
    filtered_hour = filtered_hour[filtered_hour['yr_label']==selected_yr]

if selected_season != 'Semua':
    filtered_day = filtered_day[filtered_day['season_label']==selected_season]

# ============================================================
# HEADER
# ============================================================
st.title("🚲 Bike Sharing Dashboard")
st.markdown("---")

# ============================================================
# METRIC
# ============================================================
col1,col2,col3,col4 = st.columns(4)

total = filtered_day['cnt'].sum()
avg = filtered_day['cnt'].mean()

col1.metric("Total", f"{total:,.0f}")
col2.metric("Rata-rata", f"{avg:,.0f}")
col3.metric("Max", f"{filtered_day['cnt'].max():,.0f}")
col4.metric("Min", f"{filtered_day['cnt'].min():,.0f}")

# Insight global
if avg > 5000:
    st.success("📈 Aktivitas tinggi")
elif avg > 3000:
    st.info("📊 Aktivitas stabil")
else:
    st.warning("📉 Aktivitas rendah")

# ============================================================
# TREND
# ============================================================
st.subheader("📈 Tren Bulanan")

monthly = filtered_day.groupby(['year','month'])['cnt'].sum().reset_index()
monthly['period'] = monthly['year'].astype(str)+'-'+monthly['month'].astype(str)

fig, ax = plt.subplots(figsize=(10,4))
for yr, grp in monthly.groupby('year'):
    ax.plot(grp['period'], grp['cnt'], marker='o', label=yr)

ax.tick_params(axis='x', rotation=45)
ax.legend()
st.pyplot(fig)

# Insight tren
peak = monthly.loc[monthly['cnt'].idxmax()]
low = monthly.loc[monthly['cnt'].idxmin()]

st.info(f"📊 Tertinggi: {peak['period']} ({peak['cnt']:,.0f}) | Terendah: {low['period']} ({low['cnt']:,.0f})")

# ============================================================
# CUACA & MUSIM
# ============================================================
st.subheader("🌤️ Cuaca & Musim")

colA,colB = st.columns(2)

with colA:
    weather_avg = filtered_day.groupby('weather_label')['cnt'].mean().reset_index()
    fig2, ax2 = plt.subplots()
    ax2.bar(weather_avg['weather_label'], weather_avg['cnt'])
    st.pyplot(fig2)

with colB:
    season_avg = filtered_day.groupby('season_label')['cnt'].mean().reset_index()
    fig3, ax3 = plt.subplots()
    ax3.bar(season_avg['season_label'], season_avg['cnt'])
    st.pyplot(fig3)

# Insight
best_weather = weather_avg.loc[weather_avg['cnt'].idxmax()]
best_season = season_avg.loc[season_avg['cnt'].idxmax()]

st.success(f"🌟 Terbaik: {best_weather['weather_label']} & {best_season['season_label']}")

# ============================================================
# JAM
# ============================================================
st.subheader("⏰ Pola Jam")

hourly = filtered_hour.groupby('hr')['cnt'].mean()

fig4, ax4 = plt.subplots()
ax4.plot(hourly.index, hourly.values)
st.pyplot(fig4)

peak_hour = hourly.idxmax()
st.info(f"⏰ Jam puncak: {peak_hour}:00")

# ============================================================
# HEATMAP
# ============================================================
st.subheader("🔥 Heatmap")

pivot = filtered_hour.pivot_table(index='weekday_label', columns='hr', values='cnt')

fig5, ax5 = plt.subplots(figsize=(12,4))
sns.heatmap(pivot, cmap='YlOrRd', ax=ax5)
st.pyplot(fig5)

# Insight heatmap
max_heat = pivot.stack().idxmax()
st.info(f"🔥 Puncak: {max_heat[0]} jam {max_heat[1]}")

# ============================================================
# CLUSTER
# ============================================================
st.subheader("🔵 Clustering")

cluster = filtered_day['usage_cluster'].value_counts()

fig6, ax6 = plt.subplots()
ax6.pie(cluster, labels=cluster.index, autopct='%1.1f%%')
st.pyplot(fig6)

st.info(f"📊 Dominan: {cluster.idxmax()}")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption("Dashboard Bike Sharing")
