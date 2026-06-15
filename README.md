# Multi-Outlet Restaurant Profitability Dashboard

**Interactive Streamlit P&L Dashboard | 350+ Outlets | 5 Cities | 6 Months**

Self-service profitability dashboard for cloud kitchen chains — replacing manual Excel reports with real-time, filterable analytics across Kitchen P&L and Food Variance.

---

## Dashboard Preview

```
Tab 1: Kitchen Level PNL          Tab 2: Variance Level PNL
┌─────────────────────────┐       ┌─────────────────────────┐
│ 12 Filters + 3 Sliders  │       │ Variance Category Filter │
│ 5 KPI Cards             │       │                         │
│ Kitchen Snapshot Table  │       │ Sub-dash 1:             │
│ 4 Interactive Charts    │       │ Avg Var% by Revenue Cat │
└─────────────────────────┘       │                         │
                                  │ Sub-dash 2:             │
                                  │ Store Count by Rev Bucket│
                                  └─────────────────────────┘
```

---

## Features

### Dashboard 1 — Kitchen Level PNL

**Filters (12+ dimensions simultaneously)**
- Store, Month, Revenue Cohort, CM Cohort
- EBITDA Category, EBITDA Cohort
- GM%, CM%, Net Revenue, Kitchen EBITDA, Gross Margin (range sliders)

**KPI Cards**
- Kitchen Count | Total Revenue | Gross Margin | Contribution Margin | EBITDA

**Charts**
| Chart | Type | Insight |
|-------|------|---------|
| Monthly Revenue Trend | Line | MoM trajectory |
| EBITDA by City | Color-coded Bar | City profitability ranking |
| Revenue Cohort Split | Pie | Portfolio distribution |
| GM% vs EBITDA% | Bubble Scatter | Efficiency vs profitability |

### Dashboard 2 — Variance Level PNL

- **Sub-dashboard 1:** Avg food variance % by revenue category × month (pivot table + bar chart)
- **Sub-dashboard 2:** Store count by revenue bucket × month (pivot table + heatmap)

---

## KPIs Computed

| Metric | Formula |
|--------|---------|
| GM% | (Gross Margin / Net Revenue) × 100 |
| CM% | ((Gross Margin − Variance) / Net Revenue) × 100 |
| EBITDA% | (Kitchen EBITDA / Net Revenue) × 100 |
| Variance% | (Food Waste / Ideal Food Cost) × 100 |

**Cohorts auto-assigned:**
- Revenue: Below 15L / 15–25L / 25–35L / 35–45L / Above 45L
- EBITDA: Negative / 0–10% / 10–20% / 20%+
- Variance: <2% / 2–3% / 3–5% / >5%

---

## Setup

```bash
pip install streamlit pandas numpy plotly openpyxl

# Place in same folder:
# app.py
# Kittchen_PNL_Data.xlsx

streamlit run app.py
```

Opens at `http://localhost:8501`

---

## Tech Stack

| Layer | Tool |
|-------|------|
| Frontend | Streamlit |
| Charts | Plotly (interactive) |
| Data | Pandas, NumPy |
| Caching | @st.cache_data |
| Source | Excel (.xlsx) |

---

## Data

- **2,100 rows** | 17 raw columns | 8 derived KPI columns
- **5 cities** | **6 months** (Oct 2023 – Mar 2024)
- **350+ unique kitchen outlets**
- Zero nulls in source data

---

## Files

```
├── app.py                    # Main Streamlit dashboard
├── Kittchen_PNL_Data.xlsx   # Source data
└── README.md
```

---

**Domain:** Cloud Kitchen Analytics | **Stack:** Python · Streamlit · Plotly · Pandas
