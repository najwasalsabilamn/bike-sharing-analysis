import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns

# ============================================================
# KONFIGURASI HALAMAN
# ============================================================
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Styling global matplotlib
plt.rcParams.update({
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'axes.titlesize':    13,
    'axes.titleweight':  'bold',
    'axes.labelsize':    10,
    'xtick.labelsize':   9,
    'ytick.labelsize':   9,
})

COLOR_PRIMARY = '#2196F3'
CLUSTER_COLORS = {
    'Low Usage':    '#EF9A9A',
    'Medium Usage': '#FFE082',
    'High Usage':   '#A5D6A7'
}

# ============================================================
# LOAD DATA
# ============================================================
@st.cache_data
def load_data():
    day_df  = pd.read_csv('dashboard/main_data.csv')
    hour_df = pd.read_csv('data/hour.csv')

    # Mapping
    season_map  = {1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'}
    weather_map = {1:'Clear',  2:'Mist',   3:'Light Snow/Rain', 4:'Heavy Rain'}
    weekday_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
    yr_map      = {0:'2011', 1:'2012'}

    for df in [day_df, hour_df]:
        df['dteday']       = pd.to_datetime(df['dteday'])
        df['year']         = df['dteday'].dt.year
        df['month']        = df['dteday'].dt.month
        df['season_label'] = df['season'].map(season_map).astype('category')
        df['weather_label']= df['weathersit'].map(weather_map).astype('category')
        df['weekday_label']= df['weekday'].map(weekday_map).astype('category')
        df['yr_label']     = df['yr'].map(yr_map).astype('category')

    # Clustering
    p33 = day_df['cnt'].quantile(0.33)
    p67 = day_df['cnt'].quantile(0.67)
    day_df['usage_cluster'] = pd.cut(
        day_df['cnt'],
        bins=[0, p33, p67, day_df['cnt'].max() + 1],
        labels=['Low Usage', 'Medium Usage', 'High Usage']
    )
    return day_df, hour_df

day_df, hour_df = load_data()

# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/e/e4/Bike_sharing_station_Tempelhof_Berlin.JPG/320px-Bike_sharing_station_Tempelhof_Berlin.JPG",
                 use_column_width=True)
st.sidebar.title("🚲 Bike Sharing")
st.sidebar.markdown("**Dashboard Analisis Data**")
st.sidebar.markdown("---")

# Filter Tahun
yr_options = ['Semua', '2011', '2012']
selected_yr = st.sidebar.selectbox("Pilih Tahun:", yr_options)

# Filter Musim
season_options = ['Semua'] + list(day_df['season_label'].cat.categories)
selected_season = st.sidebar.selectbox("Pilih Musim:", season_options)

st.sidebar.markdown("---")
st.sidebar.markdown("**Tentang Dataset**")
st.sidebar.markdown(
    "Dataset Capital Bikeshare Washington D.C., USA (2011–2012). "
    "Sumber: [UCI ML Repository](https://archive.ics.uci.edu/ml/datasets/Bike+Sharing+Dataset)"
)

# ============================================================
# FILTER DATA
# ============================================================
filtered_day  = day_df.copy()
filtered_hour = hour_df.copy()

if selected_yr != 'Semua':
    filtered_day  = filtered_day[filtered_day['yr_label']  == selected_yr]
    filtered_hour = filtered_hour[filtered_hour['yr_label'] == selected_yr]

if selected_season != 'Semua':
    filtered_day = filtered_day[filtered_day['season_label'] == selected_season]

# ============================================================
# HEADER
# ============================================================
st.title("🚲 Bike Sharing Analysis Dashboard")
st.markdown(
    "Dashboard interaktif untuk menganalisis pola penggunaan layanan bike sharing "
    "di Washington D.C. berdasarkan data tahun **2011–2012**."
)
st.markdown("---")

# ============================================================
# KPI METRICS
# ============================================================
col1, col2, col3, col4 = st.columns(4)

total_rides    = filtered_day['cnt'].sum()
avg_daily      = filtered_day['cnt'].mean()
total_casual   = filtered_day['casual'].sum()
total_register = filtered_day['registered'].sum()

col1.metric("🚴 Total Peminjaman",   f"{total_rides:,.0f}")
col2.metric("📅 Rata-rata Harian",   f"{avg_daily:,.0f}")
col3.metric("👤 Casual",             f"{total_casual:,.0f}",
            delta=f"{total_casual/total_rides*100:.1f}%")
col4.metric("✅ Registered",          f"{total_register:,.0f}",
            delta=f"{total_register/total_rides*100:.1f}%")

st.markdown("---")

# ============================================================
# SECTION 1: TREN BULANAN
# ============================================================
st.subheader("📈 Tren Peminjaman Sepeda Harian")

monthly = filtered_day.groupby(['year','month'], as_index=False)['cnt'].sum()
monthly['period'] = monthly['year'].astype(str) + '-' + monthly['month'].astype(str).str.zfill(2)

fig1, ax1 = plt.subplots(figsize=(12, 4))
for yr, grp in monthly.groupby('year'):
    color = '#1565C0' if yr == 2011 else '#E65100'
    ax1.plot(grp['period'], grp['cnt']/1000, marker='o', markersize=5,
             linewidth=2, label=str(yr), color=color)
ax1.set_title('Total Peminjaman Bulanan (ribuan)')
ax1.set_xlabel('Bulan')
ax1.set_ylabel('Peminjaman (ribu)')
ax1.tick_params(axis='x', rotation=45, labelsize=8)
ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}K'))
ax1.legend()
ax1.grid(axis='y', linestyle='--', alpha=0.4)
st.pyplot(fig1)
plt.close()

# ============================================================
# SECTION 2: CUACA & MUSIM
# ============================================================
st.subheader("🌤️ Pengaruh Cuaca & Musim terhadap Peminjaman")

col_a, col_b = st.columns(2)

with col_a:
    weather_avg = (filtered_day.groupby('weather_label', observed=True)['cnt']
                   .mean()
                   .reindex(['Clear','Mist','Light Snow/Rain'])
                   .reset_index()
                   .dropna())
    fig2, ax2 = plt.subplots(figsize=(6, 4))
    colors_w = ['#2196F3','#90CAF9','#E3F2FD'][:len(weather_avg)]
    bars = ax2.bar(weather_avg['weather_label'], weather_avg['cnt'], color=colors_w, edgecolor='white')
    ax2.set_title('Rata-rata Peminjaman per Kondisi Cuaca')
    ax2.set_xlabel('Kondisi Cuaca')
    ax2.set_ylabel('Rata-rata cnt')
    for bar, val in zip(bars, weather_avg['cnt']):
        ax2.text(bar.get_x()+bar.get_width()/2, bar.get_height()+50,
                 f'{val:,.0f}', ha='center', fontsize=9, fontweight='bold')
    st.pyplot(fig2)
    plt.close()

with col_b:
    season_order = ['Spring','Summer','Fall','Winter']
    season_avg = (filtered_day.groupby('season_label', observed=True)['cnt']
                  .mean()
                  .reindex(season_order)
                  .reset_index()
                  .dropna())
    fig3, ax3 = plt.subplots(figsize=(6, 4))
    colors_s = ['#A5D6A7','#FFF59D','#FFCC80','#B3E5FC'][:len(season_avg)]
    bars2 = ax3.bar(season_avg['season_label'], season_avg['cnt'], color=colors_s, edgecolor='white')
    ax3.set_title('Rata-rata Peminjaman per Musim')
    ax3.set_xlabel('Musim')
    ax3.set_ylabel('Rata-rata cnt')
    for bar, val in zip(bars2, season_avg['cnt']):
        ax3.text(bar.get_x()+bar.get_width()/2, bar.get_height()+50,
                 f'{val:,.0f}', ha='center', fontsize=9, fontweight='bold')
    st.pyplot(fig3)
    plt.close()

# ============================================================
# SECTION 3: POLA JAM
# ============================================================
st.subheader("⏰ Pola Peminjaman per Jam")

tab1, tab2 = st.tabs(["Hari Kerja vs Libur", "Heatmap Hari × Jam"])

with tab1:
    hourly_wd  = filtered_hour[filtered_hour['workingday']==1].groupby('hr')[['casual','registered','cnt']].mean()
    hourly_wkd = filtered_hour[filtered_hour['workingday']==0].groupby('hr')[['casual','registered','cnt']].mean()

    fig4, axes4 = plt.subplots(1, 2, figsize=(14, 4), sharey=True)
    hours = range(24)

    for ax, data, title in [
        (axes4[0], hourly_wd,  'Hari Kerja'),
        (axes4[1], hourly_wkd, 'Hari Libur / Weekend')
    ]:
        ax.fill_between(hours, data['registered'], alpha=0.3, color='#1565C0')
        ax.fill_between(hours, data['casual'],     alpha=0.3, color='#FF6F00')
        ax.plot(hours, data['cnt'],        color='black',   linewidth=2,   label='Total')
        ax.plot(hours, data['registered'], color='#1565C0', linewidth=1.5, linestyle='--', label='Registered')
        ax.plot(hours, data['casual'],     color='#FF6F00', linewidth=1.5, linestyle='--', label='Casual')
        ax.set_title(title)
        ax.set_xlabel('Jam')
        ax.set_ylabel('Rata-rata Peminjaman')
        ax.set_xticks(range(0,24,2))
        ax.legend(fontsize=8)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
    st.pyplot(fig4)
    plt.close()

with tab2:
    pivot = filtered_hour.pivot_table(index='weekday_label', columns='hr', values='cnt', aggfunc='mean')
    day_order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    pivot = pivot.reindex([d for d in day_order if d in pivot.index])
    fig5, ax5 = plt.subplots(figsize=(16, 4))
    sns.heatmap(pivot, cmap='YlOrRd', linewidths=0.2, linecolor='white',
                cbar_kws={'label':'Rata-rata Peminjaman'}, ax=ax5)
    ax5.set_title('Heatmap Rata-rata Peminjaman (Hari × Jam)')
    ax5.set_xlabel('Jam ke-')
    ax5.set_ylabel('Hari')
    ax5.tick_params(axis='x', rotation=0)
    st.pyplot(fig5)
    plt.close()

# ============================================================
# SECTION 4: CLUSTERING
# ============================================================
st.subheader("🔵 Segmentasi Hari: Clustering Manual")

st.markdown(
    "Hari-hari dikelompokkan ke dalam **3 cluster** berdasarkan total peminjaman harian "
    "menggunakan teknik binning berbasis persentil (Low / Medium / High Usage)."
)

col_c, col_d = st.columns([1, 2])

with col_c:
    cluster_count = filtered_day['usage_cluster'].value_counts().reindex(['Low Usage','Medium Usage','High Usage'])
    st.dataframe(
        cluster_count.reset_index().rename(columns={'usage_cluster':'Cluster','count':'Jumlah Hari'}),
        hide_index=True, use_container_width=True
    )
    profile = filtered_day.groupby('usage_cluster', observed=True).agg(
        Rata_cnt        = ('cnt',       'mean'),
        Rata_casual     = ('casual',    'mean'),
        Rata_registered = ('registered','mean'),
        Rata_suhu       = ('temp',      'mean'),
    ).round(1).reindex(['Low Usage','Medium Usage','High Usage'])
    st.dataframe(profile, use_container_width=True)

with col_d:
    fig6, axes6 = plt.subplots(1, 2, figsize=(10, 4))

    # Bar rata-rata cnt
    means_c = profile['Rata_cnt']
    bars_c  = axes6[0].bar(
        means_c.index, means_c.values,
        color=[CLUSTER_COLORS.get(c,'gray') for c in means_c.index],
        edgecolor='white'
    )
    axes6[0].set_title('Rata-rata Peminjaman per Cluster')
    axes6[0].set_ylabel('Rata-rata cnt')
    for bar, val in zip(bars_c, means_c.values):
        axes6[0].text(bar.get_x()+bar.get_width()/2, bar.get_height()+40,
                      f'{val:,.0f}', ha='center', fontsize=9, fontweight='bold')
    axes6[0].tick_params(axis='x', rotation=15)

    # Stacked bar: casual vs registered
    x6 = np.arange(len(profile))
    axes6[1].bar(x6, profile['Rata_casual'],     0.5, label='Casual',     color='#FF6F00', alpha=0.85)
    axes6[1].bar(x6, profile['Rata_registered'], 0.5, bottom=profile['Rata_casual'],
                 label='Registered', color='#1565C0', alpha=0.85)
    axes6[1].set_title('Casual + Registered per Cluster')
    axes6[1].set_xticks(x6)
    axes6[1].set_xticklabels(profile.index, fontsize=9, rotation=15)
    axes6[1].set_ylabel('Rata-rata Peminjaman')
    axes6[1].legend()

    plt.tight_layout()
    st.pyplot(fig6)
    plt.close()

# ============================================================
# FOOTER
# ============================================================
st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:gray; font-size:12px;'>"
    "Proyek Analisis Data · Dicoding · Najwa Salsabila · 2024"
    "</div>",
    unsafe_allow_html=True
)
