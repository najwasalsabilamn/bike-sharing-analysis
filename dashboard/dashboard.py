import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns

# ── Page config ────────────────────────────────────────────
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Sans:wght@300;400;500&display=swap');

/* ── Global ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

.main { background-color: #0f1117; }
section[data-testid="stSidebar"] { background-color: #0a0d14 !important; }
section[data-testid="stSidebar"] * { color: #e0e6f0 !important; }

/* ── Hero header ── */
.hero {
    background: linear-gradient(135deg, #0f1117 0%, #1a1f2e 50%, #0d1526 100%);
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 20px;
    padding: 40px 48px;
    margin-bottom: 28px;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -60px; right: -60px;
    width: 300px; height: 300px;
    background: radial-gradient(circle, rgba(66,153,225,0.12) 0%, transparent 70%);
    border-radius: 50%;
}
.hero-label {
    font-family: 'DM Sans', sans-serif;
    font-size: 11px;
    font-weight: 500;
    letter-spacing: 3px;
    text-transform: uppercase;
    color: #63b3ed;
    margin-bottom: 10px;
}
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 42px;
    font-weight: 800;
    color: #ffffff;
    line-height: 1.1;
    margin: 0 0 12px 0;
}
.hero-title span { color: #63b3ed; }
.hero-sub {
    font-size: 15px;
    color: #718096;
    font-weight: 300;
    margin: 0;
}

/* ── Section titles ── */
.section-title {
    font-family: 'Syne', sans-serif;
    font-size: 20px;
    font-weight: 700;
    color: #e2e8f0;
    margin: 32px 0 16px 0;
    padding-left: 14px;
    border-left: 3px solid #63b3ed;
}

/* ── Metric cards ── */
.metric-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin-bottom: 8px;
}
.metric-card {
    background: linear-gradient(145deg, #1a1f2e, #141820);
    border: 1px solid rgba(99,179,237,0.12);
    border-radius: 16px;
    padding: 24px 20px;
    position: relative;
    overflow: hidden;
    transition: border-color 0.2s;
}
.metric-card:hover { border-color: rgba(99,179,237,0.35); }
.metric-card::after {
    content: '';
    position: absolute;
    bottom: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, #63b3ed, transparent);
}
.metric-icon {
    font-size: 22px;
    margin-bottom: 10px;
    display: block;
}
.metric-label {
    font-size: 11px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #4a5568;
    font-weight: 500;
    margin-bottom: 6px;
}
.metric-value {
    font-family: 'Syne', sans-serif;
    font-size: 30px;
    font-weight: 700;
    color: #e2e8f0;
    line-height: 1;
    margin-bottom: 6px;
}
.metric-delta {
    font-size: 12px;
    color: #68d391;
    font-weight: 500;
}

/* ── Chart containers ── */
.chart-container {
    background: #141820;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 16px;
    padding: 24px;
    margin-bottom: 16px;
}
.chart-title {
    font-family: 'Syne', sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: #a0aec0;
    letter-spacing: 0.5px;
    margin-bottom: 16px;
    text-transform: uppercase;
}

/* ── Insight box ── */
.insight-box {
    background: linear-gradient(135deg, rgba(99,179,237,0.06), rgba(66,153,225,0.03));
    border: 1px solid rgba(99,179,237,0.15);
    border-radius: 12px;
    padding: 16px 20px;
    margin-top: 8px;
}
.insight-box p {
    color: #a0aec0;
    font-size: 13px;
    line-height: 1.7;
    margin: 0;
}
.insight-box strong { color: #63b3ed; }

/* ── Sidebar ── */
.sidebar-header {
    font-family: 'Syne', sans-serif;
    font-size: 18px;
    font-weight: 700;
    color: #63b3ed !important;
    margin-bottom: 4px;
}
.sidebar-sub {
    font-size: 11px;
    color: #4a5568 !important;
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 24px;
}

/* ── Divider ── */
.custom-divider {
    height: 1px;
    background: linear-gradient(90deg, rgba(99,179,237,0.3), transparent);
    margin: 24px 0;
}

/* ── Cluster badge ── */
.badge {
    display: inline-block;
    padding: 3px 10px;
    border-radius: 20px;
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.5px;
}
.badge-low    { background: rgba(239,154,154,0.15); color: #EF9A9A; border: 1px solid rgba(239,154,154,0.3); }
.badge-med    { background: rgba(255,224,130,0.15); color: #FFE082; border: 1px solid rgba(255,224,130,0.3); }
.badge-high   { background: rgba(165,214,167,0.15); color: #A5D6A7; border: 1px solid rgba(165,214,167,0.3); }

/* ── Hide Streamlit branding ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 24px; }
</style>
""", unsafe_allow_html=True)

# ── Matplotlib dark theme ───────────────────────────────────
plt.rcParams.update({
    'figure.facecolor':  '#141820',
    'axes.facecolor':    '#141820',
    'axes.edgecolor':    '#2d3748',
    'axes.labelcolor':   '#718096',
    'axes.titlecolor':   '#a0aec0',
    'axes.titlesize':    12,
    'axes.titleweight':  'semibold',
    'axes.labelsize':    10,
    'axes.grid':         True,
    'grid.color':        '#1e2433',
    'grid.linewidth':    0.8,
    'xtick.color':       '#4a5568',
    'ytick.color':       '#4a5568',
    'xtick.labelsize':   9,
    'ytick.labelsize':   9,
    'legend.facecolor':  '#1a1f2e',
    'legend.edgecolor':  '#2d3748',
    'legend.labelcolor': '#a0aec0',
    'legend.fontsize':   9,
    'text.color':        '#a0aec0',
    'axes.spines.top':   False,
    'axes.spines.right': False,
    'axes.spines.left':  False,
    'axes.spines.bottom':False,
})

BLUE    = '#63b3ed'
ORANGE  = '#f6ad55'
GREEN   = '#68d391'
PURPLE  = '#b794f4'
RED     = '#fc8181'
TEAL    = '#4fd1c5'

# ── Load & clean data ───────────────────────────────────────
@st.cache_data
def load_data():
    day_df  = pd.read_csv('dashboard/main_data.csv')
    hour_df = pd.read_csv('data/hour.csv')

    season_map  = {1:'Spring',2:'Summer',3:'Fall',4:'Winter'}
    weather_map = {1:'Clear',2:'Mist',3:'Light Snow/Rain',4:'Heavy Rain'}
    weekday_map = {0:'Sun',1:'Mon',2:'Tue',3:'Wed',4:'Thu',5:'Fri',6:'Sat'}
    yr_map      = {0:'2011',1:'2012'}

    for df in [day_df, hour_df]:
        df['dteday']        = pd.to_datetime(df['dteday'])
        df['year']          = df['dteday'].dt.year
        df['month']         = df['dteday'].dt.month
        df['season_label']  = df['season'].map(season_map)
        df['weather_label'] = df['weathersit'].map(weather_map)
        df['weekday_label'] = df['weekday'].map(weekday_map)
        df['yr_label']      = df['yr'].map(yr_map)

    p33 = day_df['cnt'].quantile(0.33)
    p67 = day_df['cnt'].quantile(0.67)
    day_df['usage_cluster'] = pd.cut(
        day_df['cnt'],
        bins=[0, p33, p67, day_df['cnt'].max()+1],
        labels=['Low Usage','Medium Usage','High Usage']
    )
    return day_df, hour_df

day_df, hour_df = load_data()

# ── Sidebar ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="sidebar-header">🚲 BikeShare</p>', unsafe_allow_html=True)
    st.markdown('<p class="sidebar-sub">Analytics Dashboard</p>', unsafe_allow_html=True)

    st.markdown("**Filter Data**")
    selected_yr = st.selectbox("Tahun", ['Semua','2011','2012'])
    selected_season = st.selectbox("Musim", ['Semua','Spring','Summer','Fall','Winter'])
    selected_weather = st.selectbox("Cuaca", ['Semua','Clear','Mist','Light Snow/Rain'])

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.markdown("**Dataset Info**")
    st.caption("📍 Washington D.C., USA")
    st.caption("📅 Januari 2011 – Desember 2012")
    st.caption("🗃️ Capital Bikeshare")

    st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)
    st.caption("Proyek Analisis Data · Dicoding")
    st.caption("Najwa Salsabila")

# ── Filter ──────────────────────────────────────────────────
fd = day_df.copy()
fh = hour_df.copy()
if selected_yr      != 'Semua': fd = fd[fd['yr_label']      == selected_yr];    fh = fh[fh['yr_label']      == selected_yr]
if selected_season  != 'Semua': fd = fd[fd['season_label']  == selected_season]
if selected_weather != 'Semua': fd = fd[fd['weather_label'] == selected_weather]

# ── Hero ─────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <p class="hero-label">Washington D.C. · 2011–2012</p>
    <h1 class="hero-title">Bike Sharing <span>Analytics</span></h1>
    <p class="hero-sub">Analisis pola penggunaan layanan Capital Bikeshare — cuaca, musim, jam, dan segmentasi pengguna.</p>
</div>
""", unsafe_allow_html=True)

# ── KPI Metrics ──────────────────────────────────────────────
total   = fd['cnt'].sum()
avg_d   = fd['cnt'].mean()
casual  = fd['casual'].sum()
reg     = fd['registered'].sum()
peak_hr = hour_df[hour_df['workingday']==1].groupby('hr')['cnt'].mean().idxmax()

st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card">
    <span class="metric-icon">🚴</span>
    <div class="metric-label">Total Peminjaman</div>
    <div class="metric-value">{total/1e6:.2f}M</div>
    <div class="metric-delta">↑ semua waktu</div>
  </div>
  <div class="metric-card">
    <span class="metric-icon">📅</span>
    <div class="metric-label">Rata-rata Harian</div>
    <div class="metric-value">{avg_d:,.0f}</div>
    <div class="metric-delta">per hari</div>
  </div>
  <div class="metric-card">
    <span class="metric-icon">⏰</span>
    <div class="metric-label">Jam Tersibuk</div>
    <div class="metric-value">{peak_hr:02d}:00</div>
    <div class="metric-delta">hari kerja</div>
  </div>
  <div class="metric-card">
    <span class="metric-icon">👥</span>
    <div class="metric-label">Registered vs Casual</div>
    <div class="metric-value">{reg/total*100:.0f}%</div>
    <div class="metric-delta">{casual/total*100:.0f}% casual</div>
  </div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ROW 1 — Tren & Cuaca
# ════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">📈 Tren & Pengaruh Cuaca</p>', unsafe_allow_html=True)
col1, col2 = st.columns([3, 2])

with col1:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<p class="chart-title">Total Peminjaman Bulanan</p>', unsafe_allow_html=True)

    monthly = day_df.groupby(['year','month'])['cnt'].sum().reset_index()
    monthly['label'] = monthly['year'].astype(str) + '-' + monthly['month'].astype(str).str.zfill(2)

    fig, ax = plt.subplots(figsize=(9, 3.5))
    colors_yr = {2011: BLUE, 2012: ORANGE}
    for yr, grp in monthly.groupby('year'):
        ax.plot(range(len(grp)), grp['cnt']/1000,
                color=colors_yr[yr], linewidth=2.5,
                label=str(yr), zorder=3)
        ax.fill_between(range(len(grp)), grp['cnt']/1000,
                        alpha=0.08, color=colors_yr[yr])
        ax.scatter(range(len(grp)), grp['cnt']/1000,
                   color=colors_yr[yr], s=35, zorder=4)

    ax.set_xticks(range(12))
    ax.set_xticklabels(['Jan','Feb','Mar','Apr','Mei','Jun',
                        'Jul','Agt','Sep','Okt','Nov','Des'], fontsize=8)
    ax.set_ylabel('Peminjaman (ribu)')
    ax.legend(loc='upper left')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f'{x:.0f}K'))
    fig.tight_layout(pad=1.5)
    st.pyplot(fig, use_container_width=True)
    plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<p class="chart-title">Rata-rata per Kondisi Cuaca</p>', unsafe_allow_html=True)

    w_order = ['Clear','Mist','Light Snow/Rain']
    w_avg   = (day_df.groupby('weather_label')['cnt'].mean()
               .reindex(w_order).dropna().reset_index())
    w_colors = [BLUE, TEAL, PURPLE]

    fig, ax = plt.subplots(figsize=(5, 3.5))
    bars = ax.barh(w_avg['weather_label'], w_avg['cnt'],
                   color=w_colors, height=0.5,
                   edgecolor='none')
    for bar, val in zip(bars, w_avg['cnt']):
        ax.text(bar.get_width() + 50, bar.get_y() + bar.get_height()/2,
                f'{val:,.0f}', va='center', fontsize=9, color='#a0aec0')
    ax.set_xlabel('Rata-rata Peminjaman')
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f'{x/1000:.0f}K'))
    fig.tight_layout(pad=1.5)
    st.pyplot(fig, use_container_width=True)
    plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ROW 2 — Musim & Pie
# ════════════════════════════════════════════════════════════
col3, col4 = st.columns([2, 1])

with col3:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<p class="chart-title">Rata-rata Peminjaman per Musim</p>', unsafe_allow_html=True)

    s_order  = ['Spring','Summer','Fall','Winter']
    s_avg    = (day_df.groupby('season_label')['cnt'].mean()
                .reindex(s_order).reset_index())
    s_colors = ['#68d391','#f6ad55','#fc8181','#76e4f7']

    fig, ax = plt.subplots(figsize=(7, 3.2))
    bars = ax.bar(s_avg['season_label'], s_avg['cnt'],
                  color=s_colors, width=0.5, edgecolor='none',
                  zorder=3)
    best = s_avg['cnt'].argmax()
    bars[best].set_edgecolor(BLUE)
    bars[best].set_linewidth(2)

    for bar, val in zip(bars, s_avg['cnt']):
        ax.text(bar.get_x()+bar.get_width()/2, bar.get_height()+50,
                f'{val:,.0f}', ha='center', fontsize=9, color='#a0aec0')

    ax.set_ylabel('Rata-rata Peminjaman')
    ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f'{x/1000:.1f}K'))
    fig.tight_layout(pad=1.5)
    st.pyplot(fig, use_container_width=True)
    plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

with col4:
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.markdown('<p class="chart-title">Komposisi Pengguna</p>', unsafe_allow_html=True)

    total_c = fd['casual'].sum()
    total_r = fd['registered'].sum()

    fig, ax = plt.subplots(figsize=(4, 3.2))
    wedges, texts, autotexts = ax.pie(
        [total_r, total_c],
        labels=['Registered','Casual'],
        autopct='%1.1f%%',
        colors=[BLUE, ORANGE],
        startangle=90,
        wedgeprops=dict(width=0.6, edgecolor='#141820', linewidth=3),
        pctdistance=0.75
    )
    for t in texts:      t.set_color('#718096'); t.set_fontsize(9)
    for t in autotexts:  t.set_color('#e2e8f0'); t.set_fontsize(9); t.set_fontweight('bold')
    ax.set_aspect('equal')
    fig.tight_layout(pad=0.5)
    st.pyplot(fig, use_container_width=True)
    plt.close()
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ROW 3 — Pola Jam
# ════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">⏰ Pola Peminjaman per Jam</p>', unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📊 Hari Kerja vs Libur", "🗓️ Heatmap Mingguan"])

with tab1:
    wd  = hour_df[hour_df['workingday']==1].groupby('hr')[['casual','registered','cnt']].mean()
    wkd = hour_df[hour_df['workingday']==0].groupby('hr')[['casual','registered','cnt']].mean()

    fig, axes = plt.subplots(1, 2, figsize=(14, 4), sharey=True)

    for ax, data, title, ann in [
        (axes[0], wd,  'Hari Kerja',  [(8,'08:00\nBerangkat'),(17,'17:00\nPulang')]),
        (axes[1], wkd, 'Hari Libur',  [(data.idxmax()['cnt'],'Puncak\nSiang')
                                        for data in [wkd]][0:1]),
    ]:
        hrs = range(24)
        ax.fill_between(hrs, data['registered'], alpha=0.12, color=BLUE)
        ax.fill_between(hrs, data['casual'],     alpha=0.12, color=ORANGE)
        ax.plot(hrs, data['cnt'],        color='#e2e8f0', lw=2.5, label='Total', zorder=4)
        ax.plot(hrs, data['registered'], color=BLUE,     lw=1.8, linestyle='--', label='Registered', zorder=3)
        ax.plot(hrs, data['casual'],     color=ORANGE,   lw=1.8, linestyle='--', label='Casual', zorder=3)
        ax.set_title(title, fontsize=12, color='#e2e8f0')
        ax.set_xlabel('Jam'); ax.set_ylabel('Rata-rata Peminjaman')
        ax.set_xticks(range(0,24,3))
        ax.legend(loc='upper left', fontsize=8)

        for hr, lbl in ann:
            yval = data['cnt'].iloc[hr]
            ax.scatter([hr], [yval], color='#fc8181', s=80, zorder=5)
            ax.annotate(lbl, xy=(hr, yval), xytext=(hr+1.5, yval+80),
                        fontsize=7.5, color='#fc8181',
                        arrowprops=dict(arrowstyle='-', color='#4a5568', lw=0.8))

    fig.tight_layout(pad=2)
    st.pyplot(fig, use_container_width=True)
    plt.close()

    st.markdown("""
    <div class="insight-box">
    <p>
    <strong>Hari Kerja</strong> menunjukkan pola bimodal dengan puncak pukul <strong>08:00</strong> (berangkat kerja)
    dan <strong>17:00–18:00</strong> (pulang kerja) — didominasi pengguna <strong>registered</strong>.
    <strong>Hari libur</strong> menunjukkan pola unimodal dengan puncak siang hari — proporsi pengguna
    <strong>casual</strong> jauh lebih tinggi.
    </p>
    </div>
    """, unsafe_allow_html=True)

with tab2:
    day_order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    pivot = (hour_df.pivot_table(index='weekday_label', columns='hr', values='cnt', aggfunc='mean')
             .reindex(day_order))

    fig, ax = plt.subplots(figsize=(16, 4))
    cmap = sns.color_palette("mako", as_cmap=True)
    sns.heatmap(pivot, cmap='YlOrRd', linewidths=0.3, linecolor='#0f1117',
                cbar_kws={'label':'Rata-rata Peminjaman', 'shrink':0.8},
                ax=ax, annot=False)
    ax.set_title('Rata-rata Peminjaman per Jam dan Hari', color='#e2e8f0', fontsize=12)
    ax.set_xlabel('Jam ke-', color='#718096')
    ax.set_ylabel('')
    ax.tick_params(axis='x', rotation=0)
    ax.tick_params(axis='y', rotation=0, labelcolor='#a0aec0')
    fig.tight_layout(pad=1.5)
    st.pyplot(fig, use_container_width=True)
    plt.close()

st.markdown('<div class="custom-divider"></div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════
# ROW 4 — Clustering
# ════════════════════════════════════════════════════════════
st.markdown('<p class="section-title">🔵 Segmentasi Tingkat Penggunaan</p>', unsafe_allow_html=True)

CLUSTER_COLORS = {'Low Usage':'#EF9A9A','Medium Usage':'#FFE082','High Usage':'#A5D6A7'}
cluster_list   = ['Low Usage','Medium Usage','High Usage']

profile = day_df.groupby('usage_cluster', observed=True).agg(
    Jumlah_Hari     = ('cnt','count'),
    Rata_cnt        = ('cnt','mean'),
    Rata_casual     = ('casual','mean'),
    Rata_registered = ('registered','mean'),
    Rata_temp       = ('temp','mean'),
    Pct_workingday  = ('workingday','mean'),
).round(2).reindex(cluster_list)

col5, col6, col7 = st.columns(3)

for col, cl, icon in zip([col5,col6,col7], cluster_list, ['🔴','🟡','🟢']):
    with col:
        row = profile.loc[cl]
        badge_class = {'Low Usage':'badge-low','Medium Usage':'badge-med','High Usage':'badge-high'}[cl]
        st.markdown(f"""
        <div class="chart-container" style="text-align:center;">
            <div style="margin-bottom:12px;">
                <span class="badge {badge_class}">{icon} {cl}</span>
            </div>
            <div style="font-family:'Syne',sans-serif; font-size:36px; font-weight:800;
                        color:{CLUSTER_COLORS[cl]}; line-height:1;">
                {row['Rata_cnt']:,.0f}
            </div>
            <div style="font-size:11px; color:#4a5568; letter-spacing:1px;
                        text-transform:uppercase; margin:6px 0 16px 0;">
                rata-rata cnt/hari
            </div>
            <div style="display:grid; grid-template-columns:1fr 1fr; gap:8px; text-align:left;">
                <div style="background:#1a1f2e; border-radius:8px; padding:10px 12px;">
                    <div style="font-size:10px; color:#4a5568; text-transform:uppercase; letter-spacing:1px;">Casual</div>
                    <div style="font-family:'Syne',sans-serif; font-size:18px; color:#f6ad55; font-weight:700;">{row['Rata_casual']:,.0f}</div>
                </div>
                <div style="background:#1a1f2e; border-radius:8px; padding:10px 12px;">
                    <div style="font-size:10px; color:#4a5568; text-transform:uppercase; letter-spacing:1px;">Registered</div>
                    <div style="font-family:'Syne',sans-serif; font-size:18px; color:#63b3ed; font-weight:700;">{row['Rata_registered']:,.0f}</div>
                </div>
                <div style="background:#1a1f2e; border-radius:8px; padding:10px 12px;">
                    <div style="font-size:10px; color:#4a5568; text-transform:uppercase; letter-spacing:1px;">Suhu</div>
                    <div style="font-family:'Syne',sans-serif; font-size:18px; color:#68d391; font-weight:700;">{row['Rata_temp']:.3f}</div>
                </div>
                <div style="background:#1a1f2e; border-radius:8px; padding:10px 12px;">
                    <div style="font-size:10px; color:#4a5568; text-transform:uppercase; letter-spacing:1px;">Hari Kerja</div>
                    <div style="font-family:'Syne',sans-serif; font-size:18px; color:#b794f4; font-weight:700;">{row['Pct_workingday']*100:.0f}%</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# Cluster bar chart
st.markdown('<div class="chart-container">', unsafe_allow_html=True)
st.markdown('<p class="chart-title">Distribusi cnt per Cluster</p>', unsafe_allow_html=True)

fig, axes = plt.subplots(1, 3, figsize=(14, 3.5))

# 1 – Histogram per cluster
for cl in cluster_list:
    axes[0].hist(day_df[day_df['usage_cluster']==cl]['cnt'], bins=18,
                 alpha=0.75, color=CLUSTER_COLORS[cl], label=cl, edgecolor='none')
axes[0].set_title('Distribusi cnt per Cluster')
axes[0].set_xlabel('Jumlah Peminjaman'); axes[0].set_ylabel('Frekuensi')
axes[0].legend(fontsize=8)
axes[0].xaxis.set_major_formatter(plt.FuncFormatter(lambda x,_: f'{x/1000:.0f}K'))

# 2 – Komposisi musim per cluster
season_cl = (day_df.groupby(['usage_cluster','season_label'], observed=True)
             .size().reset_index(name='count'))
sp = season_cl.pivot_table(index='usage_cluster', columns='season_label',
                            values='count', observed=True).fillna(0)
sp_pct = (sp.div(sp.sum(axis=1), axis=0)*100).reindex(cluster_list)
s_colors_map = {'Fall':'#fc8181','Spring':'#68d391','Summer':'#f6ad55','Winter':'#76e4f7'}
bottom = np.zeros(3)
for season in sp_pct.columns:
    vals = sp_pct[season].values
    axes[1].bar(cluster_list, vals, bottom=bottom,
                color=s_colors_map.get(season,'#a0aec0'),
                label=season, edgecolor='none', width=0.5)
    bottom += vals
axes[1].set_title('Komposisi Musim per Cluster (%)')
axes[1].set_ylabel('%'); axes[1].legend(fontsize=8, loc='upper right')
axes[1].tick_params(axis='x', labelsize=8)

# 3 – Suhu per cluster
temp_m = profile['Rata_temp']
b3 = axes[2].bar(cluster_list, temp_m,
                 color=[CLUSTER_COLORS[c] for c in cluster_list],
                 width=0.5, edgecolor='none')
axes[2].set_title('Rata-rata Suhu per Cluster')
axes[2].set_ylabel('Suhu (normalized)')
axes[2].set_ylim(0, temp_m.max()*1.3)
for bar, val in zip(b3, temp_m):
    axes[2].text(bar.get_x()+bar.get_width()/2, bar.get_height()+0.005,
                 f'{val:.3f}', ha='center', fontsize=9, color='#a0aec0')

fig.tight_layout(pad=2)
st.pyplot(fig, use_container_width=True)
plt.close()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown("""
<div class="insight-box">
<p>
Cluster <strong style="color:#EF9A9A;">Low Usage</strong> didominasi musim Spring & Winter dengan suhu rendah.
Cluster <strong style="color:#A5D6A7;">High Usage</strong> erat kaitannya dengan musim Fall/Summer dan suhu hangat.
Proporsi hari kerja relatif merata (~67–73%) di ketiga cluster — membuktikan bahwa
<strong>cuaca dan musim jauh lebih berpengaruh</strong> dibanding hari kerja/libur dalam menentukan
tingkat penggunaan.
</p>
</div>
""", unsafe_allow_html=True)

# ── Footer ───────────────────────────────────────────────────
st.markdown("""
<div style="text-align:center; padding:40px 0 20px 0;">
    <div style="font-family:'Syne',sans-serif; font-size:13px; color:#2d3748; letter-spacing:2px; text-transform:uppercase;">
        Bike Sharing Analytics · Dicoding · Najwa Salsabila · 2024
    </div>
</div>
""", unsafe_allow_html=True)
