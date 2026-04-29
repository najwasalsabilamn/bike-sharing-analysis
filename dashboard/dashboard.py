import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide"
)

# ============================================================
# CUSTOM CSS
# ============================================================
st.markdown("""
<style>
.main {background-color: #F8FAFC;}
.block-container {padding-top: 2rem;}
.metric-card {
    background: white;
    padding: 15px;
    border-radius: 15px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    transition: 0.2s;
}
.metric-card:hover {transform: scale(1.03);}
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    day_df = pd.read_csv('dashboard/main_data.csv')
    hour_df = pd.read_csv('data/hour.csv')

    season_map = {1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'}
    weather_map = {1:'Clear', 2:'Mist', 3:'Light Snow/Rain', 4:'Heavy Rain'}
    weekday_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
    yr_map = {0:'2011', 1:'2012'}

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
selected_yr = st.sidebar.selectbox("Pilih Tahun", ['Semua','2011','2012'])
selected_month = st.sidebar.multiselect(
    "Pilih Bulan",
    sorted(day_df['month'].unique()),
    default=sorted(day_df['month'].unique())
)

# ============================================================
# FILTER
# ============================================================
filtered_day = day_df.copy()
filtered_hour = hour_df.copy()

if selected_yr != 'Semua':
    filtered_day = filtered_day[filtered_day['yr_label'] == selected_yr]
    filtered_hour = filtered_hour[filtered_hour['yr_label'] == selected_yr]

filtered_day = filtered_day[filtered_day['month'].isin(selected_month)]
filtered_hour = filtered_hour[filtered_hour['month'].isin(selected_month)]

# ============================================================
# HEADER
# ============================================================
st.markdown("""
<h1 style='text-align:center;'>🚲 Bike Sharing Dashboard</h1>
<p style='text-align:center;color:gray;'>Dashboard interaktif & analisis penggunaan sepeda</p>
""", unsafe_allow_html=True)

# ============================================================
# KPI
# ============================================================
def metric_card(title, value, subtitle):
    st.markdown(f"""
    <div class='metric-card'>
        <h4>{title}</h4>
        <h2>{value}</h2>
        <p style='color:gray'>{subtitle}</p>
    </div>
    """, unsafe_allow_html=True)

col1,col2,col3,col4 = st.columns(4)

total = filtered_day['cnt'].sum()
avg = filtered_day['cnt'].mean()
casual = filtered_day['casual'].sum()
reg = filtered_day['registered'].sum()

with col1: metric_card("Total Ride", f"{total:,.0f}", "Total")
with col2: metric_card("Avg Daily", f"{avg:,.0f}", "Rata-rata")
with col3: metric_card("Casual", f"{casual:,.0f}", f"{casual/total:.1%}")
with col4: metric_card("Registered", f"{reg:,.0f}", f"{reg/total:.1%}")

st.markdown("---")

# ============================================================
# TREND
# ============================================================
monthly = filtered_day.groupby(['year','month'], as_index=False)['cnt'].sum()
monthly['period'] = monthly['year'].astype(str) + '-' + monthly['month'].astype(str)

fig = px.line(monthly, x='period', y='cnt', color='year', markers=True,
              title="📈 Tren Peminjaman Bulanan")
st.plotly_chart(fig, use_container_width=True)

peak = monthly.loc[monthly['cnt'].idxmax()]
st.info(f"📌 Puncak di {peak['period']} dengan {peak['cnt']:,.0f} peminjaman")

# ============================================================
# CUACA
# ============================================================
weather_avg = filtered_day.groupby('weather_label')['cnt'].mean().reset_index()
fig2 = px.bar(weather_avg, x='weather_label', y='cnt', color='weather_label',
              title="🌤️ Pengaruh Cuaca")
st.plotly_chart(fig2, use_container_width=True)

# ============================================================
# POLA JAM
# ============================================================
st.subheader("⏰ Pola Peminjaman per Jam")

hourly = filtered_hour.groupby('hr')['cnt'].mean().reset_index()
fig3 = px.line(hourly, x='hr', y='cnt', markers=True,
               title="Rata-rata Peminjaman per Jam")
st.plotly_chart(fig3, use_container_width=True)

# ============================================================
# HEATMAP
# ============================================================
pivot = filtered_hour.pivot_table(index='weekday_label', columns='hr', values='cnt', aggfunc='mean')
fig4 = px.imshow(pivot, aspect='auto', color_continuous_scale='YlOrRd',
                 title="🔥 Heatmap Hari vs Jam")
st.plotly_chart(fig4, use_container_width=True)

# ============================================================
# CLUSTER
# ============================================================
st.subheader("🔵 Clustering Penggunaan")
cluster_avg = filtered_day.groupby('usage_cluster')['cnt'].mean().reset_index()
fig5 = px.bar(cluster_avg, x='usage_cluster', y='cnt', color='usage_cluster',
              title="Rata-rata Peminjaman per Cluster")
st.plotly_chart(fig5, use_container_width=True)

# ============================================================
# DISTRIBUTION
# ============================================================
st.subheader("Distribusi Pengguna")
pct = casual/total
st.progress(int(pct*100))
st.caption(f"Casual: {pct:.1%}")

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown("<p style='text-align:center;color:gray'>Final Enhanced Dashboard</p>", unsafe_allow_html=True)
