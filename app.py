import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import io

# ── Page config ──────────────────────────────────────────────
st.set_page_config(
    page_title="Multi-Outlet Restaurant P&L Dashboard",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS ──────────────────────────────────────────────────────
st.markdown("""
<style>
[data-testid="stAppViewContainer"] { background: #f8f7f5; }
[data-testid="stSidebar"] { background: #1a1a1a; }
[data-testid="stSidebar"] * { color: #e0e0e0 !important; }
[data-testid="stSidebar"] .stSelectbox label,
[data-testid="stSidebar"] .stMultiSelect label,
[data-testid="stSidebar"] .stSlider label { color: #aaa !important; font-size:11px !important; font-weight:600 !important; letter-spacing:0.06em !important; text-transform:uppercase !important; }
.kpi-card { background:white; border-radius:8px; padding:16px 20px; border-left:4px solid #e07030; box-shadow:0 1px 6px rgba(0,0,0,0.06); }
.kpi-label { font-size:10px; font-weight:700; letter-spacing:0.12em; text-transform:uppercase; color:#999; margin-bottom:4px; }
.kpi-value { font-size:22px; font-weight:700; color:#1a1a1a; line-height:1.2; }
.kpi-sub { font-size:11px; color:#888; margin-top:3px; }
.kpi-good { color:#27ae60 !important; }
.kpi-bad  { color:#e74c3c !important; }
.section-title { font-size:13px; font-weight:700; color:#1a1a1a; margin:0 0 8px 0; letter-spacing:0.02em; }
div[data-testid="stTabs"] button { font-size:13px !important; font-weight:600 !important; }
</style>
""", unsafe_allow_html=True)

MONTH_ORDER = ['Oct-2023','Nov-2023','Dec-2023','Jan-2024','Feb-2024','Mar-2024']
CITY_COLORS = {'Ahmedabad':'#e07030','Pune':'#3498db','Bangalore':'#27ae60',
               'Mumbai':'#9b59b6','Hyderabad':'#f39c12'}

# ── Data loading ─────────────────────────────────────────────
@st.cache_data
def load_data(file_bytes):
    df = pd.read_excel(io.BytesIO(file_bytes), header=1)
    df.columns = df.columns.str.strip()
    # Derived KPIs
    df['GM_PCT']     = (df['GROSS MARGIN']    / df['NET REVENUE'] * 100).round(2)
    df['CM']         = df['GROSS MARGIN'] - df['VARIANCE']
    df['CM_PCT']     = (df['CM']              / df['NET REVENUE'] * 100).round(2)
    df['EBITDA_PCT'] = (df['KITCHEN EBITDA']  / df['NET REVENUE'] * 100).round(2)
    df['VAR_PCT']    = (df['VARIANCE']        / df['IDEAL FOOD COST'] * 100).round(2)
    df['MONTH_ORD']  = pd.Categorical(df['MONTH'], categories=MONTH_ORDER, ordered=True)
    return df

# ── Try loading from disk first (local / after upload to repo)
try:
    with open('Kittchen_PNL_Data.xlsx','rb') as f:
        raw = f.read()
    df_raw = load_data(raw)
    data_source = "local"
except FileNotFoundError:
    data_source = "upload"
    df_raw = None

# ── Header ───────────────────────────────────────────────────
st.markdown("## 🍽️ Multi-Outlet Restaurant Profitability Dashboard")
st.markdown("**Cloud Kitchen P&L Analytics** · 344 kitchens · 5 cities · 6 months (Oct 2023 – Mar 2024)")

if data_source == "upload" or df_raw is None:
    st.markdown("---")
    uploaded = st.file_uploader(
        "Upload `Kittchen_PNL_Data.xlsx` to load the dashboard",
        type=["xlsx"],
        help="Upload the kitchen P&L Excel file to begin"
    )
    if uploaded is None:
        st.info("👆 Upload the Excel file above to load all charts and KPIs.")
        st.stop()
    df_raw = load_data(uploaded.read())

st.markdown("---")

# ── SIDEBAR FILTERS ──────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🔍 Filters")

    cities = st.multiselect("City", sorted(df_raw['CITY'].unique()),
                            default=sorted(df_raw['CITY'].unique()))
    months = st.multiselect("Month", MONTH_ORDER,
                            default=MONTH_ORDER)
    status = st.multiselect("Store Status", df_raw['STATUS'].unique().tolist(),
                            default=df_raw['STATUS'].unique().tolist())
    zones  = st.multiselect("Zone", sorted(df_raw['ZONE MAPPING'].unique()),
                            default=sorted(df_raw['ZONE MAPPING'].unique()))

    st.markdown("---")
    st.markdown("### 📊 Cohort Filters")
    rev_cohorts  = st.multiselect("Revenue Cohort",  df_raw['REVENUE COHORT'].unique().tolist(),
                                  default=df_raw['REVENUE COHORT'].unique().tolist())
    ebitda_cats  = st.multiselect("EBITDA Category", df_raw['EBITDA CATEGORY'].unique().tolist(),
                                  default=df_raw['EBITDA CATEGORY'].unique().tolist())
    ebitda_cohs  = st.multiselect("EBITDA Cohort",   df_raw['EBITDA COHORT'].unique().tolist(),
                                  default=df_raw['EBITDA COHORT'].unique().tolist())

    st.markdown("---")
    st.markdown("### 🎚️ KPI Range Filters")
    gm_range  = st.slider("GM % Range",   0, 100, (0, 100))
    cm_range  = st.slider("CM % Range",   -50, 100, (-50, 100))
    ebitda_range = st.slider("EBITDA % Range", -50, 50, (-50, 50))

# ── Apply filters ─────────────────────────────────────────────
df = df_raw[
    df_raw['CITY'].isin(cities) &
    df_raw['MONTH'].isin(months) &
    df_raw['STATUS'].isin(status) &
    df_raw['ZONE MAPPING'].isin(zones) &
    df_raw['REVENUE COHORT'].isin(rev_cohorts) &
    df_raw['EBITDA CATEGORY'].isin(ebitda_cats) &
    df_raw['EBITDA COHORT'].isin(ebitda_cohs) &
    df_raw['GM_PCT'].between(*gm_range) &
    df_raw['CM_PCT'].between(*cm_range) &
    df_raw['EBITDA_PCT'].between(*ebitda_range)
].copy()

if df.empty:
    st.warning("No data matches your filters. Adjust the sidebar.")
    st.stop()

# ── TABS ─────────────────────────────────────────────────────
tab1, tab2 = st.tabs(["📊 Kitchen Level P&L", "📉 Variance Level P&L"])

# ════════════════════════════════════════════════════════════
# TAB 1 — Kitchen Level P&L
# ════════════════════════════════════════════════════════════
with tab1:

    # KPI Cards
    total_stores  = df['STORE'].nunique()
    total_rev     = df['NET REVENUE'].sum()
    total_gm      = df['GROSS MARGIN'].sum()
    total_cm      = df['CM'].sum()
    total_ebitda  = df['KITCHEN EBITDA'].sum()
    avg_gm_pct    = (total_gm / total_rev * 100)
    avg_cm_pct    = (total_cm / total_rev * 100)
    avg_ebitda_pct= (total_ebitda / total_rev * 100)

    c1,c2,c3,c4,c5 = st.columns(5)

    def kcard(col, label, value, sub, good=None):
        sub_cls = ("kpi-good" if good is True else "kpi-bad" if good is False else "")
        col.markdown(f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub {sub_cls}">{sub}</div>
        </div>""", unsafe_allow_html=True)

    kcard(c1, "Kitchen Count",    f"{total_stores}",
          f"of 344 total stores")
    kcard(c2, "Total Net Revenue", f"₹{total_rev/1e7:.2f} Cr",
          f"₹{total_rev/1e5:.0f}L across selection")
    kcard(c3, "Gross Margin",     f"₹{total_gm/1e7:.2f} Cr",
          f"{avg_gm_pct:.1f}% GM%", good=(avg_gm_pct >= 55))
    kcard(c4, "Contribution Margin", f"₹{total_cm/1e7:.2f} Cr",
          f"{avg_cm_pct:.1f}% CM%", good=(avg_cm_pct >= 50))
    kcard(c5, "Kitchen EBITDA",   f"₹{total_ebitda/1e7:.2f} Cr",
          f"{avg_ebitda_pct:.1f}% EBITDA%", good=(avg_ebitda_pct > 0))

    st.markdown("---")

    # Row 1: Monthly Revenue Trend + EBITDA by City
    col1, col2 = st.columns([2,1])

    with col1:
        st.markdown('<p class="section-title">Monthly Revenue & EBITDA% Trend</p>', unsafe_allow_html=True)
        monthly = (df.groupby('MONTH_ORD', observed=True)
                     .agg(NET_REV=('NET REVENUE','sum'),
                          EBITDA=('KITCHEN EBITDA','sum'),
                          GM=('GROSS MARGIN','sum'))
                     .reset_index()
                     .sort_values('MONTH_ORD'))
        monthly['EBITDA_PCT'] = (monthly['EBITDA'] / monthly['NET_REV'] * 100).round(1)
        monthly['MONTH_LBL'] = monthly['MONTH_ORD'].astype(str)

        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(go.Bar(x=monthly['MONTH_LBL'], y=monthly['NET_REV']/1e5,
                             name='Net Revenue (₹L)', marker_color='#e07030', opacity=0.85),
                      secondary_y=False)
        fig.add_trace(go.Scatter(x=monthly['MONTH_LBL'], y=monthly['EBITDA_PCT'],
                                 name='EBITDA %', mode='lines+markers',
                                 line=dict(color='#27ae60', width=2.5),
                                 marker=dict(size=8, symbol='circle')),
                      secondary_y=True)
        fig.add_hline(y=0, secondary_y=True, line=dict(color='red', dash='dot', width=1))
        fig.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                          legend=dict(orientation='h', y=1.12),
                          plot_bgcolor='white', paper_bgcolor='white', font=dict(size=11))
        fig.update_yaxes(title_text="Net Revenue (₹ Lakhs)", secondary_y=False, gridcolor='#f0f0f0')
        fig.update_yaxes(title_text="EBITDA %", secondary_y=True, gridcolor='#f0f0f0')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.markdown('<p class="section-title">EBITDA% by City</p>', unsafe_allow_html=True)
        city_agg = (df.groupby('CITY')
                      .agg(REV=('NET REVENUE','sum'), EBITDA=('KITCHEN EBITDA','sum'))
                      .reset_index())
        city_agg['EBITDA_PCT'] = (city_agg['EBITDA'] / city_agg['REV'] * 100).round(1)
        city_agg = city_agg.sort_values('EBITDA_PCT')
        city_agg['COLOR'] = city_agg['EBITDA_PCT'].apply(lambda x: '#27ae60' if x >= 0 else '#e74c3c')

        fig2 = go.Figure(go.Bar(
            y=city_agg['CITY'], x=city_agg['EBITDA_PCT'],
            orientation='h', marker_color=city_agg['COLOR'],
            text=city_agg['EBITDA_PCT'].apply(lambda x: f"{x:+.1f}%"),
            textposition='outside'
        ))
        fig2.add_vline(x=0, line=dict(color='#333', width=1))
        fig2.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                           plot_bgcolor='white', paper_bgcolor='white',
                           xaxis_title='EBITDA %', font=dict(size=11))
        fig2.update_yaxes(title='')
        st.plotly_chart(fig2, use_container_width=True)

    # Row 2: Revenue Cohort Pie + GM% vs EBITDA% Scatter
    col3, col4 = st.columns([1,2])

    with col3:
        st.markdown('<p class="section-title">Revenue Cohort Distribution</p>', unsafe_allow_html=True)
        coh = df.groupby('REVENUE COHORT')['NET REVENUE'].sum().reset_index()
        fig3 = px.pie(coh, names='REVENUE COHORT', values='NET REVENUE',
                      color_discrete_sequence=['#e07030','#f39c12','#27ae60'],
                      hole=0.4)
        fig3.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                           legend=dict(orientation='v', font=dict(size=10)),
                           paper_bgcolor='white', font=dict(size=11))
        fig3.update_traces(textposition='inside', textinfo='percent+label', textfont_size=10)
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        st.markdown('<p class="section-title">GM% vs EBITDA% by Store (Bubble = Net Revenue)</p>', unsafe_allow_html=True)
        scatter = (df.groupby(['STORE','CITY'])
                     .agg(GM_PCT=('GM_PCT','mean'),
                          EBITDA_PCT=('EBITDA_PCT','mean'),
                          NET_REV=('NET REVENUE','sum'))
                     .reset_index())
        fig4 = px.scatter(scatter, x='GM_PCT', y='EBITDA_PCT',
                          size='NET_REV', color='CITY',
                          color_discrete_map=CITY_COLORS,
                          size_max=25, opacity=0.7,
                          hover_data={'STORE': True, 'NET_REV': ':,.0f',
                                      'GM_PCT': ':.1f', 'EBITDA_PCT': ':.1f'})
        fig4.add_hline(y=0, line=dict(color='red', dash='dot', width=1.5))
        fig4.add_vline(x=55, line=dict(color='orange', dash='dot', width=1.5))
        fig4.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                           plot_bgcolor='white', paper_bgcolor='white',
                           xaxis_title='Gross Margin %', yaxis_title='EBITDA %',
                           font=dict(size=11))
        st.plotly_chart(fig4, use_container_width=True)

    # Kitchen Snapshot Table
    st.markdown("---")
    st.markdown('<p class="section-title">Kitchen Snapshot Table</p>', unsafe_allow_html=True)

    snap = (df.groupby(['CITY','STORE','STATUS'])
              .agg(MONTHS=('MONTH','count'),
                   NET_REV=('NET REVENUE','sum'),
                   GM=('GROSS MARGIN','sum'),
                   EBITDA=('KITCHEN EBITDA','sum'),
                   ORDERS=('ORDER COUNT','sum'))
              .reset_index())
    snap['GM_PCT']     = (snap['GM'] / snap['NET_REV'] * 100).round(1)
    snap['EBITDA_PCT'] = (snap['EBITDA'] / snap['NET_REV'] * 100).round(1)
    snap['REV_L']      = (snap['NET_REV'] / 1e5).round(2)
    snap['EBITDA_L']   = (snap['EBITDA'] / 1e5).round(2)
    snap = snap.sort_values('NET_REV', ascending=False)

    disp = snap[['CITY','STORE','STATUS','MONTHS','REV_L','GM_PCT','EBITDA_L','EBITDA_PCT','ORDERS']].rename(columns={
        'REV_L':'Rev (₹L)', 'GM_PCT':'GM%', 'EBITDA_L':'EBITDA (₹L)', 'EBITDA_PCT':'EBITDA%', 'ORDERS':'Orders'
    })

    # Format numeric columns before display
    disp_fmt = disp.copy()
    disp_fmt['Rev (₹L)']     = disp_fmt['Rev (₹L)'].map('{:.2f}'.format)
    disp_fmt['GM%']           = disp_fmt['GM%'].map('{:.1f}'.format)
    disp_fmt['EBITDA (₹L)']  = disp_fmt['EBITDA (₹L)'].map('{:.2f}'.format)
    disp_fmt['EBITDA%']       = disp_fmt['EBITDA%'].map('{:.1f}'.format)
    disp_fmt['Orders']        = disp_fmt['Orders'].map('{:,}'.format)
    st.dataframe(disp_fmt, use_container_width=True, height=400)


# ════════════════════════════════════════════════════════════
# TAB 2 — Variance Level P&L
# ════════════════════════════════════════════════════════════
with tab2:

    st.markdown("### Food Variance Analysis")
    st.markdown("Food variance = actual food cost vs ideal food cost. Positive variance means over-spending.")

    # Sub-dashboard 1: Avg Variance% by Revenue Cohort × Month
    st.markdown("---")
    st.markdown('<p class="section-title">Sub-Dashboard 1 — Avg Food Variance % by Revenue Category × Month</p>',
                unsafe_allow_html=True)

    var_pivot = (df.groupby(['REVENUE COHORT','MONTH_ORD'], observed=True)['VAR_PCT']
                   .mean().round(2).reset_index()
                   .sort_values('MONTH_ORD'))
    var_pivot['MONTH_LBL'] = var_pivot['MONTH_ORD'].astype(str)

    pivot_tbl = var_pivot.pivot(index='REVENUE COHORT', columns='MONTH_LBL', values='VAR_PCT')
    pivot_tbl = pivot_tbl[[m for m in MONTH_ORDER if m in pivot_tbl.columns]]

    col_a, col_b = st.columns([1, 2])

    with col_a:
        st.markdown("**Pivot Table — Avg Variance %**")
        pivot_fmt = pivot_tbl.copy()
        for col in pivot_fmt.columns:
            pivot_fmt[col] = pivot_fmt[col].map('{:.2f}%'.format)
        st.dataframe(pivot_fmt, use_container_width=True)

    with col_b:
        fig5 = px.bar(var_pivot, x='MONTH_LBL', y='VAR_PCT',
                      color='REVENUE COHORT', barmode='group',
                      color_discrete_sequence=['#e07030','#3498db','#27ae60'],
                      labels={'VAR_PCT': 'Avg Variance %', 'MONTH_LBL': 'Month',
                              'REVENUE COHORT': 'Revenue Category'})
        fig5.add_hline(y=3, line=dict(color='red', dash='dot', width=1.5),
                       annotation_text="3% Alert Threshold")
        fig5.update_layout(height=300, margin=dict(l=0,r=0,t=10,b=0),
                           plot_bgcolor='white', paper_bgcolor='white',
                           legend=dict(orientation='h', y=1.12), font=dict(size=11))
        st.plotly_chart(fig5, use_container_width=True)

    # Sub-dashboard 2: Store Count by Revenue Bucket × Month
    st.markdown("---")
    st.markdown('<p class="section-title">Sub-Dashboard 2 — Store Count by Revenue Bucket × Month</p>',
                unsafe_allow_html=True)

    count_pivot = (df.groupby(['REVENUE COHORT','MONTH_ORD'], observed=True)['STORE']
                     .nunique().reset_index()
                     .sort_values('MONTH_ORD'))
    count_pivot['MONTH_LBL'] = count_pivot['MONTH_ORD'].astype(str)
    count_tbl = count_pivot.pivot(index='REVENUE COHORT', columns='MONTH_LBL', values='STORE')
    count_tbl = count_tbl[[m for m in MONTH_ORDER if m in count_tbl.columns]]

    col_c, col_d = st.columns([1, 2])

    with col_c:
        st.markdown("**Pivot Table — Store Count**")
        count_fmt = count_tbl.fillna(0).astype(int)
        st.dataframe(count_fmt, use_container_width=True)

    with col_d:
        # Heatmap
        heat_df = count_tbl.reset_index().melt(id_vars='REVENUE COHORT',
                                                var_name='Month', value_name='Store Count')
        fig6 = px.density_heatmap(heat_df, x='Month', y='REVENUE COHORT',
                                   z='Store Count', color_continuous_scale='Blues',
                                   text_auto=True)
        fig6.update_layout(height=280, margin=dict(l=0,r=0,t=10,b=0),
                           plot_bgcolor='white', paper_bgcolor='white',
                           font=dict(size=11), xaxis_title='', yaxis_title='')
        st.plotly_chart(fig6, use_container_width=True)

    # Variance flag summary
    st.markdown("---")
    st.markdown('<p class="section-title">Variance Flag Summary — Stores Above 3% Threshold</p>',
                unsafe_allow_html=True)
    flagged = df[df['VAR_PCT'] > 3].groupby(['CITY','STORE']).agg(
        Avg_Var_Pct=('VAR_PCT','mean'),
        Months_Flagged=('MONTH','count'),
        Total_Variance=('VARIANCE','sum')
    ).reset_index().sort_values('Avg_Var_Pct', ascending=False)
    flagged['Avg_Var_Pct'] = flagged['Avg_Var_Pct'].round(2)
    flagged['Total_Variance'] = (flagged['Total_Variance']/1e5).round(2)
    flagged.columns = ['City','Store','Avg Var %','Months Flagged','Total Variance (₹L)']
    st.dataframe(flagged, use_container_width=True, height=350)

# ── Footer ────────────────────────────────────────────────────
st.markdown("---")
st.caption("Built by **Vishal Shaw** · Multi-Outlet Restaurant Profitability Dashboard · Streamlit + Plotly + Pandas · [GitHub](https://github.com/shaw-vishal/Multi-Outlet-Restaurant-Profitability-Dashboard)")
