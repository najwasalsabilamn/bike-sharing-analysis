import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ═══════════════════════════════════════════════════════════
# PAGE CONFIG
# ═══════════════════════════════════════════════════════════
st.set_page_config(
    page_title="BikeShare Analytics",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ═══════════════════════════════════════════════════════════
# DESIGN SYSTEM
# ═══════════════════════════════════════════════════════════
BG_BASE    = "#080b12"
BG_CARD    = "#0d1117"
BG_CARD2   = "#111827"
BORDER     = "#1f2937"
BORDER_LIT = "#374151"

CYAN       = "#22d3ee"
CYAN_DIM   = "#0e7490"
BLUE       = "#3b82f6"
VIOLET     = "#8b5cf6"
EMERALD    = "#10b981"
AMBER      = "#f59e0b"
ROSE       = "#f43f5e"
INDIGO     = "#6366f1"

TEXT_HI    = "#f9fafb"
TEXT_MED   = "#9ca3af"
TEXT_LO    = "#4b5563"

# Plotly base layout
PLOTLY_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="'DM Mono', monospace", color=TEXT_MED, size=11),
    margin=dict(l=10, r=10, t=35, b=10),
    legend=dict(
        bgcolor="rgba(13,17,23,0.8)",
        bordercolor=BORDER,
        borderwidth=1,
        font=dict(color=TEXT_MED, size=10)
    ),
    xaxis=dict(
        gridcolor=BORDER,
        zerolinecolor=BORDER,
        tickfont=dict(color=TEXT_LO),
        linecolor=BORDER,
    ),
    yaxis=dict(
        gridcolor=BORDER,
        zerolinecolor=BORDER,
        tickfont=dict(color=TEXT_LO),
        linecolor=BORDER,
    ),
    hoverlabel=dict(
        bgcolor=BG_CARD2,
        bordercolor=CYAN,
        font=dict(color=TEXT_HI, size=12),
    )
)

# ═══════════════════════════════════════════════════════════
# CSS
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800;900&family=DM+Mono:wght@300;400;500&display=swap');

/* ── Reset & base ── */
*, *::before, *::after {{ box-sizing: border-box; }}
html, body, [class*="css"] {{
    font-family: 'Outfit', sans-serif;
    background-color: {BG_BASE};
    color: {TEXT_MED};
}}
.main {{ background-color: {BG_BASE} !important; }}
.block-container {{ padding: 20px 32px 40px 32px !important; max-width: 1400px; }}

/* ── Scrollbar ── */
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: {BG_BASE}; }}
::-webkit-scrollbar-thumb {{ background: {BORDER_LIT}; border-radius: 4px; }}

/* ── Sidebar ── */
section[data-testid="stSidebar"] {{
    background: {BG_CARD} !important;
    border-right: 1px solid {BORDER} !important;
}}
section[data-testid="stSidebar"] * {{ color: {TEXT_MED} !important; }}
section[data-testid="stSidebar"] .stSelectbox label {{ color: {TEXT_LO} !important; font-size: 11px !important; letter-spacing: 1px; text-transform: uppercase; }}

/* ── Streamlit widgets dark ── */
div[data-baseweb="select"] > div {{
    background-color: {BG_CARD2} !important;
    border-color: {BORDER} !important;
    color: {TEXT_HI} !important;
}}
div[data-baseweb="select"] span {{ color: {TEXT_HI} !important; }}
.stTabs [data-baseweb="tab-list"] {{
    background-color: {BG_CARD} !important;
    border-bottom: 1px solid {BORDER} !important;
    gap: 0;
    padding: 0;
}}
.stTabs [data-baseweb="tab"] {{
    background-color: transparent !important;
    color: {TEXT_LO} !important;
    padding: 10px 24px !important;
    font-size: 12px !important;
    font-weight: 500 !important;
    letter-spacing: 0.5px !important;
    border-bottom: 2px solid transparent !important;
    transition: all 0.2s;
}}
.stTabs [aria-selected="true"] {{
    color: {CYAN} !important;
    border-bottom-color: {CYAN} !important;
    background-color: rgba(34,211,238,0.04) !important;
}}
.stTabs [data-baseweb="tab-panel"] {{ padding: 0 !important; }}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header {{ visibility: hidden; }}
.stDeployButton {{ display: none; }}

/* ── Hero ── */
@keyframes glow-pulse {{
    0%, 100% {{ opacity: 0.4; transform: scale(1); }}
    50%       {{ opacity: 0.7; transform: scale(1.05); }}
}}
@keyframes fadeInUp {{
    from {{ opacity: 0; transform: translateY(20px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
@keyframes scanline {{
    0%   {{ transform: translateY(-100%); }}
    100% {{ transform: translateY(100vh); }}
}}

.hero-wrap {{
    position: relative;
    background: linear-gradient(135deg, #080b12 0%, #0d1520 50%, #080b12 100%);
    border: 1px solid {BORDER};
    border-radius: 20px;
    padding: 44px 48px;
    margin-bottom: 24px;
    overflow: hidden;
    animation: fadeInUp 0.6s ease both;
}}
.hero-wrap::before {{
    content: '';
    position: absolute;
    inset: 0;
    background:
        radial-gradient(ellipse 500px 300px at 80% 50%, rgba(34,211,238,0.07) 0%, transparent 70%),
        radial-gradient(ellipse 300px 200px at 20% 80%, rgba(99,102,241,0.06) 0%, transparent 70%);
    pointer-events: none;
}}
.hero-wrap::after {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent, {CYAN}, transparent);
    opacity: 0.6;
}}
.hero-eyebrow {{
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: {CYAN};
    letter-spacing: 3px;
    text-transform: uppercase;
    margin-bottom: 14px;
}}
.hero-title {{
    font-size: 52px;
    font-weight: 900;
    line-height: 1;
    color: {TEXT_HI};
    margin: 0 0 10px 0;
    letter-spacing: -1px;
}}
.hero-title em {{
    font-style: normal;
    background: linear-gradient(90deg, {CYAN}, {BLUE});
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}}
.hero-desc {{
    font-size: 14px;
    color: {TEXT_LO};
    font-weight: 300;
    max-width: 560px;
    line-height: 1.6;
}}
.hero-badge {{
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(34,211,238,0.08);
    border: 1px solid rgba(34,211,238,0.2);
    border-radius: 20px;
    padding: 5px 14px;
    font-size: 11px;
    color: {CYAN};
    font-family: 'DM Mono', monospace;
    letter-spacing: 1px;
    margin-top: 20px;
}}
.hero-stat-row {{
    position: absolute;
    right: 48px; top: 50%;
    transform: translateY(-50%);
    display: flex;
    gap: 32px;
}}
.hero-stat {{
    text-align: right;
}}
.hero-stat-val {{
    font-family: 'DM Mono', monospace;
    font-size: 32px;
    font-weight: 500;
    color: {TEXT_HI};
    line-height: 1;
}}
.hero-stat-val span {{ color: {CYAN}; }}
.hero-stat-lbl {{
    font-size: 10px;
    color: {TEXT_LO};
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-top: 4px;
}}

/* ── KPI cards ── */
.kpi-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 24px;
    animation: fadeInUp 0.6s ease 0.1s both;
}}
.kpi-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 14px;
    padding: 20px 22px;
    position: relative;
    overflow: hidden;
    cursor: default;
    transition: border-color 0.25s, transform 0.25s;
}}
.kpi-card:hover {{
    border-color: {BORDER_LIT};
    transform: translateY(-2px);
}}
.kpi-card::before {{
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
}}
.kpi-card.cyan::before   {{ background: linear-gradient(90deg, {CYAN}, transparent); }}
.kpi-card.blue::before   {{ background: linear-gradient(90deg, {BLUE}, transparent); }}
.kpi-card.emerald::before{{ background: linear-gradient(90deg, {EMERALD}, transparent); }}
.kpi-card.amber::before  {{ background: linear-gradient(90deg, {AMBER}, transparent); }}
.kpi-icon {{
    font-size: 18px;
    margin-bottom: 12px;
}}
.kpi-label {{
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    color: {TEXT_LO};
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 6px;
}}
.kpi-value {{
    font-size: 28px;
    font-weight: 800;
    color: {TEXT_HI};
    line-height: 1;
    letter-spacing: -0.5px;
    margin-bottom: 8px;
}}
.kpi-sub {{
    font-size: 11px;
    color: {TEXT_LO};
    font-weight: 300;
}}
.kpi-sub b {{ color: {EMERALD}; font-weight: 600; }}

/* ── Section header ── */
.sec-head {{
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 28px 0 16px 0;
    animation: fadeInUp 0.5s ease both;
}}
.sec-line {{
    width: 3px;
    height: 22px;
    border-radius: 3px;
    flex-shrink: 0;
}}
.sec-title {{
    font-size: 13px;
    font-weight: 700;
    color: {TEXT_HI};
    letter-spacing: 2px;
    text-transform: uppercase;
    font-family: 'DM Mono', monospace;
}}
.sec-desc {{
    margin-left: auto;
    font-size: 11px;
    color: {TEXT_LO};
}}

/* ── Chart card ── */
.chart-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
    animation: fadeInUp 0.5s ease both;
}}
.chart-card-title {{
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: {TEXT_LO};
    letter-spacing: 2px;
    text-transform: uppercase;
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 1px solid {BORDER};
    display: flex;
    align-items: center;
    gap: 8px;
}}
.chart-card-title span {{ color: {CYAN}; }}

/* ── Cluster cards ── */
.cluster-grid {{
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 14px;
    margin-bottom: 16px;
}}
.cluster-card {{
    background: {BG_CARD};
    border-radius: 16px;
    padding: 24px;
    border: 1px solid {BORDER};
    position: relative;
    overflow: hidden;
    transition: transform 0.25s, border-color 0.25s;
}}
.cluster-card:hover {{
    transform: translateY(-3px);
}}
.cluster-card .glow {{
    position: absolute;
    width: 120px; height: 120px;
    border-radius: 50%;
    filter: blur(40px);
    opacity: 0.15;
    top: -20px; right: -20px;
}}
.cluster-card .tag {{
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 4px 10px;
    border-radius: 20px;
    margin-bottom: 16px;
}}
.cluster-card .big-num {{
    font-size: 44px;
    font-weight: 900;
    line-height: 1;
    letter-spacing: -2px;
    margin-bottom: 4px;
}}
.cluster-card .sub-label {{
    font-size: 10px;
    color: {TEXT_LO};
    letter-spacing: 1px;
    text-transform: uppercase;
    margin-bottom: 20px;
    font-family: 'DM Mono', monospace;
}}
.cluster-card .stat-row {{
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
    margin-top: 4px;
}}
.cluster-card .stat-box {{
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 10px;
    padding: 10px 12px;
}}
.cluster-card .stat-lbl {{
    font-size: 8px;
    color: {TEXT_LO};
    letter-spacing: 1.5px;
    text-transform: uppercase;
    margin-bottom: 4px;
    font-family: 'DM Mono', monospace;
}}
.cluster-card .stat-val {{
    font-size: 18px;
    font-weight: 700;
    line-height: 1;
}}

/* ── Insight ── */
.insight {{
    background: linear-gradient(135deg, rgba(34,211,238,0.04), rgba(59,130,246,0.03));
    border: 1px solid rgba(34,211,238,0.1);
    border-left: 3px solid {CYAN};
    border-radius: 0 12px 12px 0;
    padding: 14px 18px;
    margin-top: 10px;
    font-size: 12.5px;
    color: {TEXT_LO};
    line-height: 1.7;
}}
.insight strong {{ color: {CYAN}; font-weight: 600; }}

/* ── Footer ── */
.footer {{
    text-align: center;
    padding: 32px 0 12px;
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: {TEXT_LO};
    letter-spacing: 2px;
    text-transform: uppercase;
    border-top: 1px solid {BORDER};
    margin-top: 32px;
}}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# LOAD DATA
# ═══════════════════════════════════════════════════════════
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


# ═══════════════════════════════════════════════════════════
# SIDEBAR
# ═══════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown(f"""
    <div style="padding:8px 0 20px 0;">
      <div style="font-family:'DM Mono',monospace; font-size:9px; color:{CYAN};
                  letter-spacing:3px; text-transform:uppercase; margin-bottom:6px;">Dashboard</div>
      <div style="font-size:22px; font-weight:800; color:{TEXT_HI}; letter-spacing:-0.5px;">BikeShare</div>
      <div style="font-size:11px; color:{TEXT_LO}; margin-top:2px;">Capital Bikeshare · D.C.</div>
    </div>
    <div style="height:1px; background:linear-gradient(90deg,{CYAN},transparent);
                margin-bottom:20px; opacity:0.3;"></div>
    """, unsafe_allow_html=True)

    st.markdown(f"<div style='font-size:10px; color:{TEXT_LO}; letter-spacing:2px; text-transform:uppercase; margin-bottom:10px; font-family:DM Mono,monospace;'>Filter</div>", unsafe_allow_html=True)

    selected_yr      = st.selectbox("Tahun",  ['Semua','2011','2012'])
    selected_season  = st.selectbox("Musim",  ['Semua','Spring','Summer','Fall','Winter'])
    selected_weather = st.selectbox("Cuaca",  ['Semua','Clear','Mist','Light Snow/Rain'])
    workday_filter   = st.selectbox("Tipe Hari", ['Semua','Hari Kerja','Hari Libur'])

    st.markdown(f"""
    <div style="height:1px; background:{BORDER}; margin:20px 0;"></div>
    <div style="font-size:10px; color:{TEXT_LO}; font-family:'DM Mono',monospace; line-height:2;">
        <div>📍 Washington D.C., USA</div>
        <div>📅 Jan 2011 – Des 2012</div>
        <div>🗃️ 731 hari · 17.379 jam</div>
        <div>🏷️ UCI ML Repository</div>
    </div>
    <div style="height:1px; background:{BORDER}; margin:20px 0;"></div>
    <div style="font-size:9px; color:{TEXT_LO}; font-family:'DM Mono',monospace; line-height:2; letter-spacing:1px;">
        PROYEK AKHIR · DICODING<br>
        NAJWA SALSABILA
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# FILTER
# ═══════════════════════════════════════════════════════════
fd = day_df.copy()
fh = hour_df.copy()

if selected_yr      != 'Semua': fd=fd[fd['yr_label']==selected_yr];      fh=fh[fh['yr_label']==selected_yr]
if selected_season  != 'Semua': fd=fd[fd['season_label']==selected_season]
if selected_weather != 'Semua': fd=fd[fd['weather_label']==selected_weather]
if workday_filter == 'Hari Kerja':  fd=fd[fd['workingday']==1]; fh=fh[fh['workingday']==1]
if workday_filter == 'Hari Libur':  fd=fd[fd['workingday']==0]; fh=fh[fh['workingday']==0]


# ═══════════════════════════════════════════════════════════
# HERO
# ═══════════════════════════════════════════════════════════
total_rides = fd['cnt'].sum()
avg_daily   = fd['cnt'].mean()
pct_growth  = ((day_df[day_df['year']==2012]['cnt'].mean() /
                day_df[day_df['year']==2011]['cnt'].mean()) - 1) * 100

st.markdown(f"""
<div class="hero-wrap">
  <div class="hero-eyebrow">// bike sharing analytics dashboard</div>
  <h1 class="hero-title">Bike<em>Share</em><br>Analytics</h1>
  <p class="hero-desc">
    Analisis mendalam pola penggunaan layanan Capital Bikeshare
    Washington D.C. — cuaca, musim, jam sibuk, dan segmentasi pengguna.
  </p>
  <div class="hero-badge">
    <span>●</span> LIVE DATA · 2011–2012
  </div>
  <div class="hero-stat-row">
    <div class="hero-stat">
      <div class="hero-stat-val">{total_rides/1e6:.2f}<span>M</span></div>
      <div class="hero-stat-lbl">Total Peminjaman</div>
    </div>
    <div class="hero-stat">
      <div class="hero-stat-val">+{pct_growth:.0f}<span>%</span></div>
      <div class="hero-stat-lbl">Growth 2011→2012</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# KPI CARDS
# ═══════════════════════════════════════════════════════════
total_c  = fd['casual'].sum()
total_r  = fd['registered'].sum()
peak_day = fd.loc[fd['cnt'].idxmax(), 'dteday'].strftime('%d %b %Y') if len(fd) > 0 else '-'

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card cyan">
    <div class="kpi-icon">🚴</div>
    <div class="kpi-label">Total Peminjaman</div>
    <div class="kpi-value">{total_rides/1e6:.2f}M</div>
    <div class="kpi-sub">Selama periode yang dipilih</div>
  </div>
  <div class="kpi-card blue">
    <div class="kpi-icon">📊</div>
    <div class="kpi-label">Rata-rata Harian</div>
    <div class="kpi-value">{avg_daily:,.0f}</div>
    <div class="kpi-sub"><b>↑</b> peminjaman per hari</div>
  </div>
  <div class="kpi-card emerald">
    <div class="kpi-icon">✅</div>
    <div class="kpi-label">Pengguna Registered</div>
    <div class="kpi-value">{total_r/total_rides*100:.1f}%</div>
    <div class="kpi-sub">{total_r/1e6:.2f}M total registered</div>
  </div>
  <div class="kpi-card amber">
    <div class="kpi-icon">🗓️</div>
    <div class="kpi-label">Hari Tersibuk</div>
    <div class="kpi-value" style="font-size:18px; padding-top:6px;">{peak_day}</div>
    <div class="kpi-sub">{fd['cnt'].max():,.0f} peminjaman</div>
  </div>
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# SECTION 1 — TREN
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="sec-head">
  <div class="sec-line" style="background:linear-gradient(180deg,{CYAN},{BLUE});"></div>
  <div class="sec-title">01 — Tren Peminjaman</div>
  <div class="sec-desc">Total bulanan & pertumbuhan tahunan</div>
</div>
""", unsafe_allow_html=True)

c1, c2 = st.columns([3, 2])

with c1:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-card-title"><span>▸</span> Total Peminjaman Bulanan</div>', unsafe_allow_html=True)

    monthly = day_df.groupby(['year','month'])['cnt'].sum().reset_index()
    months  = ['Jan','Feb','Mar','Apr','Mei','Jun','Jul','Agt','Sep','Okt','Nov','Des']

    fig = go.Figure()
    colors_yr = {2011: CYAN, 2012: AMBER}
    for yr, grp in monthly.groupby('year'):
        grp = grp.sort_values('month')
        fig.add_trace(go.Scatter(
            x=grp['month'], y=grp['cnt'],
            name=str(yr),
            mode='lines+markers',
            line=dict(color=colors_yr[yr], width=2.5, shape='spline'),
            marker=dict(size=7, color=colors_yr[yr],
                        line=dict(color=BG_CARD, width=2)),
            fill='tozeroy',
            fillcolor=f"rgba({','.join(str(int(colors_yr[yr].lstrip('#')[i:i+2],16)) for i in (0,2,4))},0.06)",
            hovertemplate=f"<b>{yr}</b> · %{{x}}<br>Peminjaman: <b>%{{y:,.0f}}</b><extra></extra>"
        ))

    fig.update_layout(
        **PLOTLY_LAYOUT,
        height=280,
        xaxis=dict(
            tickvals=list(range(1,13)),
            ticktext=months,
            gridcolor=BORDER,
            tickfont=dict(color=TEXT_LO, size=10),
        ),
        yaxis=dict(
            gridcolor=BORDER,
            tickfont=dict(color=TEXT_LO),
            tickformat=',.0f'
        ),
        legend=dict(x=0.01, y=0.99, bgcolor='rgba(0,0,0,0)',
                    borderwidth=0, font=dict(size=11))
    )
    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar':False})
    st.markdown('</div>', unsafe_allow_html=True)

with c2:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-card-title"><span>▸</span> Distribusi Pengguna</div>', unsafe_allow_html=True)

    fig2 = go.Figure()
    fig2.add_trace(go.Pie(
        labels=['Registered','Casual'],
        values=[total_r, total_c],
        hole=0.65,
        marker=dict(colors=[CYAN, AMBER],
                    line=dict(color=BG_CARD, width=4)),
        textfont=dict(color=TEXT_MED, size=11),
        hovertemplate="<b>%{label}</b><br>Total: %{value:,.0f}<br>Porsi: %{percent}<extra></extra>"
    ))
    fig2.add_annotation(
        text=f"<b>{total_r/total_rides*100:.0f}%</b><br><span style='font-size:10px'>Registered</span>",
        x=0.5, y=0.5, showarrow=False,
        font=dict(size=16, color=TEXT_HI),
        align='center'
    )
    fig2.update_layout(
        **PLOTLY_LAYOUT,
        height=280,
        showlegend=True,
        legend=dict(orientation='h', x=0.5, xanchor='center', y=-0.08)
    )
    st.plotly_chart(fig2, use_container_width=True, config={'displayModeBar':False})
    st.markdown('</div>', unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# SECTION 2 — CUACA & MUSIM
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="sec-head">
  <div class="sec-line" style="background:linear-gradient(180deg,{EMERALD},{CYAN});"></div>
  <div class="sec-title">02 — Cuaca & Musim</div>
  <div class="sec-desc">Pengaruh kondisi lingkungan terhadap peminjaman</div>
</div>
""", unsafe_allow_html=True)

c3, c4 = st.columns(2)

with c3:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-card-title"><span>▸</span> Rata-rata per Kondisi Cuaca</div>', unsafe_allow_html=True)

    w_order  = ['Clear','Mist','Light Snow/Rain']
    w_avg    = day_df.groupby('weather_label')['cnt'].mean().reindex(w_order).dropna().reset_index()
    w_colors = [CYAN, BLUE, VIOLET]

    fig3 = go.Figure()
    fig3.add_trace(go.Bar(
        x=w_avg['weather_label'], y=w_avg['cnt'],
        marker=dict(
            color=w_colors,
            line=dict(width=0),
            cornerradius=8,
        ),
        text=[f"{v:,.0f}" for v in w_avg['cnt']],
        textposition='outside',
        textfont=dict(color=TEXT_MED, size=11),
        hovertemplate="<b>%{x}</b><br>Rata-rata: <b>%{y:,.0f}</b><extra></extra>"
    ))
    fig3.update_layout(
        **PLOTLY_LAYOUT,
        height=270,
        yaxis=dict(gridcolor=BORDER, tickformat=',.0f', tickfont=dict(color=TEXT_LO)),
        xaxis=dict(tickfont=dict(color=TEXT_MED, size=11), gridcolor='rgba(0,0,0,0)'),
        bargap=0.4,
    )
    st.plotly_chart(fig3, use_container_width=True, config={'displayModeBar':False})
    st.markdown('</div>', unsafe_allow_html=True)

with c4:
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.markdown(f'<div class="chart-card-title"><span>▸</span> Rata-rata per Musim</div>', unsafe_allow_html=True)

    s_order  = ['Spring','Summer','Fall','Winter']
    s_avg    = day_df.groupby('season_label')['cnt'].mean().reindex(s_order).reset_index()
    s_colors = [EMERALD, AMBER, ROSE, BLUE]

    fig4 = go.Figure()
    fig4.add_trace(go.Bar(
        x=s_avg['season_label'], y=s_avg['cnt'],
        marker=dict(color=s_colors, line=dict(width=0), cornerradius=8),
        text=[f"{v:,.0f}" for v in s_avg['cnt']],
        textposition='outside',
        textfont=dict(color=TEXT_MED, size=11),
        hovertemplate="<b>%{x}</b><br>Rata-rata: <b>%{y:,.0f}</b><extra></extra>"
    ))
    # Highlight bar tertinggi
    best = s_avg['cnt'].argmax()
    fig4.add_annotation(
        x=s_avg['season_label'].iloc[best],
        y=s_avg['cnt'].iloc[best] + 350,
        text="★ TERTINGGI",
        showarrow=False,
        font=dict(size=9, color=ROSE),
        xanchor='center'
    )
    fig4.update_layout(
        **PLOTLY_LAYOUT,
        height=270,
        yaxis=dict(gridcolor=BORDER, tickformat=',.0f', tickfont=dict(color=TEXT_LO)),
        xaxis=dict(tickfont=dict(color=TEXT_MED, size=11), gridcolor='rgba(0,0,0,0)'),
        bargap=0.4,
    )
    st.plotly_chart(fig4, use_container_width=True, config={'displayModeBar':False})
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="insight">
  Cuaca <strong>Clear</strong> menghasilkan rata-rata <strong>~4.877 peminjaman/hari</strong>,
  sedangkan <strong>Light Snow/Rain</strong> hanya ~1.803/hari — turun <strong>63%</strong>.
  Musim <strong>Fall</strong> adalah musim tersibuk (~5.644/hari) karena suhu nyaman dan cuaca stabil.
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# SECTION 3 — POLA JAM
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="sec-head">
  <div class="sec-line" style="background:linear-gradient(180deg,{AMBER},{ROSE});"></div>
  <div class="sec-title">03 — Pola Per Jam</div>
  <div class="sec-desc">Hari kerja vs hari libur · heatmap mingguan</div>
</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["📈  Hari Kerja vs Hari Libur", "🗓️  Heatmap Mingguan"])

with tab1:
    wd  = hour_df[hour_df['workingday']==1].groupby('hr')[['casual','registered','cnt']].mean()
    wkd = hour_df[hour_df['workingday']==0].groupby('hr')[['casual','registered','cnt']].mean()

    fig5 = make_subplots(
        rows=1, cols=2,
        subplot_titles=["Hari Kerja (Mon–Fri)", "Hari Libur / Weekend"],
        horizontal_spacing=0.08
    )

    for col_idx, (data, label) in enumerate([(wd,'Hari Kerja'), (wkd,'Hari Libur')], 1):
        hrs = list(range(24))
        c = col_idx

        # Fill area
        fig5.add_trace(go.Scatter(
            x=hrs, y=data['cnt'], name=f'Total ({label})',
            mode='lines', line=dict(color=TEXT_HI, width=2.5),
            fill='tozeroy', fillcolor=f"rgba(249,250,251,0.04)",
            hovertemplate="Jam %{x}:00<br>Total: <b>%{y:,.0f}</b><extra></extra>",
            showlegend=(c==1)
        ), row=1, col=c)

        fig5.add_trace(go.Scatter(
            x=hrs, y=data['registered'], name=f'Registered',
            mode='lines', line=dict(color=CYAN, width=1.8, dash='dot'),
            fill='tozeroy', fillcolor=f"rgba(34,211,238,0.05)",
            hovertemplate="Jam %{x}:00<br>Registered: <b>%{y:,.0f}</b><extra></extra>",
            showlegend=(c==1)
        ), row=1, col=c)

        fig5.add_trace(go.Scatter(
            x=hrs, y=data['casual'], name=f'Casual',
            mode='lines', line=dict(color=AMBER, width=1.8, dash='dot'),
            fill='tozeroy', fillcolor=f"rgba(245,158,11,0.05)",
            hovertemplate="Jam %{x}:00<br>Casual: <b>%{y:,.0f}</b><extra></extra>",
            showlegend=(c==1)
        ), row=1, col=c)

        # Annotation puncak
        peak = data['cnt'].idxmax()
        fig5.add_annotation(
            x=peak, y=data['cnt'].max(),
            text=f"⬆ {peak}:00<br>{data['cnt'].max():,.0f}",
            showarrow=True, arrowhead=0,
            arrowcolor=ROSE, font=dict(size=9, color=ROSE),
            ax=0, ay=-40, row=1, col=c
        )

    fig5.update_layout(
        **PLOTLY_LAYOUT,
        height=340,
        legend=dict(x=0.01, y=0.98, bgcolor='rgba(0,0,0,0)', borderwidth=0),
    )
    for i in [1,2]:
        fig5.update_xaxes(tickvals=list(range(0,24,3)), ticktext=[f"{h}" for h in range(0,24,3)],
                          gridcolor=BORDER, tickfont=dict(color=TEXT_LO, size=9), row=1, col=i)
        fig5.update_yaxes(gridcolor=BORDER, tickfont=dict(color=TEXT_LO), row=1, col=i)
    fig5.update_annotations(font_size=10)

    st.plotly_chart(fig5, use_container_width=True, config={'displayModeBar':False})

    st.markdown(f"""
    <div class="insight">
      <strong>Hari Kerja:</strong> Pola bimodal — puncak pukul <strong>08:00</strong> (berangkat) dan
      <strong>17:00–18:00</strong> (pulang). Pengguna <strong>registered</strong> dominan. &nbsp;|&nbsp;
      <strong>Hari Libur:</strong> Pola unimodal — puncak siang <strong>11:00–14:00</strong>.
      Proporsi <strong>casual</strong> jauh lebih tinggi.
    </div>
    """, unsafe_allow_html=True)

with tab2:
    day_order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
    pivot = (hour_df.pivot_table(index='weekday_label', columns='hr', values='cnt', aggfunc='mean')
             .reindex(day_order))

    fig6 = go.Figure(go.Heatmap(
        z=pivot.values,
        x=[f"{h:02d}:00" for h in range(24)],
        y=day_order,
        colorscale=[
            [0.0,  '#0d1117'],
            [0.25, '#0e3a4f'],
            [0.5,  '#0e7490'],
            [0.75, '#f59e0b'],
            [1.0,  '#f43f5e']
        ],
        showscale=True,
        colorbar=dict(
            title=dict(text='Avg', font=dict(color=TEXT_LO, size=10)),
            tickfont=dict(color=TEXT_LO, size=9),
            thickness=10,
            len=0.8,
        ),
        hovertemplate="<b>%{y}</b> pukul <b>%{x}</b><br>Rata-rata: <b>%{z:,.0f}</b><extra></extra>",
        xgap=2, ygap=2
    ))
    fig6.update_layout(
        **PLOTLY_LAYOUT,
        height=300,
        xaxis=dict(tickfont=dict(color=TEXT_LO, size=9), gridcolor='rgba(0,0,0,0)',
                   tickangle=0, side='bottom'),
        yaxis=dict(tickfont=dict(color=TEXT_MED, size=11), gridcolor='rgba(0,0,0,0)'),
    )
    st.plotly_chart(fig6, use_container_width=True, config={'displayModeBar':False})

    st.markdown(f"""
    <div class="insight">
      Heatmap mengonfirmasi <strong>jam 07:00–09:00 dan 17:00–19:00 pada Senin–Jumat</strong>
      adalah periode tersibuk. Sabtu–Minggu menunjukkan pola merata di siang hari tanpa lonjakan tajam.
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# SECTION 4 — CLUSTERING
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="sec-head">
  <div class="sec-line" style="background:linear-gradient(180deg,{VIOLET},{INDIGO});"></div>
  <div class="sec-title">04 — Segmentasi Penggunaan</div>
  <div class="sec-desc">Clustering manual berbasis persentil</div>
</div>
""", unsafe_allow_html=True)

p33 = day_df['cnt'].quantile(0.33)
p67 = day_df['cnt'].quantile(0.67)
day_df['usage_cluster'] = pd.cut(
    day_df['cnt'],
    bins=[0, p33, p67, day_df['cnt'].max()+1],
    labels=['Low Usage','Medium Usage','High Usage']
)
profile = day_df.groupby('usage_cluster', observed=True).agg(
    Jumlah=('cnt','count'), Rata_cnt=('cnt','mean'),
    Casual=('casual','mean'), Registered=('registered','mean'),
    Temp=('temp','mean'), Pct_WD=('workingday','mean')
).round(2)

CLUS = {
    'Low Usage':    {'color': ROSE,    'glow': ROSE,    'tag_bg':'rgba(244,63,94,0.1)',    'tag_border':'rgba(244,63,94,0.25)'},
    'Medium Usage': {'color': AMBER,   'glow': AMBER,   'tag_bg':'rgba(245,158,11,0.1)',   'tag_border':'rgba(245,158,11,0.25)'},
    'High Usage':   {'color': EMERALD, 'glow': EMERALD, 'tag_bg':'rgba(16,185,129,0.1)',   'tag_border':'rgba(16,185,129,0.25)'},
}

st.markdown('<div class="cluster-grid">', unsafe_allow_html=True)
for cl in ['Low Usage','Medium Usage','High Usage']:
    row   = profile.loc[cl]
    c_cfg = CLUS[cl]
    icon  = {'Low Usage':'↘','Medium Usage':'→','High Usage':'↗'}[cl]
    st.markdown(f"""
    <div class="cluster-card" style="border-color: rgba({','.join(str(int(c_cfg['color'].lstrip('#')[i:i+2],16)) for i in (0,2,4))},0.2);">
      <div class="glow" style="background:{c_cfg['glow']};"></div>
      <div class="tag" style="background:{c_cfg['tag_bg']}; border:1px solid {c_cfg['tag_border']}; color:{c_cfg['color']};">
        {icon} {cl.upper()}
      </div>
      <div class="big-num" style="color:{c_cfg['color']};">{row['Rata_cnt']:,.0f}</div>
      <div class="sub-label">rata-rata cnt / hari</div>
      <div class="stat-row">
        <div class="stat-box">
          <div class="stat-lbl">Casual</div>
          <div class="stat-val" style="color:{AMBER};">{row['Casual']:,.0f}</div>
        </div>
        <div class="stat-box">
          <div class="stat-lbl">Registered</div>
          <div class="stat-val" style="color:{CYAN};">{row['Registered']:,.0f}</div>
        </div>
        <div class="stat-box">
          <div class="stat-lbl">Avg Suhu</div>
          <div class="stat-val" style="color:{EMERALD};">{row['Temp']:.3f}</div>
        </div>
        <div class="stat-box">
          <div class="stat-lbl">% Hari Kerja</div>
          <div class="stat-val" style="color:{VIOLET};">{row['Pct_WD']*100:.0f}%</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Cluster interactive chart
st.markdown('<div class="chart-card">', unsafe_allow_html=True)
st.markdown(f'<div class="chart-card-title"><span>▸</span> Distribusi & Komposisi Cluster</div>', unsafe_allow_html=True)

fig7 = make_subplots(
    rows=1, cols=3,
    subplot_titles=['Distribusi cnt per Cluster','Casual vs Registered','Komposisi Musim (%)'],
    horizontal_spacing=0.1
)

# 1 – Histogram
for cl, col in [('Low Usage',ROSE),('Medium Usage',AMBER),('High Usage',EMERALD)]:
    data = day_df[day_df['usage_cluster']==cl]['cnt']
    fig7.add_trace(go.Histogram(
        x=data, name=cl, marker_color=col,
        opacity=0.75, nbinsx=18,
        hovertemplate=f"<b>{cl}</b><br>Rentang: %{{x}}<br>Jumlah: %{{y}}<extra></extra>"
    ), row=1, col=1)

# 2 – Grouped bar
cl_labels = ['Low Usage','Medium Usage','High Usage']
cl_colors  = [ROSE, AMBER, EMERALD]
fig7.add_trace(go.Bar(
    name='Casual', x=cl_labels,
    y=[profile.loc[c,'Casual'] for c in cl_labels],
    marker_color=AMBER, marker_line_width=0, opacity=0.85,
    hovertemplate="%{x}<br>Casual: <b>%{y:,.0f}</b><extra></extra>"
), row=1, col=2)
fig7.add_trace(go.Bar(
    name='Registered', x=cl_labels,
    y=[profile.loc[c,'Registered'] for c in cl_labels],
    marker_color=CYAN, marker_line_width=0, opacity=0.85,
    hovertemplate="%{x}<br>Registered: <b>%{y:,.0f}</b><extra></extra>"
), row=1, col=2)

# 3 – Stacked bar musim
season_cl = (day_df.groupby(['usage_cluster','season_label'], observed=True)
             .size().reset_index(name='count'))
sp = season_cl.pivot_table(index='usage_cluster', columns='season_label',
                            values='count', observed=True).fillna(0)
sp_pct = (sp.div(sp.sum(axis=1), axis=0)*100).reindex(['Low Usage','Medium Usage','High Usage'])
s_clrs = {'Fall':ROSE,'Spring':EMERALD,'Summer':AMBER,'Winter':BLUE}

for season in sp_pct.columns:
    fig7.add_trace(go.Bar(
        name=season,
        x=['Low','Med','High'],
        y=sp_pct[season].values,
        marker_color=s_clrs.get(season, TEXT_LO),
        marker_line_width=0,
        hovertemplate=f"<b>{season}</b>: %{{y:.1f}}%<extra></extra>"
    ), row=1, col=3)

fig7.update_layout(
    **PLOTLY_LAYOUT,
    height=300,
    barmode='group',
    legend=dict(
        x=1.01, y=0.5,
        bgcolor='rgba(0,0,0,0)', borderwidth=0,
        font=dict(size=9)
    ),
)
for i in [1,2,3]:
    fig7.update_xaxes(gridcolor='rgba(0,0,0,0)', tickfont=dict(size=9, color=TEXT_LO), row=1, col=i)
    fig7.update_yaxes(gridcolor=BORDER, tickfont=dict(size=9, color=TEXT_LO), row=1, col=i)

# Fix subplot 3 ke stacked
fig7.update_layout(barmode='stack')

st.plotly_chart(fig7, use_container_width=True, config={'displayModeBar':False})
st.markdown('</div>', unsafe_allow_html=True)

st.markdown(f"""
<div class="insight">
  <strong>Low Usage</strong> — didominasi Spring & Winter, suhu rendah (~0.37).
  <strong>High Usage</strong> — erat kaitannya dengan Fall/Summer, suhu hangat (~0.59).
  Proporsi hari kerja merata di ketiga cluster (~67–73%) → <strong>cuaca dan musim jauh lebih
  berpengaruh</strong> daripada hari kerja/libur dalam menentukan tingkat penggunaan.
</div>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════
st.markdown(f"""
<div class="footer">
  BikeShare Analytics &nbsp;·&nbsp; Dicoding &nbsp;·&nbsp;
  Najwa Salsabila &nbsp;·&nbsp; 2024
</div>
""", unsafe_allow_html=True)
