import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import re

# --- Configuration ---
st.set_page_config(page_title="Earnings & Time Dashboard", layout="wide")

# --- Helper Functions ---

def parse_duration(duration_str):
    """
    Parses strings like '1h 40m 0s', '40m', '1m 43s' into total hours (float).
    """
    if pd.isna(duration_str) or str(duration_str).strip() in ["-", ""]:
        return 0.0

    hours = 0
    minutes = 0
    seconds = 0

    # Regex to capture hours, minutes, seconds
    h_match = re.search(r'(\d+)h', str(duration_str))
    m_match = re.search(r'(\d+)m', str(duration_str))
    s_match = re.search(r'(\d+)s', str(duration_str))

    if h_match: hours = int(h_match.group(1))
    if m_match: minutes = int(m_match.group(1))
    if s_match: seconds = int(s_match.group(1))

    return hours + (minutes / 60) + (seconds / 3600)

def format_hours(hours_float):
    """
    Converts a float (e.g., 1.5) to a string (e.g., '1h 30m').
    """
    if pd.isna(hours_float):
        return "0h 0m"
    hours = int(hours_float)
    minutes = int((hours_float - hours) * 60)
    return f"{hours}h {minutes}m"

def load_data(file):
    name = getattr(file, "name", "").lower()
    if name.endswith((".xlsx", ".xls")):
        df = pd.read_excel(file)
    else:
        df = pd.read_csv(file)

    # 1. Clean 'Payable'
    df['Payable'] = df['Payable'].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
    df['Payable'] = pd.to_numeric(df['Payable'], errors='coerce').fillna(0.0)

    # 2. Clean 'Rate'
    df['Rate_Clean'] = df['Rate'].astype(str).str.replace('$', '', regex=False).str.replace('/hr', '', regex=False).str.replace(',', '', regex=False)
    df['Rate_Clean'] = pd.to_numeric(df['Rate_Clean'], errors='coerce').fillna(0)

    # 3. Parse 'Duration' to Hours
    df['Hours'] = df['Duration'].apply(parse_duration)

    # 4. Convert 'Work Date' to datetime
    df['Work Date'] = pd.to_datetime(df['Work Date'])

    # 5. Extract additional time features
    df['Month'] = df['Work Date'].dt.strftime('%Y-%m')
    df['Day'] = df['Work Date'].dt.date

    return df

# --- Main Dashboard ---

st.title("Freelance Earnings & Time Tracking")

# File Uploader
uploaded_file = st.file_uploader("Upload your earnings file (CSV or Excel)", type=['csv', 'xlsx', 'xls'])

if uploaded_file is not None:
    try:
        df = load_data(uploaded_file)

        # --- Sidebar Filters ---
        st.sidebar.header("Filters")

        # Date Range Filter
        min_date = df['Work Date'].min().date()
        max_date = df['Work Date'].max().date()
        start_date, end_date = st.sidebar.date_input(
            "Select Date Range",
            value=[min_date, max_date],
            min_value=min_date,
            max_value=max_date
        )

        # Project Filter
        projects = ['All'] + sorted(df['Project Name'].dropna().unique().tolist())
        selected_project = st.sidebar.selectbox("Select Project", projects)

        # Apply Filters
        mask = (df['Work Date'].dt.date >= start_date) & (df['Work Date'].dt.date <= end_date)
        if selected_project != 'All':
            mask = mask & (df['Project Name'] == selected_project)

        filtered_df = df.loc[mask]

        # --- Top Level Metrics ---

        total_earnings = filtered_df['Payable'].sum()
        total_hours = filtered_df['Hours'].sum()
        total_days_worked = filtered_df['Work Date'].nunique()

        # Weighted Average Hourly Rate
        avg_hourly_rate = total_earnings / total_hours if total_hours > 0 else 0

        c1, c2, c3, c4 = st.columns(4)
        with c1: st.metric("Total Earnings", f"${total_earnings:,.2f}")
        with c2: st.metric("Total Hours", format_hours(total_hours))
        with c3: st.metric("Work Days", f"{total_days_worked}")
        with c4: st.metric("Avg Hourly Rate", f"${avg_hourly_rate:,.2f}/hr")

        st.markdown("---")

        # --- Charts Row 1: Trends ---

        c_chart1, c_chart2 = st.columns(2)

        daily_stats = (
            filtered_df.groupby('Day')[['Payable', 'Hours']]
            .sum()
            .reset_index()
            .sort_values('Day', ascending=False)
        )
        daily_stats['Time_Label'] = daily_stats['Hours'].apply(format_hours)

        # 1. Daily Hours Chart (line + markers)
        with c_chart1:
            st.subheader("Daily Hours Worked")
            fig_hours = go.Figure()
            fig_hours.add_trace(go.Scatter(
                x=daily_stats['Day'],
                y=daily_stats['Hours'],
                mode='lines+markers',
                line=dict(color='#A5A0F0', width=2),
                marker=dict(size=7, color='#A5A0F0',
                            line=dict(width=1.5, color='#A5A0F0')),
                customdata=daily_stats[['Time_Label']],
                hovertemplate='<b>Date:</b> %{x|%b %d, %Y}<br>'
                              '<b>Time:</b> %{customdata[0]}<extra></extra>',
            ))
            fig_hours.update_layout(
                margin=dict(t=10, l=10, r=10, b=10),
                xaxis_title=None,
                yaxis_title=None,
                xaxis=dict(autorange='reversed', showgrid=True,
                           gridcolor='rgba(120,120,120,0.25)', griddash='dot'),
                yaxis=dict(showgrid=True, gridcolor='rgba(120,120,120,0.25)',
                           griddash='dot', ticksuffix='h'),
                plot_bgcolor='rgba(0,0,0,0)',
                hoverlabel=dict(bgcolor='white', font_color='black'),
                height=360,
            )
            st.plotly_chart(fig_hours, use_container_width=True)

        # 2. Daily Earnings Chart (bars)
        with c_chart2:
            st.subheader("Daily Earnings")
            fig_daily = go.Figure()
            fig_daily.add_trace(go.Bar(
                x=daily_stats['Day'],
                y=daily_stats['Payable'],
                marker_color='#86D2A8',
                hovertemplate='<b>Date:</b> %{x|%b %d, %Y}<br>'
                              '<b>totalEarnings:</b> $%{y:,.2f}<extra></extra>',
            ))
            fig_daily.update_layout(
                margin=dict(t=10, l=10, r=10, b=10),
                xaxis_title=None,
                yaxis_title=None,
                xaxis=dict(autorange='reversed', showgrid=True,
                           gridcolor='rgba(120,120,120,0.25)', griddash='dot'),
                yaxis=dict(showgrid=True, gridcolor='rgba(120,120,120,0.25)',
                           griddash='dot', tickprefix='$', tickformat=',.2f'),
                plot_bgcolor='rgba(0,0,0,0)',
                hoverlabel=dict(bgcolor='white', font_color='black'),
                bargap=0.25,
                height=360,
            )
            st.plotly_chart(fig_daily, use_container_width=True)

        # --- Charts Row 2: Distribution ---

        c_chart3, c_chart4 = st.columns(2)

        # 3. Project Pie Chart
        with c_chart3:
            st.subheader("Earnings by Project")
            project_earnings = filtered_df.groupby('Project Name')['Payable'].sum().reset_index()

            fig_pie = px.pie(
                project_earnings,
                values='Payable',
                names='Project Name',
                hole=0.4,
                title="Project Earnings Share",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_pie.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig_pie, use_container_width=True)

        # 4. Task Type Chart
        with c_chart4:
            st.subheader("Task Type Distribution")
            type_counts = filtered_df.groupby('Type')['Payable'].sum().reset_index()

            fig_type = px.bar(
                type_counts,
                x='Type',
                y='Payable',
                title="Earnings by Task Type",
                text='Payable',
                color='Type',
                color_discrete_sequence=px.colors.qualitative.Bold
            )
            fig_type.update_traces(texttemplate='$%{y:.2f}', textposition='outside')
            fig_type.update_layout(showlegend=False, yaxis_title=None, xaxis_title=None)
            st.plotly_chart(fig_type, use_container_width=True)

        # --- Charts Row 3: Project Performance ---

        st.subheader("Project Performance Details")
        proj_stats = filtered_df.groupby('Project Name').agg({
            'Payable': 'sum',
            'Hours': 'sum',
            'Work Date': 'nunique'
        }).reset_index()

        proj_stats['Effective Rate'] = proj_stats['Payable'] / proj_stats['Hours']
        proj_stats['Time_Label'] = proj_stats['Hours'].apply(format_hours)

        fig_scatter = px.scatter(
            proj_stats,
            x='Hours',
            y='Payable',
            size='Payable',
            color='Project Name',
            title="Earnings vs. Hours by Project",
            hover_name='Project Name',
            custom_data=['Time_Label', 'Effective Rate']
        )

        fig_scatter.update_traces(
            hovertemplate='<b>%{hovertext}</b><br>' +
                          'Earnings: $%{y:.2f}<br>' +
                          'Time: %{customdata[0]}<br>' +
                          'Rate: $%{customdata[1]:.2f}/hr<extra></extra>'
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        # Display Data Table
        with st.expander("View Raw Data"):
            st.dataframe(filtered_df.sort_values(by='Work Date', ascending=False))

    except Exception as e:
        st.error(f"Error processing file: {e}")
else:
    st.info("Please upload your earnings CSV or Excel file to generate the dashboard.")
