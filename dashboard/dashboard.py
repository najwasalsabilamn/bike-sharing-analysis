import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots

# ============================================================
# PAGE CONFIG
# ============================================================
st.set_page_config(
    page_title="Bike Sharing Dashboard",
    page_icon="🚲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================
# CSS
# ============================================================
st.markdown("""
<style>
    .main { background-color: #F8FAFC; }
    .metric-card {
        background: white;
        padding: 18px 20px;
        border-radius: 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.07);
        text-align: center;
    }
    .metric-card h4 { color: #666; font-size: 13px; margin: 0 0 6px 0; text-transform: uppercase; letter-spacing: 0.5px; }
    .metric-card h2 { color: #1565C0; font-size: 28px; margin: 0 0 4px 0; }
    .metric-card p  { color: #999; font-size: 12px; margin: 0; }
    .section-header {
        background: linear-gradient(90deg, #1565C0, #42A5F5);
        color: white;
        padding: 10px 18px;
        border-radius: 8px;
        font-weight: bold;
        margin: 16px 0 10px 0;
    }
    .insight-box {
        background: #E3F2FD;
        border-left: 4px solid #1565C0;
        padding: 12px 16px;
        border-radius: 0 8px 8px 0;
        margin: 8px 0;
    }
</style>
""", unsafe_allow_html=True)


# ============================================================
# LOAD & PREPARE DATA
# ============================================================
@st.cache_data
def load_data():
    day_df  = pd.read_csv('dashboard/main_data.csv')
    hour_df = pd.read_csv('data/hour.csv')

    season_map  = {1:'Spring', 2:'Summer', 3:'Fall', 4:'Winter'}
    weather_map = {1:'Clear',  2:'Mist',   3:'Light Snow/Rain', 4:'Heavy Rain'}
    weekday_map = {0:'Sun', 1:'Mon', 2:'Tue', 3:'Wed', 4:'Thu', 5:'Fri', 6:'Sat'}
    yr_map      = {0:'2011', 1:'2012'}

    for df in [day_df, hour_df]:
        df['dteday']        = pd.to_datetime(df['dteday'])
        df['year']          = df['dteday'].dt.year
        df['month']         = df['dteday'].dt.month
        df['season_label']  = df['season'].map(season_map)
        df['weather_label'] = df['weathersit'].map(weather_map)
        df['weekday_label'] = df['weekday'].map(weekday_map)
        df['yr_label']      = df['yr'].map(yr_map)

    # Clustering persentil
    p33 = day_df['cnt'].quantile(0.33)
    p67 = day_df['cnt'].quantile(0.67)
    day_df['usage_cluster'] = pd.cut(
        day_df['cnt'],
        bins=[0, p33, p67, day_df['cnt'].max()+1],
        labels=['Low Usage', 'Medium Usage', 'High Usage']
    )
    return day_df, hour_df, p33, p67


day_df, hour_df, P33, P67 = load_data()


# ============================================================
# SIDEBAR
# ============================================================
st.sidebar.image("https://img.icons8.com/color/96/bicycle.png", width=80)
st.sidebar.title("🚲 Bike Sharing")
st.sidebar.caption("Capital Bikeshare · Washington D.C. · 2011–2012")
st.sidebar.markdown("---")

st.sidebar.subheader("Filter Data")
selected_yr = st.sidebar.selectbox("📅 Tahun", ['Semua', '2011', '2012'])

month_names = {1:'Jan',2:'Feb',3:'Mar',4:'Apr',5:'Mei',6:'Jun',
               7:'Jul',8:'Agu',9:'Sep',10:'Okt',11:'Nov',12:'Des'}
all_months = sorted(day_df['month'].unique())
selected_months = st.sidebar.multiselect(
    "📆 Bulan",
    options=all_months,
    default=all_months,
    format_func=lambda x: month_names[x]
)

season_opts = ['Semua'] + sorted(day_df['season_label'].dropna().unique().tolist())
selected_season = st.sidebar.selectbox("🌸 Musim", season_opts)

weather_opts = ['Semua'] + sorted(day_df['weather_label'].dropna().unique().tolist())
selected_weather = st.sidebar.selectbox("🌤️ Kondisi Cuaca", weather_opts)

st.sidebar.markdown("---")
st.sidebar.markdown("""
**ℹ️ Pertanyaan Bisnis:**
1. Perbedaan rata-rata peminjaman per cuaca & musim
2. Jam puncak hari kerja vs hari libur & komposisi pengguna
3. Profil segmen Low/Medium/High Usage
""")

# ============================================================
# APPLY FILTERS
# ============================================================
fd = day_df.copy()
fh = hour_df.copy()

if selected_yr != 'Semua':
    fd = fd[fd['yr_label'] == selected_yr]
    fh = fh[fh['yr_label'] == selected_yr]

if selected_months:
    fd = fd[fd['month'].isin(selected_months)]
    fh = fh[fh['month'].isin(selected_months)]

if selected_season != 'Semua':
    fd = fd[fd['season_label'] == selected_season]
    fh = fh[fh['season_label'] == selected_season]

if selected_weather != 'Semua':
    fd = fd[fd['weather_label'] == selected_weather]
    fh = fh[fh['weather_label'] == selected_weather]

empty = fd.empty or fh.empty

# ============================================================
# HEADER
# ============================================================
st.markdown("<h1 style='text-align:center; color:#1565C0;'>🚲 Bike Sharing Dashboard</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align:center; color:#666;'>Capital Bikeshare · Washington D.C. · 2011–2012 | Analisis Peminjaman Sepeda Harian & Per Jam</p>", unsafe_allow_html=True)
st.markdown("---")

if empty:
    st.warning("⚠️ Tidak ada data untuk filter yang dipilih. Silakan sesuaikan filter di sidebar.")
    st.stop()

# ============================================================
# KPI CARDS
# ============================================================
total   = int(fd['cnt'].sum())
avg_day = fd['cnt'].mean()
casual  = int(fd['casual'].sum())
reg     = int(fd['registered'].sum())
n_days  = len(fd)
peak_day_val = int(fd['cnt'].max())
peak_day_dt  = fd.loc[fd['cnt'].idxmax(), 'dteday'].strftime('%d %b %Y')

c1, c2, c3, c4, c5, c6 = st.columns(6)
cards = [
    (c1, "Total Peminjaman",    f"{total:,}",          f"{n_days} hari data"),
    (c2, "Rata-rata Harian",    f"{avg_day:,.0f}",      "peminjaman/hari"),
    (c3, "Pengguna Casual",     f"{casual:,}",          f"{casual/total:.1%} dari total"),
    (c4, "Pengguna Registered", f"{reg:,}",             f"{reg/total:.1%} dari total"),
    (c5, "Puncak Harian",       f"{peak_day_val:,}",    peak_day_dt),
    (c6, "Periode Data",        f"{n_days} hari",       f"{fd['dteday'].min().strftime('%b %Y')} – {fd['dteday'].max().strftime('%b %Y')}"),
]
for col, title, val, sub in cards:
    with col:
        st.markdown(f"""<div class='metric-card'>
            <h4>{title}</h4><h2>{val}</h2><p>{sub}</p>
        </div>""", unsafe_allow_html=True)

st.markdown("")

# ── Trend Bulanan ──
st.markdown("<div class='section-header'>📈 Tren Peminjaman Bulanan</div>", unsafe_allow_html=True)

monthly = fd.groupby(['year','month'], as_index=False)['cnt'].sum()
monthly['period'] = monthly['year'].astype(str) + '-' + monthly['month'].astype(str).str.zfill(2)

fig_trend = px.line(
    monthly, x='period', y='cnt', color='year',
    markers=True, color_discrete_map={2011:'#90CAF9', 2012:'#1565C0'},
    labels={'cnt':'Total Peminjaman','period':'Periode','year':'Tahun'}
)
fig_trend.update_traces(line_width=2.5)
fig_trend.update_layout(
    height=320, margin=dict(l=20,r=20,t=20,b=20),
    plot_bgcolor='white', paper_bgcolor='white',
    xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
    legend_title='Tahun'
)
st.plotly_chart(fig_trend, use_container_width=True)

peak_m  = monthly.loc[monthly['cnt'].idxmax()]
low_m   = monthly.loc[monthly['cnt'].idxmin()]
st.markdown(f"""<div class='insight-box'>
📌 <b>Puncak:</b> {peak_m['period']} ({peak_m['cnt']:,} peminjaman) &nbsp;|&nbsp;
📉 <b>Terendah:</b> {low_m['period']} ({low_m['cnt']:,} peminjaman)
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# PERTANYAAN 1: CUACA & MUSIM
# ============================================================
st.markdown("<div class='section-header'>❓ Pertanyaan 1 — Perbedaan Rata-rata Peminjaman Harian per Kondisi Cuaca & Musim (2011–2012)</div>", unsafe_allow_html=True)
st.caption("Seberapa besar perbedaan rata-rata `cnt` harian antar 3 kondisi cuaca dan 4 musim? Kondisi mana tertinggi dan terendah?")

col_w, col_s = st.columns(2)

with col_w:
    weather_order = ['Clear', 'Mist', 'Light Snow/Rain']
    w_avg = (fd.groupby('weather_label')['cnt']
               .mean().reindex(weather_order).dropna()
               .reset_index())
    w_avg.columns = ['Kondisi Cuaca', 'Rata-rata cnt']
    clear_val = w_avg.loc[w_avg['Kondisi Cuaca']=='Clear','Rata-rata cnt'].values
    w_avg['% vs Clear'] = ((w_avg['Rata-rata cnt'] - (clear_val[0] if len(clear_val) else 0))
                            / (clear_val[0] if len(clear_val) else 1) * 100).round(1)
    color_map_w = {'Clear':'#2196F3', 'Mist':'#90CAF9', 'Light Snow/Rain':'#E3F2FD'}
    fig_w = px.bar(
        w_avg, x='Kondisi Cuaca', y='Rata-rata cnt',
        color='Kondisi Cuaca', color_discrete_map=color_map_w,
        text='Rata-rata cnt',
        title='Rata-rata Peminjaman per Kondisi Cuaca',
        labels={'Rata-rata cnt':'Rata-rata Peminjaman Harian'}
    )
    fig_w.update_traces(texttemplate='<b>%{text:,.0f}</b>', textposition='outside')
    fig_w.update_layout(
        height=380, showlegend=False, plot_bgcolor='white',
        margin=dict(l=10,r=10,t=40,b=10),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
    )
    st.plotly_chart(fig_w, use_container_width=True)
    if len(w_avg) > 0:
        best_w = w_avg.loc[w_avg['Rata-rata cnt'].idxmax(), 'Kondisi Cuaca']
        worst_w = w_avg.loc[w_avg['Rata-rata cnt'].idxmin(), 'Kondisi Cuaca']
        diff_w = w_avg['Rata-rata cnt'].max() - w_avg['Rata-rata cnt'].min()
        st.markdown(f"""<div class='insight-box'>
        ✅ Tertinggi: <b>{best_w}</b> ({w_avg['Rata-rata cnt'].max():,.0f}/hari)<br>
        ❌ Terendah: <b>{worst_w}</b> ({w_avg['Rata-rata cnt'].min():,.0f}/hari)<br>
        📊 Selisih: <b>{diff_w:,.0f}/hari</b> ({abs(w_avg.loc[w_avg['Kondisi Cuaca']==worst_w,'% vs Clear'].values[0]):.0f}% lebih rendah dari Clear)
        </div>""", unsafe_allow_html=True)

with col_s:
    season_order = ['Spring', 'Summer', 'Fall', 'Winter']
    s_avg = (fd.groupby('season_label')['cnt']
               .mean().reindex(season_order).dropna()
               .reset_index())
    s_avg.columns = ['Musim', 'Rata-rata cnt']
    color_map_s = {'Spring':'#A5D6A7','Summer':'#FFF59D','Fall':'#FFCC80','Winter':'#B3E5FC'}
    fig_s = px.bar(
        s_avg, x='Musim', y='Rata-rata cnt',
        color='Musim', color_discrete_map=color_map_s,
        text='Rata-rata cnt',
        title='Rata-rata Peminjaman per Musim',
        labels={'Rata-rata cnt':'Rata-rata Peminjaman Harian'}
    )
    fig_s.update_traces(texttemplate='<b>%{text:,.0f}</b>', textposition='outside')
    fig_s.update_layout(
        height=380, showlegend=False, plot_bgcolor='white',
        margin=dict(l=10,r=10,t=40,b=10),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0')
    )
    st.plotly_chart(fig_s, use_container_width=True)
    if len(s_avg) > 0:
        best_s  = s_avg.loc[s_avg['Rata-rata cnt'].idxmax(), 'Musim']
        worst_s = s_avg.loc[s_avg['Rata-rata cnt'].idxmin(), 'Musim']
        diff_s  = s_avg['Rata-rata cnt'].max() - s_avg['Rata-rata cnt'].min()
        pct_diff = diff_s / s_avg['Rata-rata cnt'].min() * 100
        st.markdown(f"""<div class='insight-box'>
        ✅ Tertinggi: <b>{best_s}</b> ({s_avg['Rata-rata cnt'].max():,.0f}/hari)<br>
        ❌ Terendah: <b>{worst_s}</b> ({s_avg['Rata-rata cnt'].min():,.0f}/hari)<br>
        📊 Selisih: <b>{diff_s:,.0f}/hari</b> ({pct_diff:.0f}% lebih rendah dari {best_s})
        </div>""", unsafe_allow_html=True)

# Tabel ringkasan Q1
with st.expander("📋 Lihat Tabel Ringkasan Pertanyaan 1"):
    t1a = fd.groupby('weather_label')['cnt'].agg(['mean','median','std','count']).round(1)
    t1a.columns = ['Rata-rata','Median','Std Dev','Jumlah Hari']
    t1b = fd.groupby('season_label')['cnt'].agg(['mean','median','std','count']).round(1)
    t1b.columns = ['Rata-rata','Median','Std Dev','Jumlah Hari']
    c1t, c2t = st.columns(2)
    with c1t:
        st.caption("Per Kondisi Cuaca")
        st.dataframe(t1a.sort_values('Rata-rata', ascending=False), use_container_width=True)
    with c2t:
        st.caption("Per Musim")
        st.dataframe(t1b.sort_values('Rata-rata', ascending=False), use_container_width=True)

st.markdown("---")

# ============================================================
# PERTANYAAN 2: JAM PUNCAK
# ============================================================
st.markdown("<div class='section-header'>❓ Pertanyaan 2 — Jam Puncak Peminjaman: Hari Kerja vs Hari Libur & Komposisi Pengguna (2011–2012)</div>", unsafe_allow_html=True)
st.caption("Pukul berapa puncak terjadi? Seberapa besar selisihnya? Bagaimana komposisi casual vs registered pada jam puncak?")

hourly_wd = fh[fh['workingday']==1].groupby('hr')[['casual','registered','cnt']].mean().round(2)
hourly_we = fh[fh['workingday']==0].groupby('hr')[['casual','registered','cnt']].mean().round(2)

col_q2a, col_q2b = st.columns([3, 1])

with col_q2a:
    # Line chart workday vs weekend
    hours = list(range(24))
    fig_hr = go.Figure()
    for data, name, color, dash in [
        (hourly_wd, 'Hari Kerja', '#1565C0', 'solid'),
        (hourly_we, 'Hari Libur', '#FF6F00', 'dash'),
    ]:
        if not data.empty:
            fig_hr.add_trace(go.Scatter(
                x=hours, y=data['cnt'].reindex(hours, fill_value=0),
                mode='lines+markers', name=name,
                line=dict(color=color, width=2.5, dash=dash),
                marker=dict(size=5)
            ))
    fig_hr.update_layout(
        title='Rata-rata Peminjaman per Jam: Hari Kerja vs Hari Libur',
        xaxis_title='Jam (0–23)', yaxis_title='Rata-rata Peminjaman',
        height=380, plot_bgcolor='white',
        xaxis=dict(tickmode='linear', dtick=1, showgrid=False),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        margin=dict(l=10,r=10,t=40,b=10),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    # Anotasi puncak
    if not hourly_wd.empty:
        pk_wd = hourly_wd['cnt'].idxmax()
        fig_hr.add_annotation(
            x=pk_wd, y=hourly_wd['cnt'].max(),
            text=f"Puncak WD<br>{pk_wd}:00 ({hourly_wd['cnt'].max():.0f})",
            showarrow=True, arrowhead=2, ax=-50, ay=-40,
            bgcolor='#E3F2FD', bordercolor='#1565C0', font=dict(size=10)
        )
    if not hourly_we.empty:
        pk_we = hourly_we['cnt'].idxmax()
        fig_hr.add_annotation(
            x=pk_we, y=hourly_we['cnt'].max(),
            text=f"Puncak WE<br>{pk_we}:00 ({hourly_we['cnt'].max():.0f})",
            showarrow=True, arrowhead=2, ax=50, ay=-40,
            bgcolor='#FFF3E0', bordercolor='#FF6F00', font=dict(size=10)
        )
    st.plotly_chart(fig_hr, use_container_width=True)

with col_q2b:
    st.markdown("**Statistik Jam Puncak**")
    if not hourly_wd.empty:
        pk_wd = hourly_wd['cnt'].idxmax()
        wd_cas_pct = hourly_wd['casual'].iloc[pk_wd] / hourly_wd['cnt'].iloc[pk_wd] * 100
        wd_reg_pct = hourly_wd['registered'].iloc[pk_wd] / hourly_wd['cnt'].iloc[pk_wd] * 100
        st.metric("Puncak Hari Kerja", f"{pk_wd}:00", f"{hourly_wd['cnt'].max():.0f} /jam")
        st.caption(f"Registered: **{wd_reg_pct:.0f}%** | Casual: **{wd_cas_pct:.0f}%**")

    if not hourly_we.empty:
        pk_we = hourly_we['cnt'].idxmax()
        we_cas_pct = hourly_we['casual'].iloc[pk_we] / hourly_we['cnt'].iloc[pk_we] * 100
        we_reg_pct = hourly_we['registered'].iloc[pk_we] / hourly_we['cnt'].iloc[pk_we] * 100
        st.metric("Puncak Hari Libur", f"{pk_we}:00", f"{hourly_we['cnt'].max():.0f} /jam")
        st.caption(f"Registered: **{we_reg_pct:.0f}%** | Casual: **{we_cas_pct:.0f}%**")

    if not hourly_wd.empty and not hourly_we.empty:
        diff = hourly_wd['cnt'].max() - hourly_we['cnt'].max()
        pct  = diff / hourly_we['cnt'].max() * 100
        st.markdown(f"""<div class='insight-box' style='margin-top:12px;'>
        Puncak hari kerja <b>{pct:.0f}% lebih tinggi</b> dari hari libur<br>
        Selisih: <b>{diff:.0f} peminjaman/jam</b>
        </div>""", unsafe_allow_html=True)

# Casual vs Registered per jam
st.markdown("**Komposisi Pengguna Casual vs Registered per Jam**")
col_cd, col_ce = st.columns(2)

def make_composition_chart(data, title, peak_hr):
    if data.empty:
        return go.Figure()
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(range(24)), y=data['registered'].reindex(range(24), fill_value=0),
                         name='Registered', marker_color='#1565C0', opacity=0.85))
    fig.add_trace(go.Bar(x=list(range(24)), y=data['casual'].reindex(range(24), fill_value=0),
                         name='Casual', marker_color='#FF6F00', opacity=0.85))
    fig.update_layout(
        barmode='stack', title=title, height=300,
        xaxis_title='Jam', yaxis_title='Rata-rata Peminjaman',
        plot_bgcolor='white', margin=dict(l=10,r=10,t=40,b=10),
        xaxis=dict(tickmode='linear', dtick=2),
        yaxis=dict(gridcolor='#f0f0f0'),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, x=0)
    )
    if peak_hr is not None:
        fig.add_vline(x=peak_hr, line_dash='dash', line_color='red',
                      annotation_text=f'Puncak {peak_hr}:00', annotation_position='top right')
    return fig

with col_cd:
    pk_wd = hourly_wd['cnt'].idxmax() if not hourly_wd.empty else None
    st.plotly_chart(make_composition_chart(hourly_wd, 'Komposisi Pengguna — Hari Kerja', pk_wd),
                    use_container_width=True)

with col_ce:
    pk_we = hourly_we['cnt'].idxmax() if not hourly_we.empty else None
    st.plotly_chart(make_composition_chart(hourly_we, 'Komposisi Pengguna — Hari Libur', pk_we),
                    use_container_width=True)

# Heatmap
st.markdown("**Heatmap Rata-rata Peminjaman per Hari & Jam**")
day_order = ['Mon','Tue','Wed','Thu','Fri','Sat','Sun']
pivot = (fh.pivot_table(index='weekday_label', columns='hr', values='cnt', aggfunc='mean')
          .reindex(day_order))
if not pivot.empty:
    fig_hm = px.imshow(
        pivot, aspect='auto', color_continuous_scale='YlOrRd',
        labels=dict(x='Jam', y='Hari', color='Rata-rata Peminjaman'),
        title='Heatmap: Rata-rata Peminjaman per Hari & Jam (2011–2012)'
    )
    fig_hm.update_layout(height=300, margin=dict(l=10,r=10,t=40,b=10))
    st.plotly_chart(fig_hm, use_container_width=True)

st.markdown("""<div class='insight-box'>
📌 <b>Hari Kerja (bimodal):</b> puncak pagi ~08:00 (berangkat kerja) & puncak sore ~17:00 (pulang kerja) — registered dominan ±85%<br>
📌 <b>Hari Libur (unimodal):</b> puncak siang ~13:00 (rekreasi) — proporsi casual naik ke ±35%<br>
📌 <b>Heatmap:</b> slot 07–09 & 16–19 di Senin–Jumat secara konsisten paling padat sepanjang 2011–2012
</div>""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# PERTANYAAN 3: CLUSTERING
# ============================================================
st.markdown(f"<div class='section-header'>❓ Pertanyaan 3 — Profil Segmen Low/Medium/High Usage: Suhu, Musim, Cuaca & Tipe Pengguna (2011–2012)</div>",
            unsafe_allow_html=True)
st.caption(f"Batas cluster: Low ≤ {P33:.0f} | Medium {P33:.0f}–{P67:.0f} | High > {P67:.0f} peminjaman/hari (berdasarkan persentil ke-33 dan ke-67)")

CLUSTER_COLORS = {'Low Usage':'#EF9A9A', 'Medium Usage':'#FFE082', 'High Usage':'#A5D6A7'}

cluster_df = fd.dropna(subset=['usage_cluster'])

if cluster_df.empty:
    st.warning("Tidak ada data cluster untuk filter yang dipilih.")
else:
    cluster_list = ['Low Usage', 'Medium Usage', 'High Usage']

    cp = cluster_df.groupby('usage_cluster', observed=True).agg(
        Jumlah_Hari     = ('cnt',        'count'),
        Rata_cnt        = ('cnt',        'mean'),
        Rata_casual     = ('casual',     'mean'),
        Rata_registered = ('registered', 'mean'),
        Rata_temp       = ('temp',       'mean'),
        Rata_hum        = ('hum',        'mean'),
        Pct_workingday  = ('workingday', 'mean'),
    ).round(3)

    # ── Row 1: Rata-rata cnt & Casual vs Registered ──
    col3a, col3b, col3c = st.columns(3)

    with col3a:
        avg_cnt = cp['Rata_cnt'].reindex(cluster_list).dropna()
        fig3a = px.bar(
            x=avg_cnt.index, y=avg_cnt.values,
            color=avg_cnt.index,
            color_discrete_map=CLUSTER_COLORS,
            text=[f'{v:,.0f}' for v in avg_cnt.values],
            title='Rata-rata Peminjaman per Segmen',
            labels={'x':'Segmen','y':'Rata-rata cnt'}
        )
        fig3a.update_traces(textposition='outside', textfont_size=12)
        fig3a.update_layout(height=320, showlegend=False, plot_bgcolor='white',
                            margin=dict(l=10,r=10,t=40,b=10),
                            yaxis=dict(gridcolor='#f0f0f0'))
        st.plotly_chart(fig3a, use_container_width=True)

    with col3b:
        reg_vals = cp['Rata_registered'].reindex(cluster_list).dropna()
        cas_vals = cp['Rata_casual'].reindex(cluster_list).dropna()
        fig3b = go.Figure()
        fig3b.add_trace(go.Bar(name='Registered', x=cluster_list,
                                y=reg_vals.reindex(cluster_list, fill_value=0),
                                marker_color='#1565C0', opacity=0.85,
                                text=[f'{v:.0f}' for v in reg_vals.reindex(cluster_list, fill_value=0)],
                                textposition='outside'))
        fig3b.add_trace(go.Bar(name='Casual', x=cluster_list,
                                y=cas_vals.reindex(cluster_list, fill_value=0),
                                marker_color='#FF6F00', opacity=0.85))
        fig3b.update_layout(
            title='Casual vs Registered per Segmen',
            barmode='group', height=320, plot_bgcolor='white',
            margin=dict(l=10,r=10,t=40,b=10),
            yaxis=dict(gridcolor='#f0f0f0'),
            legend=dict(orientation='h', y=1.1, x=0)
        )
        st.plotly_chart(fig3b, use_container_width=True)

    with col3c:
        temp_vals = cp['Rata_temp'].reindex(cluster_list).dropna()
        fig3c = px.bar(
            x=temp_vals.index, y=temp_vals.values,
            color=temp_vals.index,
            color_discrete_map=CLUSTER_COLORS,
            text=[f'{v:.3f}' for v in temp_vals.values],
            title='Rata-rata Suhu Ternormalisasi per Segmen',
            labels={'x':'Segmen','y':'Suhu (0–1)'}
        )
        fig3c.update_traces(textposition='outside', textfont_size=12)
        fig3c.update_layout(height=320, showlegend=False, plot_bgcolor='white',
                            margin=dict(l=10,r=10,t=40,b=10),
                            yaxis=dict(range=[0, 0.8], gridcolor='#f0f0f0'))
        st.plotly_chart(fig3c, use_container_width=True)

    # ── Row 2: Komposisi Musim & Cuaca ──
    col3d, col3e = st.columns(2)

    with col3d:
        season_cl = (cluster_df.groupby(['usage_cluster','season_label'], observed=True)
                     .size().reset_index(name='count'))
        tot_s = season_cl.groupby('usage_cluster', observed=True)['count'].transform('sum')
        season_cl['pct'] = (season_cl['count'] / tot_s * 100).round(1)
        season_pivot = season_cl.pivot_table(
            index='usage_cluster', columns='season_label', values='pct', observed=True
        ).fillna(0).reindex(cluster_list)

        fig3d = go.Figure()
        s_colors = {'Spring':'#A5D6A7','Summer':'#FFF59D','Fall':'#FFCC80','Winter':'#B3E5FC'}
        for season in season_pivot.columns:
            if season in s_colors:
                fig3d.add_trace(go.Bar(
                    name=season, x=cluster_list,
                    y=season_pivot[season].reindex(cluster_list, fill_value=0),
                    marker_color=s_colors[season],
                    marker_line_color='white', marker_line_width=1
                ))
        fig3d.update_layout(
            title='Komposisi Musim per Segmen (%)',
            barmode='stack', height=320, plot_bgcolor='white',
            margin=dict(l=10,r=10,t=40,b=10),
            yaxis=dict(title='Persentase (%)', gridcolor='#f0f0f0'),
            legend=dict(orientation='h', y=1.1, x=0)
        )
        st.plotly_chart(fig3d, use_container_width=True)

    with col3e:
        weather_cl = (cluster_df.groupby(['usage_cluster','weather_label'], observed=True)
                      .size().reset_index(name='count'))
        tot_w = weather_cl.groupby('usage_cluster', observed=True)['count'].transform('sum')
        weather_cl['pct'] = (weather_cl['count'] / tot_w * 100).round(1)
        weather_pivot = weather_cl.pivot_table(
            index='usage_cluster', columns='weather_label', values='pct', observed=True
        ).fillna(0).reindex(cluster_list)

        fig3e = go.Figure()
        w_colors = {'Clear':'#2196F3','Mist':'#90CAF9','Light Snow/Rain':'#E3F2FD'}
        for weather in weather_pivot.columns:
            if weather in w_colors:
                fig3e.add_trace(go.Bar(
                    name=weather, x=cluster_list,
                    y=weather_pivot[weather].reindex(cluster_list, fill_value=0),
                    marker_color=w_colors[weather],
                    marker_line_color='white', marker_line_width=1
                ))
        fig3e.update_layout(
            title='Komposisi Kondisi Cuaca per Segmen (%)',
            barmode='stack', height=320, plot_bgcolor='white',
            margin=dict(l=10,r=10,t=40,b=10),
            yaxis=dict(title='Persentase (%)', gridcolor='#f0f0f0'),
            legend=dict(orientation='h', y=1.1, x=0)
        )
        st.plotly_chart(fig3e, use_container_width=True)

    # ── Tabel Profil Cluster ──
    with st.expander("📋 Lihat Tabel Profil Lengkap per Segmen"):
        display_cp = cp.copy()
        display_cp['Pct_workingday'] = (display_cp['Pct_workingday'] * 100).round(1)
        display_cp.columns = ['Jml Hari','Rata-rata cnt','Rata-rata Casual',
                               'Rata-rata Registered','Suhu Avg','Humidity Avg','% Hari Kerja']
        st.dataframe(display_cp.reindex(cluster_list).style.format('{:.2f}'), use_container_width=True)

    st.markdown(f"""<div class='insight-box'>
    📌 <b>High Usage</b> ({P67:.0f}+ /hari): suhu tinggi, ~82% hari Clear, dominasi Fall/Summer, registered ~86% — hari operasional paling produktif<br>
    📌 <b>Low Usage</b> (≤{P33:.0f} /hari): suhu rendah, hanya ~48% hari Clear, Spring/Winter dominan — perlu strategi insentif & promosi<br>
    📌 <b>Faktor penentu utama:</b> suhu & cuaca (bukan tipe hari), karena proporsi hari kerja merata (~67–73%) di ketiga segmen
    </div>""", unsafe_allow_html=True)

st.markdown("---")

# ============================================================
# FOOTER
# ============================================================
st.markdown("""
<div style='text-align:center; color:#999; font-size:12px; padding:16px 0;'>
    🚲 Bike Sharing Dashboard · Capital Bikeshare Washington D.C. 2011–2012<br>
    Dibuat oleh <b>Najwa Salsabila</b> · Dicoding Data Analysis Submission
</div>
""", unsafe_allow_html=True)
