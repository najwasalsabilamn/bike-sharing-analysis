import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(page_title="Bike Sharing Dashboard", page_icon="🚲", layout="wide")

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
.main {background-color: #F8FAFC;}
.metric-card {background:white;padding:15px;border-radius:15px;box-shadow:0 4px 12px rgba(0,0,0,0.05);transition:0.2s;}
.metric-card:hover {transform:scale(1.03);}
</style>
""", unsafe_allow_html=True)

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    day_df = pd.read_csv('dashboard/main_data.csv')
    hour_df = pd.read_csv('data/hour.csv')

    season_map = {1:'Spring',2:'Summer',3:'Fall',4:'Winter'}
    weather_map = {1:'Clear',2:'Mist',3:'Light Snow/Rain',4:'Heavy Rain'}
    weekday_map = {0:'Sun',1:'Mon',2:'Tue',3:'Wed',4:'Thu',5:'Fri',6:'Sat'}
    yr_map = {0:'2011',1:'2012'}

    for df in [day_df,hour_df]:
        df['dteday']=pd.to_datetime(df['dteday'])
        df['year']=df['dteday'].dt.year
        df['month']=df['dteday'].dt.month
        df['season_label']=df['season'].map(season_map)
        df['weather_label']=df['weathersit'].map(weather_map)
        df['weekday_label']=df['weekday'].map(weekday_map)
        df['yr_label']=df['yr'].map(yr_map)

    p33=day_df['cnt'].quantile(0.33)
    p67=day_df['cnt'].quantile(0.67)
    day_df['usage_cluster']=pd.cut(day_df['cnt'],bins=[0,p33,p67,day_df['cnt'].max()+1],labels=['Low Usage','Medium Usage','High Usage'])

    return day_df,hour_df


day_df,hour_df=load_data()

# ============================================================
# SIDEBAR (FILTERS)
# ============================================================
st.sidebar.title("🚲 Bike Sharing")

selected_yr = st.sidebar.selectbox("Tahun", ['Semua','2011','2012'])
selected_month = st.sidebar.multiselect(
    "Bulan",
    sorted(day_df['month'].unique()),
    default=sorted(day_df['month'].unique())
)

season_options = ['Semua'] + sorted(day_df['season_label'].dropna().unique().tolist())
selected_season = st.sidebar.selectbox("Musim", season_options)

weather_options = ['Semua'] + sorted(day_df['weather_label'].dropna().unique().tolist())
selected_weather = st.sidebar.selectbox("Cuaca", weather_options)

# ============================================================
# FILTER
# ============================================================
filtered_day = day_df.copy()
filtered_hour = hour_df.copy()

if selected_yr != 'Semua':
    filtered_day = filtered_day[filtered_day['yr_label'] == selected_yr]
    filtered_hour = filtered_hour[filtered_hour['yr_label'] == selected_yr]

if selected_month:
    filtered_day = filtered_day[filtered_day['month'].isin(selected_month)]
    filtered_hour = filtered_hour[filtered_hour['month'].isin(selected_month)]

if selected_season != 'Semua':
    filtered_day = filtered_day[filtered_day['season_label'] == selected_season]
    filtered_hour = filtered_hour[filtered_hour['season_label'] == selected_season]

if selected_weather != 'Semua':
    filtered_day = filtered_day[filtered_day['weather_label'] == selected_weather]
    filtered_hour = filtered_hour[filtered_hour['weather_label'] == selected_weather]

# ============================================================
# HEADER
# ============================================================
st.markdown("""<h1 style='text-align:center;'>🚲 Bike Sharing Dashboard</h1>""",unsafe_allow_html=True)

# ============================================================
# KPI
# ============================================================
def metric_card(title,val,sub):
    st.markdown(f"""<div class='metric-card'><h4>{title}</h4><h2>{val}</h2><p>{sub}</p></div>""",unsafe_allow_html=True)

c1,c2,c3,c4=st.columns(4)

total = filtered_day['cnt'].sum()
avg = filtered_day['cnt'].mean()
casual = filtered_day['casual'].sum()
reg = filtered_day['registered'].sum()

with c1: metric_card("Total", f"{total:,.0f}", "Ride")
with c2: metric_card("Avg", f"{avg:,.0f}", "Daily")
with c3: metric_card("Casual", f"{casual:,.0f}", f"{(casual/total if total else 0):.1%}")
with c4: metric_card("Registered", f"{reg:,.0f}", f"{(reg/total if total else 0):.1%}")

st.markdown("---")

# ============================================================
# TREND
# ============================================================
if not filtered_day.empty:
    monthly = filtered_day.groupby(['year','month'],as_index=False)['cnt'].sum()
    monthly['period'] = monthly['year'].astype(str)+'-'+monthly['month'].astype(str).str.zfill(2)

    fig = px.line(monthly,x='period',y='cnt',color='year',markers=True,title="📈 Tren")
    st.plotly_chart(fig,use_container_width=True)

    peak = monthly.loc[monthly['cnt'].idxmax()]
    low = monthly.loc[monthly['cnt'].idxmin()]
    st.info(f"Peak: {peak['period']} | Low: {low['period']}")
else:
    st.warning("Data kosong untuk filter yang dipilih.")

# ============================================================
# CUACA & MUSIM (2 COL)
# ============================================================
colA,colB = st.columns(2)

with colA:
    if not filtered_day.empty:
        weather_avg = filtered_day.groupby('weather_label')['cnt'].mean().reset_index()
        fig2 = px.bar(weather_avg,x='weather_label',y='cnt',color='weather_label',title="🌤️ Cuaca")
        st.plotly_chart(fig2,use_container_width=True)

        top_w = weather_avg.loc[weather_avg['cnt'].idxmax()]
        st.markdown(f"💡 Terbaik: {top_w['weather_label']}")

with colB:
    if not filtered_day.empty:
        season_avg = filtered_day.groupby('season_label')['cnt'].mean().reset_index()
        fig3 = px.bar(season_avg,x='season_label',y='cnt',color='season_label',title="🌸 Musim")
        st.plotly_chart(fig3,use_container_width=True)

        top_s = season_avg.loc[season_avg['cnt'].idxmax()]
        st.markdown(f"💡 Tertinggi: {top_s['season_label']}")

# ============================================================
# JAM
# ============================================================
if not filtered_hour.empty:
    hourly = filtered_hour.groupby('hr')['cnt'].mean().reset_index()
    fig4 = px.line(hourly,x='hr',y='cnt',markers=True,title="⏰ Jam")
    st.plotly_chart(fig4,use_container_width=True)

# ============================================================
# HEATMAP
# ============================================================
if not filtered_hour.empty:
    pivot = filtered_hour.pivot_table(index='weekday_label',columns='hr',values='cnt',aggfunc='mean')
    fig5 = px.imshow(pivot,aspect='auto',color_continuous_scale='YlOrRd',title="🔥 Heatmap")
    st.plotly_chart(fig5,use_container_width=True)

# ============================================================
# CLUSTER
# ============================================================
if not filtered_day.empty:
    cluster_avg = filtered_day.groupby('usage_cluster')['cnt'].mean().reset_index()
    fig6 = px.bar(cluster_avg,x='usage_cluster',y='cnt',color='usage_cluster',title="🔵 Cluster")
    st.plotly_chart(fig6,use_container_width=True)

# ============================================================
# DISTRIBUTION
# ============================================================
if total > 0:
    pct = casual/total
    st.progress(int(pct*100))
    st.caption(f"Casual {pct:.1%}")
