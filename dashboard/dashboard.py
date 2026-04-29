import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ============================================================
# KONFIGURASI HALAMAN & CSS KUSTOM
# ============================================================
st.set_page_config(
    page_title="BikeFlow | Analytics Dashboard",
    page_icon="🚲",
    layout="wide"
)

# Custom CSS untuk tampilan lebih modern
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stMetric { 
        background-color: #ffffff; 
        padding: 15px; 
        border-radius: 10px; 
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    [data-testid="stMetricValue"] { font-size: 28px !important; color: #1e88e5; }
    div[data-testid="stVerticalBlock"] > div[style*="flex-direction: column;"] > div[data-testid="stVerticalBlock"] {
        border: 1px solid #e6e9ef;
        padding: 20px;
        border-radius: 15px;
        background-color: white;
    }
    </style>
    """, unsafe_allow_html=True)

# Styling matplotlib
plt.rcParams.update({
    'axes.facecolor': '#ffffff',
    'figure.facecolor': '#ffffff',
    'axes.spines.top': False,
    'axes.spines.right': False,
    'font.family': 'sans-serif'
})

# ============================================================
# LOAD DATA
# =============================
@st.cache_data
def load_data():
    # Pastikan file ada di path yang benar
    day_df = pd.read_csv('dashboard/main_data.csv')
    hour_df = pd.read_csv('data/hour.csv')

    season_map = {1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'}
    weather_map = {1:'Clear', 2:'Mist', 3:'Light Snow/Rain', 4:'Heavy Rain'}
    weekday_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
    yr_map = {0:'2011', 1:'2012'}

    for df in [day_df, hour_df]:
        df['dteday'] = pd.to_datetime(df['dteday'])
        df['yr_label'] = df['yr'].map(yr_map)
        df['season_label'] = df['season'].map(season_map)
        df['weather_label'] = df['weathersit'].map(weather_map)
        df['weekday_label'] = df['weekday'].map(weekday_map)
    
    # Clustering sederhana
    p33, p67 = day_df['cnt'].quantile([0.33, 0.67])
    day_df['usage_cluster'] = pd.cut(
        day_df['cnt'], bins=[0, p33, p67, day_df['cnt'].max() + 1],
        labels=['Low Usage', 'Medium Usage', 'High Usage']
    )
    return day_df, hour_df

day_df, hour_df = load_data()

# ============================================================
# SIDEBAR DENGAN INTERAKSI LEBIH OKE
# ============================================================
with st.sidebar:
    st.image("https://images.unsplash.com/photo-1485965120184-e220f721d03e?auto=format&fit=crop&q=80&w=300", use_column_width=True)
    st.title("🚲 BikeFlow")
    st.caption("Monitoring Dashboard v2.1")
    
    st.markdown("---")
    # Filter Rentang Tanggal
    min_date = day_df['dteday'].min()
    max_date = day_df['dteday'].max()
    
    start_date, end_date = st.date_input(
        "Pilih Rentang Waktu:",
        value=[min_date, max_date],
        min_value=min_date,
        max_value=max_date
    )
    
    selected_season = st.multiselect(
        "Pilih Musim:", 
        options=day_df['season_label'].unique(),
        default=day_df['season_label'].unique()
    )

# Filter Data Berdasarkan Sidebar
mask = (day_df['dteday'] >= pd.Timestamp(start_date)) & \
       (day_df['dteday'] <= pd.Timestamp(end_date)) & \
       (day_df['season_label'].isin(selected_season))
filtered_day = day_df.loc[mask]
filtered_hour = hour_df[hour_df['dteday'].isin(filtered_day['dteday'])]

# ============================================================
# MAIN CONTENT
# ============================================================
st.title("🚲 Bike Sharing Analytics")
st.markdown(f"Menganalisis penggunaan dari **{start_date}** hingga **{end_date}**")

# KPI dengan Container Berwarna
kpi1, kpi2, kpi3, kpi4 = st.columns(4)
with kpi1:
    st.metric("Total Rides", f"{filtered_day['cnt'].sum():,.0f}")
with kpi2:
    st.metric("Daily Avg", f"{filtered_day['cnt'].mean():,.0f}")
with kpi3:
    registered_pct = (filtered_day['registered'].sum() / filtered_day['cnt'].sum()) * 100
    st.metric("Registered User", f"{registered_pct:.1f}%", delta="Loyalty")
with kpi4:
    casual_pct = (filtered_day['casual'].sum() / filtered_day['cnt'].sum()) * 100
    st.metric("Casual User", f"{casual_pct:.1f}%", delta_color="normal")

st.markdown("### 📊 Ringkasan Visual")

# Grid Layout untuk Grafik Utama
col_left, col_right = st.columns([2, 1])

with col_left:
    with st.container(border=True):
        st.subheader("Tren Peminjaman Waktu ke Waktu")
        fig, ax = plt.subplots(figsize=(10, 4))
        # Resample per minggu agar garis lebih smooth (tidak terlalu 'noisy')
        resampled_data = filtered_day.set_index('dteday')['cnt'].resample('W').mean()
        ax.plot(resampled_data.index, resampled_data.values, color='#1e88e5', linewidth=2.5)
        ax.fill_between(resampled_data.index, resampled_data.values, alpha=0.1, color='#1e88e5')
        ax.set_ylabel("Rata-rata Peminjaman")
        st.pyplot(fig)

with col_right:
    with st.container(border=True):
        st.subheader("Distribusi User")
        # Pie chart donat untuk proporsi user
        fig_pie, ax_pie = plt.subplots(figsize=(4, 4))
        labels = ['Registered', 'Casual']
        sizes = [filtered_day['registered'].sum(), filtered_day['casual'].sum()]
        ax_pie.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
                   colors=['#1e88e5', '#ffb74d'], pctdistance=0.85, 
                   wedgeprops={'width': 0.3, 'edgecolor': 'w'})
        st.pyplot(fig_pie)

# Heatmap & Jam Section
st.markdown("---")
col_bottom_1, col_bottom_2 = st.columns([1, 1])

with col_bottom_1:
    with st.container(border=True):
        st.subheader("⏰ Peak Hours (Senin - Minggu)")
        pivot = filtered_hour.pivot_table(index='weekday_label', columns='hr', values='cnt', aggfunc='mean')
        day_order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
        pivot = pivot.reindex(day_order)
        
        fig_heat, ax_heat = plt.subplots(figsize=(10, 6))
        sns.heatmap(pivot, cmap="Blues", ax=ax_heat, cbar=False, annot=False)
        ax_heat.set_ylabel("")
        ax_heat.set_xlabel("Jam Operasional")
        st.pyplot(fig_heat)

with col_bottom_2:
    with st.container(border=True):
        st.subheader("🌡️ Korelasi Suhu vs Rental")
        fig_scatter, ax_scatter = plt.subplots(figsize=(10, 6))
        sns.regplot(data=filtered_day, x='temp', y='cnt', 
                    scatter_kws={'alpha':0.3, 'color':'#1e88e5'}, 
                    line_kws={'color':'#ff5252'}, ax=ax_scatter)
        ax_scatter.set_xlabel("Normalized Temperature")
        ax_scatter.set_ylabel("Total Rental")
        st.pyplot(fig_scatter)

# Section Clustering yang lebih bersih
st.markdown("---")
st.subheader("🔵 Segmentasi Performa Harian")
c1, c2 = st.columns([1, 2])

with c1:
    st.write("Profil Cluster:")
    profile = filtered_day.groupby('usage_cluster', observed=True)['cnt'].agg(['count', 'mean']).round(0)
    st.table(profile)

with c2:
    with st.container(border=True):
        fig_box, ax_box = plt.subplots(figsize=(10, 4))
        sns.boxplot(data=filtered_day, x='usage_cluster', y='cnt', palette="Pastel1", ax=ax_box)
        st.pyplot(fig_box)

st.caption(f"Terakhir diperbarui: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M')}")
