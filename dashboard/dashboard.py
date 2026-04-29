import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# ============================================================
# CONFIG
# ============================================================
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

plt.rcParams.update({
    'axes.spines.top': False,
    'axes.spines.right': False,
})

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
    ['Semua'] + list(day_df['season_label'].dropna().unique())
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
st.markdown("Dashboard interaktif untuk memahami pola penggunaan sepeda")
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

# ============================================================
# EXECUTIVE SUMMARY
# ============================================================
st.markdown("### 🧠 Ringkasan Utama")

st.info(
    f"""
- Aktivitas berada di level **{"tinggi" if avg>5000 else "sedang" if avg>3000 else "rendah"}**
- Cuaca dan musim sangat mempengaruhi penggunaan
- Ada pola jam penggunaan yang konsisten

💡 Sepeda digunakan sebagai bagian dari aktivitas harian.
"""
)

# ============================================================
# INTERAKTIF CONTROL
# ============================================================
metric_option = st.selectbox(
    "📊 Pilih jenis data:",
    ["Total (cnt)", "Casual", "Registered"]
)

metric_map = {
    "Total (cnt)": "cnt",
    "Casual": "casual",
    "Registered": "registered"
}

selected_metric = metric_map[metric_option]

chart_type = st.radio(
    "📊 Pilih jenis grafik:",
    ["Line Chart", "Bar Chart"],
    horizontal=True
)

# ============================================================
# TREND
# ============================================================
st.subheader("📈 Tren Bulanan")

monthly = filtered_day.groupby(['year','month'])[selected_metric].sum().reset_index()
monthly['period'] = monthly['year'].astype(str)+'-'+monthly['month'].astype(str)

fig, ax = plt.subplots(figsize=(10,4))

for yr, grp in monthly.groupby('year'):
    if chart_type == "Line Chart":
        ax.plot(grp['period'], grp[selected_metric], marker='o', label=yr)
    else:
        ax.bar(grp['period'], grp[selected_metric], label=yr)

ax.tick_params(axis='x', rotation=45)
ax.legend()
st.pyplot(fig)

peak = monthly.loc[monthly[selected_metric].idxmax()]
low = monthly.loc[monthly[selected_metric].idxmin()]

st.info(f"Puncak: {peak['period']} | Terendah: {low['period']}")

# Ranking
st.markdown("### 🏆 Bulan Teratas")

top_n = st.slider("Top N:", 3, 12, 5)
top_data = monthly.sort_values(selected_metric, ascending=False).head(top_n)

st.dataframe(top_data[['period', selected_metric]])

# ============================================================
# CUACA
# ============================================================
st.subheader("🌤️ Cuaca")

selected_weather = st.multiselect(
    "Pilih cuaca:",
    filtered_day['weather_label'].dropna().unique(),
    default=filtered_day['weather_label'].dropna().unique()
)

weather_filtered = filtered_day[
    filtered_day['weather_label'].isin(selected_weather)
]

weather_avg = weather_filtered.groupby('weather_label')[selected_metric].mean().reset_index()

fig2, ax2 = plt.subplots()
ax2.bar(weather_avg['weather_label'], weather_avg[selected_metric])
st.pyplot(fig2)

# ============================================================
# JAM
# ============================================================
st.subheader("⏰ Pola Jam")

hourly = filtered_hour.groupby('hr')[selected_metric].mean()

fig3, ax3 = plt.subplots()
ax3.plot(hourly.index, hourly.values)
st.pyplot(fig3)

peak_hour = hourly.idxmax()

selected_hour = st.slider("Pilih jam:", 0, 23, int(peak_hour))
hour_val = hourly[selected_hour]

st.progress(int(hour_val/hourly.max()*100))
st.write(f"Jam {selected_hour}:00 → {hour_val:.0f}")

# ============================================================
# HEATMAP
# ============================================================
st.subheader("🔥 Heatmap")

pivot = filtered_hour.pivot_table(index='weekday_label', columns='hr', values=selected_metric)

fig4, ax4 = plt.subplots(figsize=(12,4))
sns.heatmap(pivot, cmap='YlOrRd', ax=ax4)
st.pyplot(fig4)

# ============================================================
# CLUSTER
# ============================================================
st.subheader("🔵 Segmentasi")

cluster = filtered_day['usage_cluster'].value_counts()

fig5, ax5 = plt.subplots()
ax5.pie(cluster, labels=cluster.index, autopct='%1.1f%%')
st.pyplot(fig5)

st.write(f"Mayoritas: {cluster.idxmax()}")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.caption("Dashboard Interaktif Bike Sharing")
