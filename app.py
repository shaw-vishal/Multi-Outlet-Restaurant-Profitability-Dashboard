import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(
    page_title='Rebel Foods PNL Dashboard',
    layout='wide')
st.image(
    "rebel_logo.png",
    use_container_width=True
)
# Data preperation

@st.cache_data
def load_data():

    df = pd.read_excel("Kittchen_PNL_Data.xlsx", header=1)

    df.columns = (
        df.columns
        .str.strip()
        .str.upper()
        .str.replace(" ", "_"))

    df['STORE'] = df['STORE'].astype(str).str.strip()

    # derived KPIs
    df['CM']     = df['GROSS_MARGIN'] - df['VARIANCE']
    df['CM%']    = (df['CM'] / df['NET_REVENUE']) * 100
    df['GM%']    = (df['GROSS_MARGIN'] / df['NET_REVENUE']) * 100
    df['EBITDA%']= (df['KITCHEN_EBITDA'] / df['NET_REVENUE']) * 100
    df['VAR%']   = (df['VARIANCE'] / df['IDEAL_FOOD_COST']) * 100

    # revenue cohort
    def revenue_cohort(x):
        if x < 1500000:  return '(a) Below INR 15 lacs'
        elif x < 2500000: return '(b) INR 15 to 25 lacs'
        elif x < 3500000: return '(c) INR 25 to 35 lacs'
        elif x < 4500000: return '(d) INR 35 to 45 lacs'
        else:             return '(e) Above INR 45 lacs'

    df['REVENUE_COHORT_FIXED'] = df['NET_REVENUE'].apply(revenue_cohort)

    # ebitda category
    df['EBITDA_CATEGORY_FIXED'] = np.where(
        df['KITCHEN_EBITDA'] >= 0, 'EBITDA +ve', 'EBITDA -ve')

    # ebitda cohort
    def ebitda_cohort(x):
        if   x < 0:  return 'Negative EBITDA'
        elif x < 10: return '0% to 10%'
        elif x < 20: return '10% to 20%'
        else:        return 'More than 20%'

    df['EBITDA_COHORT_FIXED'] = df['EBITDA%'].apply(ebitda_cohort)

    # cm cohort
    def cm_cohort(x):
        if   x < 0: return 'Negative CM'
        elif x < 10: return '0% to 10%'
        elif x < 20: return '10% to 20%'
        elif x < 30: return '20% to 30%'
        else:        return 'More than 30%'

    df['CM_COHORT_FIXED'] = df['CM%'].apply(cm_cohort)

    # variance category
    def variance_bucket(v):
        if  v < 2: return '(a) Var < 2%'
        elif v < 3: return '(b) Var 2% to 3%'
        elif v < 5: return '(c) Var 3% to 5%'
        else:       return '(d) Var > 5%'

    df['VARIANCE_CATEGORY'] = df['VAR%'].apply(variance_bucket)

    # month sort
    month_order = ['Oct-2023','Nov-2023','Dec-2023','Jan-2024','Feb-2024','Mar-2024']
    df['MONTH'] = pd.Categorical(df['MONTH'], categories=month_order, ordered=True)
    df = df.sort_values('MONTH').reset_index(drop=True)

    return df

df = load_data()


# OPENING SCREEN

st.markdown("## Rebel Foods - Kittchen PNL")
st.markdown("---")

tab1, tab2 = st.tabs([
    "Kitchen Level PNL",
    "Variance Level PNL"
])



# DASHBOARD 1


with tab1:

    st.subheader( "Kitchen Level PNL")

    f1, f2, f3, f4 = st.columns(4)

    with f1:
        selected_store = st.multiselect("Store",
            options=sorted(df['STORE'].unique()),
            placeholder="All stores")

    with f2:
        selected_month = st.multiselect("Month",
            options=list(df['MONTH'].cat.categories),
            placeholder="All months")

    with f3:
        selected_revenue_cohort = st.multiselect("Revenue Cohort",
            options=sorted(df['REVENUE_COHORT_FIXED'].unique()),
            placeholder="All cohorts")

    with f4:
        selected_cm_cohort = st.multiselect("CM Cohort",
            options=sorted(df['CM_COHORT_FIXED'].unique()),
            placeholder="All cohorts")

    f5, f6, f7, f8 = st.columns(4)

    with f5:
        selected_ebitda_cat = st.multiselect("EBITDA Category",
            options=sorted(df['EBITDA_CATEGORY_FIXED'].unique()),
            placeholder="All")

    with f6:
        selected_ebitda_cohort = st.multiselect("EBITDA Cohort",
            options=sorted(df['EBITDA_COHORT_FIXED'].unique()),
            placeholder="All")

    with f7:
        gm_range = st.slider("GM%",
            float(df['GM%'].min()), float(df['GM%'].max()),
            (float(df['GM%'].min()), float(df['GM%'].max())))

    with f8:
        cm_pct_range = st.slider("CM%",
            float(df['CM%'].min()), float(df['CM%'].max()),
            (float(df['CM%'].min()), float(df['CM%'].max())))

    f9, f10, f11, f12 = st.columns(4)

    with f9:
        cm_range = st.slider("CM (₹)",
            float(df['CM'].min()), float(df['CM'].max()),
            (float(df['CM'].min()), float(df['CM'].max())))

    with f10:
        rev_range = st.slider("Net Revenue (₹)",
            float(df['NET_REVENUE'].min()), float(df['NET_REVENUE'].max()),
            (float(df['NET_REVENUE'].min()), float(df['NET_REVENUE'].max())))

    with f11:
        ebitda_range = st.slider("Kitchen EBITDA (₹)",
            float(df['KITCHEN_EBITDA'].min()), float(df['KITCHEN_EBITDA'].max()),
            (float(df['KITCHEN_EBITDA'].min()), float(df['KITCHEN_EBITDA'].max())))

    with f12:
        gm_abs_range = st.slider("Gross Margin (₹)",
            float(df['GROSS_MARGIN'].min()), float(df['GROSS_MARGIN'].max()),
            (float(df['GROSS_MARGIN'].min()), float(df['GROSS_MARGIN'].max())))

    #Apply filters
    fdf = df.copy()

    if selected_store:         fdf = fdf[fdf['STORE'].isin(selected_store)]
    if selected_month:         fdf = fdf[fdf['MONTH'].isin(selected_month)]
    if selected_revenue_cohort:fdf = fdf[fdf['REVENUE_COHORT_FIXED'].isin(selected_revenue_cohort)]
    if selected_cm_cohort:     fdf = fdf[fdf['CM_COHORT_FIXED'].isin(selected_cm_cohort)]
    if selected_ebitda_cat:    fdf = fdf[fdf['EBITDA_CATEGORY_FIXED'].isin(selected_ebitda_cat)]
    if selected_ebitda_cohort: fdf = fdf[fdf['EBITDA_COHORT_FIXED'].isin(selected_ebitda_cohort)]

    fdf = fdf[
        (fdf['GM%'].between(*gm_range)) &
        (fdf['CM%'].between(*cm_pct_range)) &
        (fdf['CM'].between(*cm_range)) &
        (fdf['NET_REVENUE'].between(*rev_range)) &
        (fdf['KITCHEN_EBITDA'].between(*ebitda_range)) &
        (fdf['GROSS_MARGIN'].between(*gm_abs_range))]

    st.markdown("---")

    # KPI cards
    k1, k2, k3, k4, k5 = st.columns(5)

    k1.metric("Kitchens", fdf['STORE'].nunique())
    k2.metric("Total Net Revenue", f"₹{fdf['NET_REVENUE'].sum()/1e7:.2f} Cr")
    k3.metric("Total Gross Margin", f"₹{fdf['GROSS_MARGIN'].sum()/1e7:.2f} Cr")
    k4.metric("Total CM", f"₹{fdf['CM'].sum()/1e7:.2f} Cr")
    k5.metric("Total EBITDA", f"₹{fdf['KITCHEN_EBITDA'].sum()/1e7:.2f} Cr")

    st.markdown("---")

    # kitchen snapshot- table
    st.subheader("Kitchen Snapshot")

    display_cols = [
        'STORE', 'MONTH', 'ZONE_MAPPING', 'NET_REVENUE',
        'GM%', 'CM%', 'KITCHEN_EBITDA', 'EBITDA%',
        'GROSS_MARGIN', 'CM', 'VARIANCE',
        'REVENUE_COHORT_FIXED', 'CM_COHORT_FIXED',
        'EBITDA_CATEGORY_FIXED','EBITDA_COHORT_FIXED']

    st.dataframe(fdf[display_cols], use_container_width=True, height=320)

    st.markdown("---")

    # charts — 2 per row
    c1, c2 = st.columns(2)

    with c1:

        st.subheader("Store wise Revenue Trend")

        trajectory_df = (
            fdf.groupby('MONTH', observed=True)['NET_REVENUE']
            .sum()
            .reset_index()
        )

        fig1 = px.line(
            trajectory_df,
            x='MONTH',
            y='NET_REVENUE',
            markers=True,
            labels={
                'NET_REVENUE': 'Net Revenue (₹)',
                'MONTH': ''
            }
        )

        fig1.update_layout(
            plot_bgcolor='white',
            paper_bgcolor='white',
            height=420,
            margin=dict(
                l=20,
                r=20,
                t=40,
                b=20
            )
        )

        st.plotly_chart(
            fig1,
            use_container_width=True
        )

    with c2:
        st.subheader("EBITDA by City")
        city_ebitda = fdf.groupby('CITY')['KITCHEN_EBITDA'].sum().reset_index()
        fig2 = px.bar(city_ebitda, x='CITY', y='KITCHEN_EBITDA',
                      color='KITCHEN_EBITDA',
                      color_continuous_scale=['#E24B4A','#F18F01','#27AE60'],
                      labels={'KITCHEN_EBITDA':'Total EBITDA (₹)','CITY':''})
        fig2.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                           margin=dict(t=10,b=10))
        st.plotly_chart(fig2, use_container_width=True)

    c3, c4 = st.columns(2)

    with c3:
        st.subheader("Revenue Cohort Split")
        cohort_df = fdf['REVENUE_COHORT_FIXED'].value_counts().reset_index()
        cohort_df.columns = ['Cohort','Count']
        fig3 = px.pie(cohort_df, names='Cohort', values='Count',
                      color_discrete_sequence=['#E8722A','#f0a060','#fdd8b0','#2E86AB','#27AE60'])
        fig3.update_layout(paper_bgcolor='white', margin=dict(t=10,b=10))
        st.plotly_chart(fig3, use_container_width=True)

    with c4:
        st.subheader("GM% vs EBITDA% by Store")
        scatter_df = fdf.groupby('STORE', observed=True).agg(
            GM_pct=('GM%','mean'),
            EBITDA_pct=('EBITDA%','mean'),
            Revenue=('NET_REVENUE','sum')
        ).reset_index()
        scatter_df['Revenue'] = scatter_df['Revenue'].clip(lower=0)
        fig4 = px.scatter(scatter_df, x='GM_pct', y='EBITDA_pct',
                          size='Revenue', hover_name='STORE',
                          color='EBITDA_pct',
                          color_continuous_scale=['#E24B4A','#27AE60'],
                          labels={'GM_pct':'Avg GM%','EBITDA_pct':'Avg EBITDA%'})
        fig4.update_layout(plot_bgcolor='white', paper_bgcolor='white',
                           margin=dict(t=10,b=10))
        st.plotly_chart(fig4, use_container_width=True)



# DASHBOARD 2


with tab2:

    st.subheader("Variance Level PNL")
    st.caption("Variance = Food material wastage as % of Ideal Food Cost")

    # variance filter at top - this drives both sub-dashboards
    selected_var_cats = st.multiselect(
        "Variance category ( applies to both sub-dashboards below)",
        options=sorted(df['VARIANCE_CATEGORY'].unique()),
        default=sorted(df['VARIANCE_CATEGORY'].unique()),
        placeholder="Select variance buckets")

    vdf = df[df['VARIANCE_CATEGORY'].isin(selected_var_cats)] if selected_var_cats else df.copy()

   

    # Sub dashboard 1- avg variance % by Revenue Category
    st.subheader("Sub dashboard 1 - Average xariance % by Revenue categtry")
    st.caption("Average variance %of kitchens under each revenue category per month")

    sub1 = vdf.groupby(
        ['REVENUE_COHORT_FIXED','MONTH'], observed=True)['VAR%'].mean().reset_index()

    sub1_pivot = sub1.pivot(index='REVENUE_COHORT_FIXED',columns='MONTH',values='VAR%').round(2)

    sub1_pivot.index.name = 'Revenue Category'
    sub1_pivot.columns.name = None

    # grand total -row
    grand1 = vdf.groupby('MONTH', observed=True)['VAR%'].mean().round(2)
    sub1_pivot.loc['Grand total'] = grand1

    # format as %
    sub1_display = sub1_pivot.copy()
    for col in sub1_display.columns:
        sub1_display[col] = sub1_display[col].apply(
            lambda x: f"{x:.1f}%" if pd.notnull(x) else "-")

    st.dataframe(sub1_display, use_container_width=True)


    # sub dashboard 2- store count by Revenue Bucket/ Month
    st.subheader("Sub-dashboard 2 - Store Count by Revenue Bucket per Month")
    st.caption("Number of kitchen stores in each revenue range per month")

    sub2 = vdf.groupby(['REVENUE_COHORT_FIXED','MONTH'], observed=True)['STORE'].count().reset_index()
    sub2.columns = ['Revenue Category','MONTH','Store Count']

    sub2_pivot = sub2.pivot(
        index='Revenue Category',
        columns='MONTH',
        values='Store Count').fillna(0).astype(int)


    # grand total
    sub2_pivot.loc['Grand total'] = sub2_pivot.sum()

    st.dataframe(sub2_pivot, use_container_width=True)




