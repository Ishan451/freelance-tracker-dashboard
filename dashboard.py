# import streamlit as st
# import pandas as pd
# import plotly.express as px
# import plotly.graph_objects as go
# import re

# # --- Configuration ---
# st.set_page_config(page_title="Earnings & Time Dashboard", layout="wide")

# # --- Helper Functions ---

# def parse_duration(duration_str):
#     """
#     Parses strings like '1h 40m 0s', '40m', '1m 43s' into total hours (float).
#     """
#     if pd.isna(duration_str) or str(duration_str).strip() in ["-", ""]:
#         return 0.0
    
#     hours = 0
#     minutes = 0
#     seconds = 0
    
#     # Regex to capture hours, minutes, seconds
#     h_match = re.search(r'(\d+)h', str(duration_str))
#     m_match = re.search(r'(\d+)m', str(duration_str))
#     s_match = re.search(r'(\d+)s', str(duration_str))
    
#     if h_match: hours = int(h_match.group(1))
#     if m_match: minutes = int(m_match.group(1))
#     if s_match: seconds = int(s_match.group(1))
    
#     return hours + (minutes / 60) + (seconds / 3600)

# def format_hours(hours_float):
#     """
#     Converts a float (e.g., 1.5) to a string (e.g., '1h 30m').
#     """
#     if pd.isna(hours_float):
#         return "0h 0m"
#     hours = int(hours_float)
#     minutes = int((hours_float - hours) * 60)
#     return f"{hours}h {minutes}m"

# def load_data(file):
#     name = getattr(file, "name", "").lower()
#     if name.endswith((".xlsx", ".xls")):
#         df = pd.read_excel(file)
#     else:
#         df = pd.read_csv(file)

#     # 1. Clean 'Payable'
#     df['Payable'] = df['Payable'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
#     df['Payable'] = pd.to_numeric(df['Payable'], errors='coerce').fillna(0.0)

#     # 2. Clean 'Rate'
#     df['Rate_Clean'] = df['Rate'].astype(str).str.replace('$', '', regex=False).str.replace('/hr', '', regex=False).str.replace(',', '', regex=False)
#     df['Rate_Clean'] = pd.to_numeric(df['Rate_Clean'], errors='coerce').fillna(0)

#     # 3. Parse 'Duration' to Hours
#     df['Hours'] = df['Duration'].apply(parse_duration)

#     # 4. Convert 'Work Date' to datetime
#     df['Work Date'] = pd.to_datetime(df['Work Date'])
    
#     # 5. Extract additional time features
#     df['Month'] = df['Work Date'].dt.strftime('%Y-%m')
#     df['Day'] = df['Work Date'].dt.date
    
#     return df

# # --- Main Dashboard ---

# st.title("Freelance Earnings & Time Tracking")

# # File Uploader
# uploaded_file = st.file_uploader("Upload your earnings file (CSV or Excel)", type=['csv', 'xlsx', 'xls'])

# if uploaded_file is not None:
#     try:
#         df = load_data(uploaded_file)
        
#         # --- Sidebar Filters ---
#         st.sidebar.header("Filters")
        
#         # Date Range Filter
#         min_date = df['Work Date'].min().date()
#         max_date = df['Work Date'].max().date()
#         start_date, end_date = st.sidebar.date_input(
#             "Select Date Range",
#             value=[min_date, max_date],
#             min_value=min_date,
#             max_value=max_date
#         )
        
#         # Project Filter
#         projects = ['All'] + sorted(df['Project Name'].dropna().unique().tolist())
#         selected_project = st.sidebar.selectbox("Select Project", projects)
        
#         # Apply Filters
#         mask = (df['Work Date'].dt.date >= start_date) & (df['Work Date'].dt.date <= end_date)
#         if selected_project != 'All':
#             mask = mask & (df['Project Name'] == selected_project)
            
#         filtered_df = df.loc[mask]

#         # --- Top Level Metrics ---
        
#         total_earnings = filtered_df['Payable'].sum()
#         total_hours = filtered_df['Hours'].sum()
#         total_days_worked = filtered_df['Work Date'].nunique()
        
#         # Weighted Average Hourly Rate
#         avg_hourly_rate = total_earnings / total_hours if total_hours > 0 else 0

#         c1, c2, c3, c4 = st.columns(4)
#         with c1: st.metric("Total Earnings", f"${total_earnings:,.2f}")
#         with c2: st.metric("Total Hours", format_hours(total_hours))
#         with c3: st.metric("Work Days", f"{total_days_worked}")
#         with c4: st.metric("Avg Hourly Rate", f"${avg_hourly_rate:,.2f}/hr")

#         st.markdown("---")

#         # --- Charts Row 1: Trends ---
        
#         c_chart1, c_chart2 = st.columns(2)
        
#         # 1. Daily Earnings Chart
#         with c_chart1:
#             st.subheader("Daily Earnings Trend")
#             daily_stats = filtered_df.groupby('Day')[['Payable', 'Hours']].sum().reset_index()
            
#             fig_daily = px.bar(
#                 daily_stats, 
#                 x='Day', 
#                 y='Payable',
#                 title="Earnings per Day",
#                 labels={'Payable': 'Earnings', 'Day': 'Date'},
#                 color_discrete_sequence=['#00CC96'],
#                 text_auto='.0f' # Display rounded numbers on bars
#             )
#             # Add $ symbol to text and format tooltips
#             fig_daily.update_traces(
#                 texttemplate='$%{y:.2f}', 
#                 textposition='outside',
#                 hovertemplate='<b>Date:</b> %{x}<br><b>Earnings:</b> $%{y:.2f}<extra></extra>'
#             )
#             fig_daily.update_layout(yaxis_title=None, xaxis_title=None)
#             st.plotly_chart(fig_daily, use_container_width=True)
            
#         # 2. Daily Hours Chart (Formatted Time)
#         with c_chart2:
#             st.subheader("Daily Hours Worked")
#             # Create a formatted string column for display
#             daily_stats['Time_Label'] = daily_stats['Hours'].apply(format_hours)
            
#             fig_hours = px.bar(
#                 daily_stats,
#                 x='Day',
#                 y='Hours',
#                 title="Hours Worked per Day",
#                 labels={'Hours': 'Hours', 'Day': 'Date'},
#                 color_discrete_sequence=['#636EFA'],
#                 custom_data=['Time_Label'] # Pass formatted time to chart
#             )
#             # Use the formatted string for the text label on the bar
#             fig_hours.update_traces(
#                 text=daily_stats['Time_Label'],
#                 textposition='outside',
#                 hovertemplate='<b>Date:</b> %{x}<br><b>Time:</b> %{customdata[0]}<extra></extra>'
#             )
#             fig_hours.update_layout(yaxis_title=None, xaxis_title=None)
#             st.plotly_chart(fig_hours, use_container_width=True)

#         # --- Charts Row 2: Distribution ---
        
#         c_chart3, c_chart4 = st.columns(2)
        
#         # 3. Project Pie Chart
#         with c_chart3:
#             st.subheader("Earnings by Project")
#             project_earnings = filtered_df.groupby('Project Name')['Payable'].sum().reset_index()
            
#             fig_pie = px.pie(
#                 project_earnings, 
#                 values='Payable', 
#                 names='Project Name',
#                 hole=0.4,
#                 title="Project Earnings Share",
#                 color_discrete_sequence=px.colors.qualitative.Pastel
#             )
#             fig_pie.update_traces(textposition='inside', textinfo='percent+label')
#             st.plotly_chart(fig_pie, use_container_width=True)
            
#         # 4. Task Type Chart
#         with c_chart4:
#             st.subheader("Task Type Distribution")
#             type_counts = filtered_df.groupby('Type')['Payable'].sum().reset_index()
            
#             fig_type = px.bar(
#                 type_counts, 
#                 x='Type', 
#                 y='Payable', 
#                 title="Earnings by Task Type",
#                 text='Payable',
#                 color='Type',
#                 color_discrete_sequence=px.colors.qualitative.Bold
#             )
#             fig_type.update_traces(texttemplate='$%{y:.2f}', textposition='outside')
#             fig_type.update_layout(showlegend=False, yaxis_title=None, xaxis_title=None)
#             st.plotly_chart(fig_type, use_container_width=True)

#         # --- Charts Row 3: Project Performance ---
        
#         st.subheader("Project Performance Details")
#         proj_stats = filtered_df.groupby('Project Name').agg({
#             'Payable': 'sum',
#             'Hours': 'sum',
#             'Work Date': 'nunique'
#         }).reset_index()
        
#         proj_stats['Effective Rate'] = proj_stats['Payable'] / proj_stats['Hours']
#         proj_stats['Time_Label'] = proj_stats['Hours'].apply(format_hours)
        
#         fig_scatter = px.scatter(
#             proj_stats,
#             x='Hours',
#             y='Payable',
#             size='Payable',
#             color='Project Name',
#             title="Earnings vs. Hours by Project",
#             hover_name='Project Name',
#             custom_data=['Time_Label', 'Effective Rate']
#         )
        
#         fig_scatter.update_traces(
#             hovertemplate='<b>%{hovertext}</b><br>' +
#                           'Earnings: $%{y:.2f}<br>' +
#                           'Time: %{customdata[0]}<br>' +
#                           'Rate: $%{customdata[1]:.2f}/hr<extra></extra>'
#         )
#         st.plotly_chart(fig_scatter, use_container_width=True)
        
#         # Display Data Table
#         with st.expander("View Raw Data"):
#             st.dataframe(filtered_df.sort_values(by='Work Date', ascending=False))
            
#     except Exception as e:
#         st.error(f"Error processing file: {e}")
# else:
#     st.info("Please upload your earnings CSV or Excel file to generate the dashboard.")


import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import re

# --- Configuration ---
st.set_page_config(page_title="Earnings & Time Dashboard", layout="wide")

PLOTLY_TEMPLATE = "plotly_dark"
COLOR_EARNINGS = "#00CC96"
COLOR_HOURS = "#636EFA"
COLOR_ACCENT = "#FFA15A"
COLOR_WARN = "#EF553B"
DOW_ORDER = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']

# --- Custom Styling ---
st.markdown(
    """
    <style>
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(0,204,150,0.10) 0%, rgba(99,110,250,0.10) 100%);
        border: 1px solid rgba(255,255,255,0.06);
        border-radius: 14px;
        padding: 14px 18px;
        box-shadow: 0 2px 14px rgba(0,0,0,0.25);
    }
    div[data-testid="stMetric"] label {
        color: rgba(255,255,255,0.65) !important;
        font-size: 0.78rem !important;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.55rem !important;
        font-weight: 700 !important;
    }
    .filter-chip {
        display: inline-block;
        background: rgba(99,110,250,0.18);
        border: 1px solid rgba(99,110,250,0.45);
        color: #c8cdff;
        padding: 3px 10px;
        margin: 0 6px 6px 0;
        border-radius: 999px;
        font-size: 0.78rem;
    }
    .insight-card {
        background: rgba(255,255,255,0.03);
        border: 1px solid rgba(255,255,255,0.07);
        border-radius: 12px;
        padding: 14px 18px;
        margin-bottom: 10px;
    }
    .insight-card .label {
        color: rgba(255,255,255,0.55);
        font-size: 0.75rem;
        letter-spacing: 0.05em;
        text-transform: uppercase;
        margin-bottom: 4px;
    }
    .insight-card .value {
        font-size: 1.05rem;
        color: #ffffff;
    }
    .stTabs [data-baseweb="tab-list"] button {
        font-weight: 600;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# --- Helper Functions ---

def parse_duration(duration_str):
    if pd.isna(duration_str) or str(duration_str).strip() in ["-", ""]:
        return 0.0
    s = str(duration_str)
    hours = minutes = seconds = 0
    h_match = re.search(r'(\d+)h', s)
    m_match = re.search(r'(\d+)m', s)
    s_match = re.search(r'(\d+)s', s)
    if h_match: hours = int(h_match.group(1))
    if m_match: minutes = int(m_match.group(1))
    if s_match: seconds = int(s_match.group(1))
    return hours + minutes / 60 + seconds / 3600

def format_hours(hours_float):
    if pd.isna(hours_float) or hours_float == 0:
        return "0h 0m"
    hours = int(hours_float)
    minutes = int(round((hours_float - hours) * 60))
    return f"{hours}h {minutes}m"

def load_data(file):
    name = getattr(file, "name", "").lower()
    if name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)

    df['Payable'] = df['Payable'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    df['Payable'] = pd.to_numeric(df['Payable'], errors='coerce').fillna(0.0)

    rate_str = df['Rate'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    rate_str = rate_str.str.replace('/hr', '', regex=False).str.replace('/task', '', regex=False)
    df['Rate_Clean'] = pd.to_numeric(rate_str, errors='coerce').fillna(0)

    df['Hours'] = df['Duration'].apply(parse_duration)
    df['Work Date'] = pd.to_datetime(df['Work Date'])
    df['Day'] = df['Work Date'].dt.date
    df['Month'] = df['Work Date'].dt.strftime('%Y-%m')
    df['Week'] = df['Work Date'].dt.to_period('W-SUN').apply(lambda p: p.start_time.date())
    df['DayOfWeek'] = df['Work Date'].dt.day_name()
    return df

# --- Main Dashboard ---

st.title("Freelance Earnings & Time Tracking")
st.caption("Upload your tracker export to explore earnings, time, and project performance.")

uploaded_file = st.file_uploader("Upload your earnings file (CSV or Excel)", type=['csv', 'xlsx', 'xls'])

if uploaded_file is None:
    st.info("Please upload your earnings CSV or Excel file to generate the dashboard.")
    st.stop()

try:
    df = load_data(uploaded_file)
except Exception as e:
    st.error(f"Error processing file: {e}")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("Filters")

min_date = df['Work Date'].min().date()
max_date = df['Work Date'].max().date()
date_sel = st.sidebar.date_input(
    "Date Range",
    value=[min_date, max_date],
    min_value=pd.Timestamp("2025-01-01").date(),
    max_value=pd.Timestamp("2100-12-31").date(),
)
if isinstance(date_sel, (list, tuple)) and len(date_sel) == 2:
    start_date, end_date = date_sel
else:
    only = date_sel[0] if isinstance(date_sel, (list, tuple)) else date_sel
    start_date = end_date = only

if start_date > end_date:
    st.sidebar.error("Start date is after end date.")
    st.stop()
if end_date < min_date or start_date > max_date:
    st.sidebar.error(
        f"Selected range is outside the available data ({min_date} → {max_date})."
    )
    st.stop()
if start_date < min_date or end_date > max_date:
    st.sidebar.warning(
        f"Range extends beyond available data ({min_date} → {max_date}); "
        "showing available rows only."
    )

projects = ['All'] + sorted(df['Project Name'].dropna().astype(str).unique().tolist())

if 'isolate_project' not in st.session_state:
    st.session_state.isolate_project = None

sidebar_project = st.sidebar.selectbox("Project", projects, key='sidebar_project')

types_avail = sorted(df['Type'].dropna().astype(str).unique().tolist())
selected_types = st.sidebar.multiselect("Type", types_avail, default=types_avail)

selected_status = None
if 'Status' in df.columns:
    status_avail = sorted(df['Status'].dropna().astype(str).unique().tolist())
    selected_status = st.sidebar.multiselect("Status", status_avail, default=status_avail)

st.sidebar.divider()
st.sidebar.subheader("Goal")
monthly_goal = st.sidebar.number_input(
    "Monthly earnings goal ($)",
    min_value=0.0, max_value=100000.0, value=2000.0, step=100.0,
    help="Used in the 'This month vs goal' card under Insights.",
)

# A click on a chart can override the sidebar selection.
effective_project = (
    st.session_state.isolate_project
    if st.session_state.isolate_project and st.session_state.isolate_project in projects
    else sidebar_project
)

if st.session_state.isolate_project:
    iso_l, iso_r = st.columns([6, 1])
    iso_l.info(f"Isolated to **{st.session_state.isolate_project}** (clicked from a chart)")
    if iso_r.button("Clear isolate", use_container_width=True):
        st.session_state.isolate_project = None
        st.rerun()

mask = (df['Work Date'].dt.date >= start_date) & (df['Work Date'].dt.date <= end_date)
if effective_project != 'All':
    mask &= (df['Project Name'] == effective_project)
if selected_types:
    mask &= df['Type'].isin(selected_types)
if selected_status:
    mask &= df['Status'].isin(selected_status)

filtered_df = df.loc[mask]

if filtered_df.empty:
    st.warning("No records match the current filters.")
    st.stop()

# --- Filter chip bar ---
chip_html_parts = [f'<span class="filter-chip">📅 {start_date} → {end_date}</span>']
if effective_project != 'All':
    chip_html_parts.append(f'<span class="filter-chip">📌 {effective_project}</span>')
if selected_types and len(selected_types) != len(types_avail):
    chip_html_parts.append(f'<span class="filter-chip">🏷️ {len(selected_types)} of {len(types_avail)} types</span>')
if selected_status and len(selected_status) != len(status_avail):
    chip_html_parts.append(f'<span class="filter-chip">✅ {", ".join(selected_status)}</span>')
st.markdown("".join(chip_html_parts), unsafe_allow_html=True)

# --- KPIs with period-over-period deltas ---
total_earnings = filtered_df['Payable'].sum()
total_hours = filtered_df['Hours'].sum()
total_days_worked = filtered_df['Work Date'].dt.date.nunique()

hourly_rows = filtered_df[filtered_df['Hours'] > 0]
hourly_earnings = hourly_rows['Payable'].sum()
avg_hourly_rate = hourly_earnings / total_hours if total_hours > 0 else 0

best_day_row = (
    filtered_df.groupby('Day')['Payable'].sum().sort_values(ascending=False).head(1)
)
best_day_label = (
    f"${best_day_row.iloc[0]:,.2f} on {best_day_row.index[0].strftime('%b %d')}"
    if not best_day_row.empty else "—"
)

top_project = "—"
if not filtered_df['Project Name'].dropna().empty:
    top_project = filtered_df.groupby('Project Name')['Payable'].sum().idxmax()

# Previous period of equal length, immediately before start_date
period_days = (end_date - start_date).days + 1
prev_end_ts = pd.Timestamp(start_date) - pd.Timedelta(days=1)
prev_start_ts = prev_end_ts - pd.Timedelta(days=period_days - 1)
prev_start_d = prev_start_ts.date()
prev_end_d = prev_end_ts.date()
prev_mask = (df['Work Date'].dt.date >= prev_start_d) & (df['Work Date'].dt.date <= prev_end_d)
if effective_project != 'All':
    prev_mask &= (df['Project Name'] == effective_project)
if selected_types:
    prev_mask &= df['Type'].isin(selected_types)
if selected_status:
    prev_mask &= df['Status'].isin(selected_status)
prev_df = df.loc[prev_mask]
prev_earnings = prev_df['Payable'].sum()
prev_hours = prev_df['Hours'].sum()

def pct_delta(curr, prev):
    if prev <= 0:
        return None
    return (curr - prev) / prev * 100

earn_delta = pct_delta(total_earnings, prev_earnings)
hours_delta = pct_delta(total_hours, prev_hours)

k1, k2, k3, k4, k5 = st.columns(5)
k1.metric(
    "Total Earnings",
    f"${total_earnings:,.2f}",
    delta=(f"{earn_delta:+.1f}% vs prev" if earn_delta is not None else None),
)
k2.metric(
    "Total Hours",
    format_hours(total_hours),
    delta=(f"{hours_delta:+.1f}% vs prev" if hours_delta is not None else None),
)
k3.metric("Work Days", f"{total_days_worked}")
k4.metric("Avg $/hr (time-based)", f"${avg_hourly_rate:,.2f}")
k5.metric("Top Project", str(top_project))

st.divider()

# --- Project click helper (used in Projects tab) ---
proj_stats = filtered_df.groupby('Project Name').agg(
    Earnings=('Payable', 'sum'),
    HoursF=('Hours', 'sum'),
    Days=('Day', 'nunique'),
).reset_index()
proj_stats['Hourly Rate'] = proj_stats.apply(
    lambda r: r['Earnings'] / r['HoursF'] if r['HoursF'] > 0 else 0, axis=1
)
proj_stats['Time'] = proj_stats['HoursF'].apply(format_hours)
proj_stats = proj_stats.sort_values('Earnings', ascending=False)

def _capture_project_click(event_obj):
    if not event_obj:
        return
    sel = getattr(event_obj, "selection", None) or (event_obj.get("selection") if isinstance(event_obj, dict) else None)
    if not sel:
        return
    points = getattr(sel, "points", None) if not isinstance(sel, dict) else sel.get("points")
    if not points:
        return
    p = points[0]
    label = None
    if isinstance(p, dict):
        label = p.get("label") or p.get("y") or p.get("x")
    if label and label != st.session_state.isolate_project and label in projects:
        st.session_state.isolate_project = label
        st.rerun()

# --- Tabs ---
tab_overview, tab_projects, tab_insights, tab_raw = st.tabs(
    ["Overview", "Projects", "Insights", "Raw Data"]
)

# =================== OVERVIEW TAB ===================
with tab_overview:
    left, right = st.columns([3, 1])
    left.subheader("Earnings & Hours Over Time")
    granularity = right.radio(
        "Granularity",
        ["Daily", "Weekly", "Monthly"],
        horizontal=True,
        label_visibility="collapsed",
        index=0,
    )

    group_key = {"Daily": "Day", "Weekly": "Week", "Monthly": "Month"}[granularity]
    trend = (
        filtered_df.groupby(group_key)[['Payable', 'Hours']]
        .sum()
        .reset_index()
        .sort_values(group_key)
    )
    trend['Time_Label'] = trend['Hours'].apply(format_hours)
    trend['Cumulative'] = trend['Payable'].cumsum()

    fig_combo = make_subplots(specs=[[{"secondary_y": True}]])
    fig_combo.add_trace(
        go.Bar(
            x=trend[group_key], y=trend['Payable'],
            name="Earnings", marker_color=COLOR_EARNINGS,
            hovertemplate=f'<b>{granularity}:</b> %{{x}}<br><b>Earnings:</b> $%{{y:,.2f}}<extra></extra>',
        ),
        secondary_y=False,
    )
    fig_combo.add_trace(
        go.Scatter(
            x=trend[group_key], y=trend['Hours'],
            name="Hours", mode='lines+markers',
            line=dict(color=COLOR_HOURS, width=3),
            marker=dict(size=7),
            customdata=trend[['Time_Label']],
            hovertemplate=f'<b>{granularity}:</b> %{{x}}<br><b>Time:</b> %{{customdata[0]}}<extra></extra>',
        ),
        secondary_y=True,
    )
    fig_combo.update_yaxes(title_text="Earnings ($)", secondary_y=False)
    fig_combo.update_yaxes(title_text="Hours", secondary_y=True)
    fig_combo.update_layout(
        template=PLOTLY_TEMPLATE,
        hovermode="x unified",
        legend=dict(orientation="h", y=1.12, x=0),
        margin=dict(t=30, l=10, r=10, b=10),
        xaxis_title=None,
        height=420,
    )
    st.plotly_chart(fig_combo, use_container_width=True)

    st.subheader("Effective $/hr Trend")
    rate_basis = filtered_df.copy()
    rate_basis['WeekStart'] = pd.to_datetime(rate_basis['Week'])
    rate_weekly = (
        rate_basis.groupby('WeekStart')
        .agg(Earnings=('Payable', 'sum'), Hours=('Hours', 'sum'))
        .reset_index()
        .sort_values('WeekStart')
    )
    rate_weekly = rate_weekly[rate_weekly['Hours'] > 0]
    if not rate_weekly.empty:
        rate_weekly['Rate'] = rate_weekly['Earnings'] / rate_weekly['Hours']
        rate_weekly['Time'] = rate_weekly['Hours'].apply(format_hours)
        median_rate = rate_weekly['Rate'].median()
        fig_rate = go.Figure()
        fig_rate.add_trace(go.Scatter(
            x=rate_weekly['WeekStart'], y=rate_weekly['Rate'],
            mode='lines+markers',
            line=dict(color=COLOR_EARNINGS, width=3),
            marker=dict(size=7),
            customdata=rate_weekly[['Earnings', 'Time']],
            hovertemplate='<b>Week of %{x|%b %d, %Y}</b><br>'
                          'Rate: $%{y:.2f}/hr<br>'
                          'Earnings: $%{customdata[0]:,.2f}<br>'
                          'Time: %{customdata[1]}<extra></extra>',
        ))
        fig_rate.add_hline(
            y=median_rate, line_dash='dash', line_color=COLOR_ACCENT,
            annotation_text=f"Median: ${median_rate:.2f}/hr",
            annotation_position="top left",
        )
        fig_rate.update_layout(
            template=PLOTLY_TEMPLATE,
            margin=dict(t=10, l=10, r=10, b=10),
            height=320, xaxis_title=None, yaxis_title="$ / hour",
        )
        st.plotly_chart(fig_rate, use_container_width=True)
    else:
        st.info("Not enough time-tracked rows in the current filter to compute an hourly-rate trend.")

    c_roll, c_heat = st.columns([1, 1])

    with c_roll:
        st.subheader("Rolling 30-day Earnings")
        daily_full = filtered_df.groupby('Day')['Payable'].sum().reset_index()
        daily_full['Day'] = pd.to_datetime(daily_full['Day'])
        if not daily_full.empty:
            full_idx = pd.date_range(daily_full['Day'].min(), daily_full['Day'].max(), freq='D')
            daily_full = (
                daily_full.set_index('Day').reindex(full_idx, fill_value=0)
                .rename_axis('Day').reset_index()
            )
            daily_full['Rolling30'] = daily_full['Payable'].rolling(30, min_periods=1).sum()
            fig_roll = go.Figure()
            fig_roll.add_trace(go.Scatter(
                x=daily_full['Day'], y=daily_full['Rolling30'],
                mode='lines',
                line=dict(color=COLOR_EARNINGS, width=3),
                fill='tozeroy',
                fillcolor='rgba(0,204,150,0.15)',
                hovertemplate='<b>%{x|%b %d, %Y}</b><br>Last 30 days: $%{y:,.2f}<extra></extra>',
            ))
            fig_roll.update_layout(
                template=PLOTLY_TEMPLATE,
                margin=dict(t=10, l=10, r=10, b=10),
                height=380, xaxis_title=None, yaxis_title="Trailing 30d ($)",
            )
            st.plotly_chart(fig_roll, use_container_width=True)
        else:
            st.info("No data to compute rolling earnings.")

    with c_heat:
        st.subheader("Top 10 Earning Days")
        top_days = (
            filtered_df.groupby('Day')
            .agg(Earnings=('Payable', 'sum'), Hours=('Hours', 'sum'))
            .reset_index()
            .sort_values('Earnings', ascending=False)
            .head(10)
        )
        top_days['Day_dt'] = pd.to_datetime(top_days['Day'])
        top_days['Label'] = top_days['Day_dt'].dt.strftime('%a, %b %d')
        top_days['Time'] = top_days['Hours'].apply(format_hours)
        top_days = top_days.iloc[::-1]
        fig_topdays = px.bar(
            top_days, x='Earnings', y='Label', orientation='h',
            color='Earnings', color_continuous_scale='Tealgrn',
            custom_data=['Time'],
        )
        fig_topdays.update_traces(
            texttemplate='$%{x:,.2f}', textposition='outside',
            hovertemplate='<b>%{y}</b><br>Earnings: $%{x:,.2f}<br>Time: %{customdata[0]}<extra></extra>',
        )
        fig_topdays.update_layout(
            template=PLOTLY_TEMPLATE, coloraxis_showscale=False,
            xaxis_title=None, yaxis_title=None,
            margin=dict(t=10, l=10, r=10, b=10), height=380,
        )
        st.plotly_chart(fig_topdays, use_container_width=True)

    # Calendar / contribution-graph style heatmap
    st.subheader("Daily Activity Calendar")
    daily = filtered_df.groupby('Day')['Payable'].sum().reset_index()
    daily['Day'] = pd.to_datetime(daily['Day'])
    if not daily.empty:
        date_index = pd.date_range(daily['Day'].min(), daily['Day'].max(), freq='D')
        daily = daily.set_index('Day').reindex(date_index, fill_value=0).rename_axis('Day').reset_index()
        daily['DOW'] = daily['Day'].dt.day_name()
        daily['Week'] = daily['Day'].dt.to_period('W-SUN').apply(lambda p: p.start_time.strftime('%Y-%m-%d'))
        cal = daily.pivot_table(index='DOW', columns='Week', values='Payable', fill_value=0)
        cal = cal.reindex(DOW_ORDER, fill_value=0)
        fig_cal = px.imshow(
            cal,
            labels=dict(x="Week", y="Day", color="Earnings ($)"),
            color_continuous_scale=[(0, '#1a1f2c'), (0.001, '#0e3b2e'), (0.5, '#00a575'), (1, '#7CFFA8')],
            aspect='auto',
        )
        fig_cal.update_traces(
            hovertemplate='<b>%{y}, week of %{x}</b><br>Earnings: $%{z:,.2f}<extra></extra>',
            xgap=2, ygap=2,
        )
        fig_cal.update_layout(
            template=PLOTLY_TEMPLATE,
            margin=dict(t=10, l=10, r=10, b=10),
            height=260,
        )
        st.plotly_chart(fig_cal, use_container_width=True)

# =================== PROJECTS TAB ===================
with tab_projects:
    st.subheader("Earnings by Project")
    st.caption("Tip: click a slice or a bar below to isolate a project across the entire dashboard.")
    c_top, c_pie = st.columns([3, 2])

    with c_top:
        st.markdown("**Top Projects by Earnings**")
        top_n = proj_stats.head(15).iloc[::-1]
        fig_top = px.bar(
            top_n,
            x='Earnings', y='Project Name', orientation='h',
            color='Earnings', color_continuous_scale='Tealgrn',
            custom_data=['Time', 'Hourly Rate', 'Days'],
        )
        fig_top.update_traces(
            texttemplate='$%{x:,.0f}', textposition='outside',
            hovertemplate='<b>%{y}</b><br>Earnings: $%{x:,.2f}<br>Time: %{customdata[0]}<br>Days: %{customdata[2]}<br>Rate: $%{customdata[1]:.2f}/hr<extra></extra>',
        )
        fig_top.update_layout(
            template=PLOTLY_TEMPLATE, coloraxis_showscale=False,
            xaxis_title=None, yaxis_title=None,
            margin=dict(t=10, l=10, r=10, b=10), height=460,
        )
        top_event = st.plotly_chart(
            fig_top, use_container_width=True, key="top_chart", on_select="rerun"
        )
        _capture_project_click(top_event)

    with c_pie:
        st.markdown("**Project Earnings Share**")
        fig_pie = px.pie(
            proj_stats, values='Earnings', names='Project Name',
            hole=0.55, color_discrete_sequence=px.colors.qualitative.Pastel,
        )
        fig_pie.update_traces(
            textposition='inside', textinfo='percent', sort=True,
            hovertemplate='<b>%{label}</b><br>Earnings: $%{value:,.2f}<br>Share: %{percent}<extra></extra>',
        )
        fig_pie.update_layout(
            template=PLOTLY_TEMPLATE, showlegend=True,
            legend=dict(orientation='v', y=0.5, x=1.02, font=dict(size=10)),
            margin=dict(t=10, l=10, r=10, b=10), height=460,
        )
        pie_event = st.plotly_chart(
            fig_pie, use_container_width=True, key="pie_chart", on_select="rerun"
        )
        _capture_project_click(pie_event)

    st.markdown("**Project performance**")
    table_view = proj_stats[['Project Name', 'Earnings', 'Time', 'Days', 'Hourly Rate']].copy()
    st.dataframe(
        table_view,
        use_container_width=True, hide_index=True,
        column_config={
            "Project Name": st.column_config.TextColumn("Project"),
            "Earnings": st.column_config.NumberColumn("Earnings", format="$%.2f"),
            "Time": st.column_config.TextColumn("Time"),
            "Days": st.column_config.NumberColumn("Days", format="%d"),
            "Hourly Rate": st.column_config.NumberColumn("Rate", format="$%.2f/hr"),
        },
    )

    st.markdown("**Earnings vs. Hours by Project**")
    fig_scatter = px.scatter(
        proj_stats[proj_stats['HoursF'] > 0],
        x='HoursF', y='Earnings',
        size='Earnings', color='Project Name',
        hover_name='Project Name',
        custom_data=['Time', 'Hourly Rate', 'Days'],
        size_max=50,
    )
    fig_scatter.update_traces(
        hovertemplate='<b>%{hovertext}</b><br>Earnings: $%{y:,.2f}<br>Time: %{customdata[0]}<br>Days: %{customdata[2]}<br>Rate: $%{customdata[1]:.2f}/hr<extra></extra>',
    )
    fig_scatter.update_layout(
        template=PLOTLY_TEMPLATE,
        xaxis_title="Hours", yaxis_title="Earnings ($)",
        margin=dict(t=10, l=10, r=10, b=10), showlegend=False, height=440,
    )
    st.plotly_chart(fig_scatter, use_container_width=True)

    st.markdown("**Earnings by Task Type**")
    type_counts = (
        filtered_df.groupby('Type')['Payable']
        .agg(['sum', 'count']).reset_index()
        .rename(columns={'sum': 'Earnings', 'count': 'Records'})
        .sort_values('Earnings', ascending=False)
    )
    fig_type = px.bar(
        type_counts, x='Type', y='Earnings',
        color='Type', color_discrete_sequence=px.colors.qualitative.Bold,
        custom_data=['Records'],
    )
    fig_type.update_traces(
        texttemplate='$%{y:,.2f}', textposition='outside',
        hovertemplate='<b>%{x}</b><br>Earnings: $%{y:,.2f}<br>Records: %{customdata[0]}<extra></extra>',
    )
    fig_type.update_layout(
        template=PLOTLY_TEMPLATE, showlegend=False,
        yaxis_title=None, xaxis_title=None,
        margin=dict(t=10, l=10, r=10, b=10), height=380,
    )
    st.plotly_chart(fig_type, use_container_width=True)

# =================== INSIGHTS TAB ===================
with tab_insights:
    # Goal progress for the LATEST month within filtered range
    if not filtered_df.empty:
        latest_month = filtered_df['Month'].max()
        latest_month_earn = filtered_df[filtered_df['Month'] == latest_month]['Payable'].sum()
    else:
        latest_month = None
        latest_month_earn = 0

    progress_pct = min(latest_month_earn / monthly_goal, 1.0) if monthly_goal > 0 else 0

    g1, g2 = st.columns([2, 1])
    with g1:
        st.subheader(f"Goal progress — {latest_month or 'no data'}")
        st.progress(progress_pct, text=f"${latest_month_earn:,.2f} / ${monthly_goal:,.0f}  ({progress_pct*100:.1f}%)")
        if monthly_goal > 0 and latest_month_earn >= monthly_goal:
            st.success(f"Goal reached — surplus of ${latest_month_earn - monthly_goal:,.2f}")
        elif monthly_goal > 0:
            st.warning(f"${monthly_goal - latest_month_earn:,.2f} remaining to hit your monthly goal")
    with g2:
        gauge = go.Figure(go.Indicator(
            mode="gauge+number",
            value=latest_month_earn,
            number={'prefix': "$", 'valueformat': ',.0f'},
            gauge={
                'axis': {'range': [0, max(monthly_goal, latest_month_earn or 1)]},
                'bar': {'color': COLOR_EARNINGS},
                'steps': [
                    {'range': [0, monthly_goal * 0.5 if monthly_goal > 0 else 1], 'color': 'rgba(239,85,59,0.3)'},
                    {'range': [monthly_goal * 0.5 if monthly_goal > 0 else 1, monthly_goal if monthly_goal > 0 else 1], 'color': 'rgba(255,161,90,0.3)'},
                ],
                'threshold': {'line': {'color': "white", 'width': 2}, 'thickness': 0.85, 'value': monthly_goal},
            },
        ))
        gauge.update_layout(
            template=PLOTLY_TEMPLATE,
            margin=dict(t=10, l=10, r=10, b=10), height=220,
        )
        st.plotly_chart(gauge, use_container_width=True)

    st.divider()

    # Auto-generated insight cards
    st.subheader("At-a-glance insights")
    insights = []

    # 1. Best day of week
    dow_sum = filtered_df.groupby('DayOfWeek')['Payable'].sum()
    if not dow_sum.empty:
        best_dow = dow_sum.idxmax()
        worst_dow = dow_sum.idxmin()
        insights.append(("Strongest day of week", f"{best_dow} — ${dow_sum[best_dow]:,.2f} earned"))
        insights.append(("Quietest day of week", f"{worst_dow} — ${dow_sum[worst_dow]:,.2f} earned"))

    # 2. Best month overall
    month_sum = filtered_df.groupby('Month')['Payable'].sum()
    if not month_sum.empty:
        best_month = month_sum.idxmax()
        insights.append(("Best month", f"{best_month} — ${month_sum[best_month]:,.2f}"))

    # 3. Highest-earning project
    proj_sum = filtered_df.groupby('Project Name')['Payable'].sum()
    if not proj_sum.empty:
        top_p = proj_sum.idxmax()
        insights.append(("Top project", f"{top_p} — ${proj_sum[top_p]:,.2f} ({proj_sum[top_p]/total_earnings*100:.1f}% of total)"))

    # 4. Best $/hr project (with hours)
    rate_df = proj_stats[proj_stats['HoursF'] > 0]
    if not rate_df.empty:
        best_rate_row = rate_df.sort_values('Hourly Rate', ascending=False).iloc[0]
        insights.append((
            "Highest hourly rate (project)",
            f"{best_rate_row['Project Name']} — ${best_rate_row['Hourly Rate']:.2f}/hr over {best_rate_row['Time']}"
        ))

    # 5. Type concentration
    type_sum = filtered_df.groupby('Type')['Payable'].sum().sort_values(ascending=False)
    if not type_sum.empty and total_earnings > 0:
        top_type = type_sum.index[0]
        share = type_sum.iloc[0] / total_earnings * 100
        insights.append(("Dominant task type", f"{top_type} drives {share:.1f}% of earnings"))

    # 6. Period delta
    if earn_delta is not None:
        direction = "up" if earn_delta >= 0 else "down"
        insights.append(("vs Previous period", f"Earnings {direction} {abs(earn_delta):.1f}% — ${total_earnings - prev_earnings:+,.2f}"))

    # 7. Avg per active day
    if total_days_worked > 0:
        insights.append(("Average earnings per work day", f"${total_earnings / total_days_worked:,.2f}"))
        insights.append(("Average hours per work day", format_hours(total_hours / total_days_worked)))

    # Render in a 2-col grid
    cols = st.columns(2)
    for i, (label, val) in enumerate(insights):
        with cols[i % 2]:
            st.markdown(
                f'<div class="insight-card"><div class="label">{label}</div><div class="value">{val}</div></div>',
                unsafe_allow_html=True,
            )

    st.divider()

    # Hourly rate distribution
    st.subheader("Effective hourly-rate distribution")
    rate_rows = filtered_df[filtered_df['Hours'] > 0].copy()
    if not rate_rows.empty:
        rate_rows['Effective $/hr'] = rate_rows['Payable'] / rate_rows['Hours']
        rate_rows = rate_rows[rate_rows['Effective $/hr'] < rate_rows['Effective $/hr'].quantile(0.99) + 1]
        median_rate = rate_rows['Effective $/hr'].median()
        fig_hist = px.histogram(
            rate_rows, x='Effective $/hr', nbins=40,
            color_discrete_sequence=[COLOR_EARNINGS],
        )
        fig_hist.add_vline(
            x=median_rate, line_dash='dash', line_color=COLOR_ACCENT,
            annotation_text=f"Median: ${median_rate:.2f}/hr",
            annotation_position="top right",
        )
        fig_hist.update_layout(
            template=PLOTLY_TEMPLATE,
            margin=dict(t=10, l=10, r=10, b=10), height=320,
            yaxis_title="Records", xaxis_title="$/hr",
            bargap=0.05,
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No time-tracked rows in current filter to show rate distribution.")

    # Month-over-month comparison
    st.subheader("Month-over-month")
    mom = filtered_df.groupby('Month').agg(
        Earnings=('Payable', 'sum'),
        Hours=('Hours', 'sum'),
        Days=('Day', 'nunique'),
    ).reset_index().sort_values('Month')
    if not mom.empty:
        mom['MoM %'] = mom['Earnings'].pct_change() * 100
        mom['Time'] = mom['Hours'].apply(format_hours)
        fig_mom = go.Figure()
        fig_mom.add_trace(go.Bar(
            x=mom['Month'], y=mom['Earnings'],
            name='Earnings', marker_color=COLOR_EARNINGS,
            text=[f"${v:,.0f}" for v in mom['Earnings']],
            textposition='outside',
            hovertemplate='<b>%{x}</b><br>Earnings: $%{y:,.2f}<extra></extra>',
        ))
        fig_mom.add_trace(go.Scatter(
            x=mom['Month'], y=mom['MoM %'].fillna(0),
            name='MoM %', mode='lines+markers',
            line=dict(color=COLOR_ACCENT, width=3), yaxis='y2',
            hovertemplate='<b>%{x}</b><br>MoM: %{y:+.1f}%<extra></extra>',
        ))
        fig_mom.update_layout(
            template=PLOTLY_TEMPLATE,
            yaxis=dict(title='Earnings ($)'),
            yaxis2=dict(title='MoM %', overlaying='y', side='right', showgrid=False),
            legend=dict(orientation='h', y=1.12, x=0),
            margin=dict(t=30, l=10, r=10, b=10), height=380,
            xaxis_title=None,
        )
        st.plotly_chart(fig_mom, use_container_width=True)

# =================== RAW DATA TAB ===================
with tab_raw:
    st.subheader("Filtered records")
    display_df = filtered_df.sort_values('Work Date', ascending=False).copy()
    display_df['Time'] = display_df['Hours'].apply(format_hours)
    display_df['Work Date'] = display_df['Work Date'].dt.strftime('%Y-%m-%d')
    cols_keep = [c for c in [
        'Work Date', 'Project Name', 'Type', 'Duration', 'Time',
        'Rate', 'Payable', 'Status'
    ] if c in display_df.columns]

    search_q = st.text_input("Search (project, type, status, etc.)", value="")
    table_df = display_df[cols_keep]
    if search_q.strip():
        q = search_q.strip().lower()
        table_df = table_df[table_df.apply(lambda r: q in ' '.join(map(str, r.values)).lower(), axis=1)]

    st.caption(f"Showing **{len(table_df):,}** of {len(display_df):,} records")

    st.dataframe(
        table_df,
        use_container_width=True, hide_index=True,
        column_config={
            "Payable": st.column_config.NumberColumn("Payable", format="$%.2f"),
        } if 'Payable' in cols_keep else None,
    )

    csv_bytes = table_df.to_csv(index=False).encode('utf-8')
    st.download_button(
        "Download filtered data (CSV)",
        data=csv_bytes,
        file_name="earnings_filtered.csv",
        mime="text/csv",
    )