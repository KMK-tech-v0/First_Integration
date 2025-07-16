import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import base64, os, webbrowser, textwrap, io
from datetime import datetime, timedelta
import pyodbc
import json
import folium
import re
import matplotlib.dates as mdates
import folium.plugins

# --- Data Loading ---
# Define the path to the Excel file. Adjust this path if your file is located elsewhere.
excel_path = r'D:\My Base\Share_Analyst\SM Daily Report\Regression Of CA.xlsx'
df = pd.read_excel(excel_path, sheet_name='CAX_dt', header=1)
# df = pd.read_excel(excel_path, sheet_name='CAX_dt', header =1) # Commented out for mock data demo
# df['Site_ID'] = df['Site_ID'].astype(str) # Ensure 'Site_ID' is treated as a string to avoid issues with mixed types.

# SQL data loading configuration
server = r'DESKTOP-17P73P0\SQLEXPRESS'
database = 'MMP_Analysis'
# Construct the connection string for SQL Server.
conn_str = (
    r'DRIVER={SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    'Trusted_Connection=yes;' # Use Windows authentication for a trusted connection.
)
##Establish a connection to the SQL database and load data from 'cax' and 'BKD_SUMMARY' tables.
with pyodbc.connect(conn_str) as conn: # Commented out for mock data demo
     df_sql = pd.read_sql("SELECT * FROM cax", conn)
     df_sql_bkd = pd.read_sql("SELECT * FROM BKD_SUMMARY", conn) # df_sql_bkd was missing its mock data
     df_sql_wo = pd.read_sql("SELECT * FROM wo_file", conn)

TARGET_TOWNSHIP = 'Kale'

# --- Helper: Matplotlib Figure to Base64 ---
# Function to convert a matplotlib figure to a base64 encoded PNG image for embedding in HTML.
def fig_to_base64img(fig):
    """Converts a Matplotlib figure to a base64-encoded PNG image."""
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight', dpi=150) # Save the figure to a bytes buffer with higher DPI.
    buf.seek(0) # Reset buffer position to the beginning.
    img_base64 = base64.b64encode(buf.read()).decode('utf-8') # Encode to base64.
    plt.close(fig) # Close the figure to free up memory.
    return img_base64

# --- Helper: Format Timedelta for Display (Days, Hours, Minutes) ---
def format_timedelta_dhms(td):
    """Formats a timedelta object into a human-readable string (e.g., '10D 5Hr 30Min')."""
    if pd.isna(td):
        return "-"
    total_seconds = td.total_seconds()
    if total_seconds < 0: # Handle negative timedeltas gracefully
        return "N/A (Future Time)"

    days = int(total_seconds // (24 * 3600))
    hours = int((total_seconds % (24 * 3600)) // 3600)
    minutes = int((total_seconds % 3600) // 60)
    
    parts = []
    if days > 0:
        parts.append(f"{days}D")
    if hours > 0:
        parts.append(f"{hours}Hr")
    if minutes > 0:
        parts.append(f"{minutes}Min")

    return " ".join(parts) if parts else "0Min"

# --- Filter Data for TARGET_TOWNSHIP ---
df_kale = df[(df['Township'] == TARGET_TOWNSHIP) & (df['Township'] != '!SWO')].copy()
df_sql_kale = df_sql[df_sql['Township'] == TARGET_TOWNSHIP].copy()
df_sql_bkd_kale = df_sql_bkd[df_sql_bkd['Township'] == TARGET_TOWNSHIP].copy()
df_sql_wo_kale = df_sql_wo[df_sql_wo['Site_ID'].isin(df_kale['Site_ID'])].copy() # Filter WO by sites in Kale

# Ensure 'Render' and 'STD_RFO' columns exist in df_sql_kale before any operations that might use them
if 'Render' not in df_sql_kale.columns:
    df_sql_kale['Render'] = 'Unknown (Column Missing)'
if 'STD_RFO' not in df_sql_kale.columns:
    df_sql_kale['STD_RFO'] = 'Unknown (Column Missing)'

# Ensure 'Render' column in df_sql_kale has no missing values and filter out '!SWO'.
df_sql_kale = df_sql_kale[df_sql_kale['Render'].notna()].copy()
df_sql_kale = df_sql_kale[df_sql_kale['Render'] != '!SWO'].copy() # Filter out '!SWO' as requested

# Add 'Date' column from 'Raise_Time' to df_kale for temporal analysis, coercing errors to NaT.
df_kale['Raise_Time_dt'] = pd.to_datetime(df_kale['Raise_Time'], errors='coerce')
df_sql_wo_kale['Raise_Time_dt'] = pd.to_datetime(df_sql_wo_kale['Raise_Time'], errors='coerce')
df_sql_wo_kale['Clear_Time_dt'] = pd.to_datetime(df_sql_wo_kale['Clear_Time'], errors='coerce')
df_sql_wo_kale['Downtime_Duration'] = df_sql_wo_kale['Clear_Time_dt'] - df_sql_wo_kale['Raise_Time_dt']
df_sql_wo_kale['Downtime_Hours'] = df_sql_wo_kale['Downtime_Duration'].dt.total_seconds() / 3600

print(f"✅ Data filtered for {TARGET_TOWNSHIP}.")

# --- 1. Site Inventory Overview ---
total_sites_kale = df_kale['Site_ID'].nunique()
online_sites_kale = df_kale[df_kale['Issue_Identity'] == 'Active']['Site_ID'].nunique()
down_sites_kale = total_sites_kale - online_sites_kale
effectiveness_kale = (online_sites_kale / total_sites_kale * 100) if total_sites_kale > 0 else 0

site_inventory_html = f"""
<h3 style="color:#1976d2; font-size:1.1rem;">1. Site Inventory Overview for {TARGET_TOWNSHIP}</h3>
<ul style="font-size:0.95rem;">
    <li><b>Total Number of Sites:</b> {total_sites_kale}</li>
    <li><b>Sites Currently Online:</b> {online_sites_kale}</li>
    <li><b>Sites Currently Down:</b> {down_sites_kale}</li>
    <li><b>Overall Effectiveness:</b> {effectiveness_kale:.2f}%</li>
</ul>
"""

# --- 2. Render-Wise Categorization ---
render_summary = df_kale.groupby('Render').agg(
    Site_Count=('Site_ID', 'nunique'),
    Online_Count=('Issue_Identity', lambda x: (x == 'Active').sum()),
    Downtime_Hours_Avg=('Site_ID', lambda site_ids: df_sql_wo_kale[df_sql_wo_kale['Site_ID'].isin(site_ids)]['Downtime_Hours'].mean())
).reset_index()
render_summary['Percentage'] = (render_summary['Site_Count'] / render_summary['Site_Count'].sum() * 100).round(2)
render_summary['Effectiveness (%)'] = (render_summary['Online_Count'] / render_summary['Site_Count'] * 100).round(2)
render_summary['Downtime_Hours_Avg'] = render_summary['Downtime_Hours_Avg'].round(2)

render_summary_html = render_summary.to_html(index=False, classes="styled-table", escape=False)

# Chart for Render Distribution
fig_render_dist, ax_render_dist = plt.subplots(figsize=(8, 5))
colors_render = sns.color_palette("pastel", len(render_summary))
ax_render_dist.pie(render_summary['Site_Count'], labels=render_summary['Render'], autopct='%1.1f%%', startangle=90, colors=colors_render, pctdistance=0.85)
ax_render_dist.set_title(f'Site Distribution by Render Type in {TARGET_TOWNSHIP}', fontsize=12)
ax_render_dist.axis('equal') # Equal aspect ratio ensures that pie is drawn as a circle.
img_render_dist = fig_to_base64img(fig_render_dist)

render_analysis_html = f"""
<h3 style="color:#388e3c; font-size:1.1rem;">2. Render-Wise Categorization for {TARGET_TOWNSHIP}</h3>
<p style="font-size:0.95rem;">Grouping of sites by their 'Render' type (Active vs. To be Active) provides insights into the operational status distribution and performance metrics across these categories.</p>
<div style="overflow-x:auto;">{render_summary_html}</div>
<img src="data:image/png;base64,{img_render_dist}" style="max-width:100%;border:1px solid #ccc;margin:10px 0;">
"""

# --- 3. Prolonging Analysis Timeline (Interactive) ---
prolonged_issues_kale = df_kale[
    (df_kale['Raise_Time_dt'].notna()) &
    (~df_kale['Issue_Identity'].isin(['Active', 'PIC_Finder is not Active']))
].copy()

now = datetime.now()
prolonged_issues_kale['Prolonging Duration'] = prolonged_issues_kale['Raise_Time_dt'].apply(
    lambda x: now - x if pd.notna(x) else pd.Timedelta(0)
)
prolonged_issues_kale['Prolonging Days'] = prolonged_issues_kale['Prolonging Duration'].apply(lambda x: x.total_seconds() / (24 * 3600) if pd.notnull(x) else np.nan)

# Categorize sites by activity duration
def categorize_duration(days):
    if pd.isna(days): return "Active (online)" # Assuming 'Active' implies no downtime
    if days >= 365: return "Almost a year"
    if days >= 180: return "Within 6 months"
    if days >= 90: return "Within 3 months"
    if days >= 60: return "Within 2 months"
    if days >= 30: return "Within 1 month"
    if days >= 7: return "Within 1 week"
    return "Less than 1 week"

prolonged_issues_kale['Duration_Category'] = prolonged_issues_kale['Prolonging Days'].apply(categorize_duration)

# Ensure 'Render' and 'STD_RFO' columns exist in prolonged_issues_kale with a default value
# This prevents KeyError if the merge doesn't introduce them for all rows or if prolonged_issues_kale is initially empty
if 'Render' not in prolonged_issues_kale.columns:
    prolonged_issues_kale['Render'] = 'Unknown'
if 'STD_RFO' not in prolonged_issues_kale.columns:
    prolonged_issues_kale['STD_RFO'] = 'Unknown'

# Prepare a DataFrame for merging, ensuring 'STD_RFO' exists
# Since 'Render' and 'STD_RFO' are now guaranteed to exist in df_sql_kale, we can select them directly.
merge_df_for_prolonging = df_sql_kale[['Site_ID', 'Render', 'STD_RFO']].drop_duplicates(subset=['Site_ID'])

# Merge with prolonged_issues_kale
# Use suffixes to clearly distinguish merged columns, then coalesce
prolonged_issues_kale = prolonged_issues_kale.merge(
    merge_df_for_prolonging,
    on='Site_ID',
    how='left',
    suffixes=('_original', '_from_sql')
)

# Coalesce the columns: prefer the merged values, fall back to original (or 'Unknown')
# If 'Render_from_sql' exists and is not NaN, use it. Otherwise, use 'Render_original'.
# This handles cases where the original 'Render' might have been set to 'Unknown' and then updated by the merge.
prolonged_issues_kale['Render'] = prolonged_issues_kale['Render_from_sql'].fillna(prolonged_issues_kale['Render_original'])
prolonged_issues_kale['STD_RFO'] = prolonged_issues_kale['STD_RFO_from_sql'].fillna(prolonged_issues_kale['STD_RFO_original'])

# Drop the temporary original and merged columns
prolonged_issues_kale = prolonged_issues_kale.drop(columns=['Render_original', 'STD_RFO_original', 'Render_from_sql', 'STD_RFO_from_sql'])


# Prepare data for interactive filtering
prolonging_data_json = prolonged_issues_kale[[
    'Site_ID', 'Issue_Identity', 'Render', 'Duration_Category', 'STD_RFO', 'Prolonging Duration'
]].to_dict(orient='records')

# Convert timedelta objects to formatted strings
for item in prolonging_data_json:
    if isinstance(item['Prolonging Duration'], timedelta):
        item['Prolonging Duration'] = format_timedelta_dhms(item['Prolonging Duration'])
    elif pd.isna(item['Prolonging Duration']):
        item['Prolonging Duration'] = '-'

prolonging_data_json = json.dumps(prolonging_data_json)

# Get unique values for dropdowns
unique_prolong_renders = sorted(prolonged_issues_kale['Render'].dropna().unique().tolist())
duration_order = ["Active (online)", "Less than 1 week", "Within 1 week", "Within 1 month", "Within 2 months", "Within 3 months", "Within 6 months", "Almost a year"] # Define duration_order here
unique_prolong_duration_categories = sorted(prolonged_issues_kale['Duration_Category'].dropna().unique().tolist(), key=lambda x: duration_order.index(x) if x in duration_order else len(duration_order))
unique_prolong_root_causes = sorted(prolonged_issues_kale['STD_RFO'].dropna().unique().tolist())
unique_prolong_issue_identities = sorted(prolonged_issues_kale['Issue_Identity'].dropna().unique().tolist())

prolonging_analysis_html = f"""
<h3 style="color:#673ab7; font-size:1.1rem;">3. Prolonging Analysis Timeline for {TARGET_TOWNSHIP} (Interactive)</h3>
<p style="font-size:0.95rem;">Explore prolonged issues by filtering across various categories. Downtime duration is shown in Days, Hours, and Minutes.</p>

<div style="display:flex; flex-wrap:wrap; gap:15px; margin-bottom:20px; padding:15px; background-color:#f0f8ff; border-radius:8px;">
    <div>
        <label for="prolongRenderSelect" style="font-weight:bold;">Filter by Render:</label>
        <select id="prolongRenderSelect" style="padding: 6px 10px; border-radius: 4px; border: 1px solid #ccc;">
            <option value="All">All Renders</option>
            {''.join(f'<option value="{r}">{r}</option>' for r in unique_prolong_renders)}
        </select>
    </div>
    <div>
        <label for="prolongDurationSelect" style="font-weight:bold;">Filter by Duration Category:</label>
        <select id="prolongDurationSelect" style="padding: 6px 10px; border-radius: 4px; border: 1px solid #ccc;">
            <option value="All">All Durations</option>
            {''.join(f'<option value="{d}">{d}</option>' for d in unique_prolong_duration_categories)}
        </select>
    </div>
    <div>
        <label for="prolongRootCauseSelect" style="font-weight:bold;">Filter by Root Cause (STD_RFO):</label>
        <select id="prolongRootCauseSelect" style="padding: 6px 10px; border-radius: 4px; border: 1px solid #ccc;">
            <option value="All">All Root Causes</option>
            {''.join(f'<option value="{rc}">{rc}</option>' for rc in unique_prolong_root_causes)}
        </select>
    </div>
    <div>
        <label for="prolongIssueIdentitySelect" style="font-weight:bold;">Filter by Issue Identity:</label>
        <select id="prolongIssueIdentitySelect" style="padding: 6px 10px; border-radius: 4px; border: 1px solid #ccc;">
            <option value="All">All Issue Identities</option>
            {''.join(f'<option value="{ii}">{ii}</option>' for ii in unique_prolong_issue_identities)}
        </select>
    </div>
</div>

<div id="prolongedIssuesTableContainer" style="overflow-x:auto;">
    <!-- Prolonged issues table will be rendered here by JavaScript -->
</div>
"""

# --- 4. Cell Availability (CA) Analysis ---
# Calculate overall average CA result for each site
site_avg_ca = df_sql_kale.groupby('Site_ID')['CA_Result'].mean().round(2).reset_index()
site_avg_ca.columns = ['Site_ID', 'Avg_CA_Result']

# Add up/down arrows based on comparison to overall average CA result (or previous week/month)
# For simplicity, let's compare to the overall mean CA result for Kale
overall_mean_ca = df_sql_kale['CA_Result'].mean()

site_avg_ca['Trend'] = ''
for idx, row in site_avg_ca.iterrows():
    if row['Avg_CA_Result'] > overall_mean_ca:
        site_avg_ca.loc[idx, 'Trend'] = '<span style="color:green; font-size:1.2em;">▲</span>'
    elif row['Avg_CA_Result'] < overall_mean_ca:
        site_avg_ca.loc[idx, 'Trend'] = '<span style="color:red; font-size:1.2em;">▼</span>'
    else:
        site_avg_ca.loc[idx, 'Trend'] = '<span style="color:gray; font-size:1.2em;">━</span>'

site_avg_ca['Avg_CA_Result_Display'] = site_avg_ca.apply(lambda x: f"{x['Avg_CA_Result']} {x['Trend']}", axis=1) # Removed %
site_avg_ca_html = site_avg_ca[['Site_ID', 'Avg_CA_Result_Display']].to_html(index=False, classes="styled-table", escape=False)


# Issue_Identity patterns for Kale (excluding 'Active' and 'PIC_Finder is not Active')
issue_patterns_kale = df_kale[
    ~df_kale['Issue_Identity'].isin(['Active', 'PIC_Finder is not Active'])
]['Issue_Identity'].value_counts().reset_index()
issue_patterns_kale.columns = ['Issue_Identity', 'Count']
issue_patterns_kale['Percentage'] = (issue_patterns_kale['Count'] / issue_patterns_kale['Count'].sum() * 100).round(2)

issue_patterns_html = issue_patterns_kale.to_html(index=False, classes="styled-table", escape=False)


# New: CA Trend Graph with fluctuations, arrows, and colors
df_sql_kale['Date_dt'] = pd.to_datetime(df_sql_kale['Date'])
df_sql_kale['WeekNumber'] = df_sql_kale['Date_dt'].dt.isocalendar().week.astype(int)

# Prepare data for interactive weekly CA trend by render
weekly_ca_trend_data = {}
unique_renders = df_sql_kale['Render'].unique().tolist()
unique_renders.sort() # Sort renders alphabetically

# Add an 'All Renders' option
unique_renders.insert(0, 'All Renders')

for render in unique_renders:
    if render == 'All Renders':
        temp_df = df_sql_kale.copy()
    else:
        temp_df = df_sql_kale[df_sql_kale['Render'] == render].copy()
    
    if not temp_df.empty:
        weekly_trend = temp_df.groupby('WeekNumber')['CA_Result'].mean().reset_index()
        weekly_trend.columns = ['WeekNumber', 'Avg_CA_Result']
        weekly_trend['Prev_Avg_CA'] = weekly_trend['Avg_CA_Result'].shift(1)
        weekly_trend['Change'] = weekly_trend['Avg_CA_Result'] - weekly_trend['Prev_Avg_CA']
        
        # Prepare data for Chart.js
        labels = weekly_trend['WeekNumber'].astype(str).tolist()
        data = weekly_trend['Avg_CA_Result'].round(2).tolist()
        changes = weekly_trend['Change'].round(2).tolist()
        
        weekly_ca_trend_data[render] = {
            'labels': labels,
            'data': data,
            'changes': changes
        }
    else:
        weekly_ca_trend_data[render] = {
            'labels': [],
            'data': [],
            'changes': []
        }

# Convert Python dict to JSON string for JavaScript
weekly_ca_trend_json = json.dumps(weekly_ca_trend_data)
unique_renders_json = json.dumps(unique_renders)

corrective_action_html = f"""
<h3 style="color:#f57c00; font-size:1.1rem;">4. Cell Availability (CA) Analysis for {TARGET_TOWNSHIP}</h3>
<p style="font-size:0.95rem;">Overall average CA performance scores for each site in {TARGET_TOWNSHIP} (compared to overall mean):</p>
<div style="overflow-x:auto;">{site_avg_ca_html}</div>
<p style="font-size:0.95rem;">Issue Identity patterns (excluding 'Active' and 'PIC_Finder is not Active'):</p>
<div style="overflow-x:auto;">{issue_patterns_html}</div>

<h4 style="color:#f57c00; font-size:1rem; margin-top:20px;">Weekly Average CA Performance Score Trend by Render</h4>
<p style="font-size:0.95rem;">Select a Render type to view its weekly average Cell Availability (CA) performance score trend. Arrows indicate improvement (green ▲), decline (red ▼), or stability (━) compared to the previous week.</p>
<div style="margin-bottom: 15px;">
    <label for="renderSelect" style="font-size:0.95rem; font-weight:bold; margin-right:10px;">Select Render:</label>
    <select id="renderSelect" style="padding: 8px 12px; border-radius: 5px; border: 1px solid #ccc; font-size:0.9rem;">
    </select>
</div>
<div style="width: 100%; max-width: 900px; margin: 0 auto;">
    <canvas id="caTrendChart"></canvas>
</div>
"""

# --- 5. Site Value Analysis and Recommendations ---
# Criteria for valuable/non-valuable sites
# Valuable: High Avg_CA_Result, low number of issues, low average downtime
# Non-valuable: Low Avg_CA_Result, high number of issues, high average downtime

# Calculate key metrics per site
site_performance = df_kale.groupby('Site_ID').agg(
    Total_Issues=('Issue_Identity', lambda x: (~x.isin(['Active', 'PIC_Finder is not Active'])).sum()),
    Active_Status=('Issue_Identity', lambda x: 'Active' if 'Active' in x.values else 'Inactive'),
    Last_Issue_Time=('Raise_Time_dt', 'max')
).reset_index()

site_performance = site_performance.merge(site_avg_ca[['Site_ID', 'Avg_CA_Result']], on='Site_ID', how='left')
site_performance['Avg_CA_Result'] = site_performance['Avg_CA_Result'].fillna(0) # Fill NaN for sites with no CA data

# Add average downtime from WO data
site_wo_downtime = df_sql_wo_kale.groupby('Site_ID')['Downtime_Hours'].mean().round(2).reset_index()
site_wo_downtime.columns = ['Site_ID', 'Avg_Downtime_Hours']
site_performance = site_performance.merge(site_wo_downtime, on='Site_ID', how='left')
site_performance['Avg_Downtime_Hours'] = site_performance['Avg_Downtime_Hours'].fillna(0)

# Identify Valuable Sites
# Criteria: Active, high Avg_CA_Result (e.g., > 90), low total issues (e.g., <= 1)
valuable_sites = site_performance[
    (site_performance['Active_Status'] == 'Active') &
    (site_performance['Avg_CA_Result'] >= 90) &
    (site_performance['Total_Issues'] <= 1)
].sort_values(by='Avg_CA_Result', ascending=False)

# Identify Non-Valuable Sites
# Criteria: Inactive, low Avg_CA_Result (e.g., < 70), high total issues (e.g., > 5), high average downtime
non_valuable_sites = site_performance[
    (site_performance['Active_Status'] == 'Inactive') |
    (site_performance['Avg_CA_Result'] < 70) |
    (site_performance['Total_Issues'] > 5) |
    (site_performance['Avg_Downtime_Hours'] > 24*7) # More than a week of average downtime
].sort_values(by=['Total_Issues', 'Avg_Downtime_Hours'], ascending=[False, False])

valuable_sites_html = "<ul>"
if not valuable_sites.empty:
    for _, row in valuable_sites.head(5).iterrows(): # Show top 5
        valuable_sites_html += f"<li><b>{row['Site_ID']}</b>: Avg CA: {row['Avg_CA_Result']}, Issues: {row['Total_Issues']}, Avg Downtime: {row['Avg_Downtime_Hours']:.1f} hrs. (Consistently high performance, minimal issues.)</li>"
else:
    valuable_sites_html += "<li>No sites identified as highly valuable based on current criteria.</li>"
valuable_sites_html += "</ul>"

non_valuable_sites_html = "<ul>"
if not non_valuable_sites.empty:
    for _, row in non_valuable_sites.head(5).iterrows(): # Show top 5
        non_valuable_sites_html += f"<li><b>{row['Site_ID']}</b>: Avg CA: {row['Avg_CA_Result']}, Issues: {row['Total_Issues']}, Avg Downtime: {row['Avg_Downtime_Hours']:.1f} hrs. (Frequent issues, low CA, or prolonged outages.)</li>"
else:
    non_valuable_sites_html += "<li>No sites identified as significantly non-valuable based on current criteria.</li>"
non_valuable_sites_html += "</ul>"

site_value_analysis_html = f"""
<h3 style="color:#8bc34a; font-size:1.1rem;">5. Site Value Analysis and Recommendations for {TARGET_TOWNSHIP}</h3>
<p style="font-size:0.95rem;">Based on the analysis of Cell Availability (CA) performance scores, issue frequency, and average downtime, sites are categorized by their operational value.</p>

<h4 style="color:#8bc34a; font-size:1rem; margin-top:15px;">Valuable Sites (Top Performers)</h4>
<p style="font-size:0.9rem;">These sites exhibit high average CA performance scores, minimal operational issues, and contribute significantly to Site stability:</p>
{valuable_sites_html}

<h4 style="color:#ef5350; font-size:1rem; margin-top:15px;">Sites Requiring Attention (Non-Valuable / Underperforming)</h4>
<p style="font-size:0.9rem;">These sites show lower CA performance scores, frequent or prolonged issues, and may require immediate intervention or re-evaluation:</p>
{non_valuable_sites_html}

<p style="font-size:0.95rem; margin-top:20px;"><b>Recommendations:</b></p>
<ul style="font-size:0.9rem;">
    <li><b>For Valuable Sites:</b> Continue monitoring and consider these sites as benchmarks for best practices. Invest in proactive maintenance to maintain their high performance.</li>
    <li><b>For Sites Requiring Attention:</b> Prioritize detailed investigation into the root causes of their underperformance. Allocate resources for targeted repairs, upgrades, or re-evaluation of their strategic importance if issues persist.</li>
</ul>
"""


# --- Executive Summary ---
executive_summary_html = f"""
<h2 style="font-size:1.5rem; color:#1976d2;">📌 Executive Summary: Site Performance in {TARGET_TOWNSHIP}</h2>
<blockquote style="border-left: 4px solid #1976d2; padding-left: 12px; color: #333; font-style: italic; font-size:0.9rem; background-color: #eef7ff; padding: 15px; border-radius: 8px;">
    This report provides a comprehensive analysis of Site performance within <b>{TARGET_TOWNSHIP}</b>, highlighting key operational metrics, and temporal trends.
    <ul style="font-size:0.9rem; margin-top: 8px; padding-left: 20px;">
        <li><b>Site Overview:</b> {total_sites_kale} total sites in {TARGET_TOWNSHIP}, with {online_sites_kale} currently online ({effectiveness_kale:.2f}% effectiveness).</li>
        <li><b>Key Issues:</b> The most prevalent non-active issues include {', '.join(issue_patterns_kale['Issue_Identity'].head(3).tolist() if not issue_patterns_kale.empty else ['N/A'])}. These recurring issues warrant focused attention for resolution.</li>
        <li><b>Prolonged Outages:</b> Sites experiencing prolonged downtime are categorized, with a notable number of sites being down for various periods. This section is now interactive, allowing filtering by Render, Duration Category, Root Cause, and Issue Identity, with durations shown in Days, Hours, and Minutes.</li>
        <li><b>CA Trend:</b> The weekly average Cell Availability (CA) performance scores show fluctuations, which are detailed in the "CA Analysis" section with visual indicators of improvement or decline, and can be filtered by render type.</li>
        <li><b>Site Value:</b> Identified valuable sites demonstrate consistent high performance, while others require attention due to recurring issues or prolonged outages.</li>
        <li><b>Recommendation:</b> Prioritize investigation into the top root causes and prolonged issues identified. Leverage the geospatial insights for efficient resource allocation and proactive maintenance strategies to enhance Site stability and reliability in {TARGET_TOWNSHIP}.</li>
    </ul>
</blockquote>
"""

# --- Dataframe Viewer HTML (for all dataframes) ---
dataframe_dict = {
    f"Detail Data ({TARGET_TOWNSHIP})": df_kale,
    f"SQL Data ({TARGET_TOWNSHIP})": df_sql_kale,
    f"BKD Summary ({TARGET_TOWNSHIP})": df_sql_bkd_kale, # Added df_sql_bkd_kale to the viewer
    f"WO File ({TARGET_TOWNSHIP})": df_sql_wo_kale,
}

dataframe_tabs = []
dataframe_contents = []
for idx, (df_name, df_obj) in enumerate(dataframe_dict.items()):
    safe_id = f"df_tab_{idx}"
    html_table = df_obj.head(100).to_html(
        index=False,
        classes="display compact nowrap attractive-df-table",
        table_id=f"df_table_{idx}",
        escape=False
    )
    dataframe_tabs.append(
        f'<button class="df-tab-btn" data-df-tab="{safe_id}">{df_name}</button>'
    )
    dataframe_contents.append(
        f"""
        <div id="{safe_id}" class="df-tab-content" style="display:none;">
            <h3 style="color:#1976d2;">{df_name} (First 100 rows)</h3>
            <div style="overflow-x:auto;">{html_table}</div>
            <div style="font-size:0.9em;color:#888;margin-top:8px;">
                <em>Showing up to 100 rows for performance. Use export for full data.</em>
            </div>
        </div>
        """
    )

dataframe_viewer_html = f"""
<!-- Floating button to open dataframe viewer -->
<button id="openDfViewerBtn" title="View All DataFrames" style="
    position: fixed; bottom: 30px; right: 30px; z-index: 2000;
    background: linear-gradient(90deg,#1976d2 60%,#42a5f5 100%);
    color: #fff; border: none; border-radius: 50%; width: 60px; height: 60px;
    box-shadow: 0 4px 16px rgba(25,118,210,0.25);
    font-size: 2.1em; font-weight: bold; cursor: pointer; display: flex; align-items: center; justify-content: center;
    transition: background 0.2s, box-shadow 0.2s;
">
    <span style="font-size:1.5em;">🗂️</span>
</button>
<div id="dfViewerModal" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.18); z-index:2100;">
  <div style="background:#fff; margin:40px auto; padding:25px; border-radius:14px; max-width:1200px; min-width:350px; position:relative; overflow-y: auto; max-height: calc(100vh - 80px); box-shadow: 0 8px 32px rgba(25,118,210,0.18);">
    <button onclick="document.getElementById('dfViewerModal').style.display='none'" style="position:absolute; top:8px; right:8px; font-size:1.3em; background:none; border:none; cursor:pointer; color:#888;">✖</button>
    <h2 style="color:#1976d2;">🗂️ DataFrame Explorer for {TARGET_TOWNSHIP}</h2>
    <div style="margin-bottom:12px;color:#444;font-size:1em;">
        <b>Explore all related dataframes interactively.</b> Click a tab below to view each dataframe. Use search, filter, and export as needed.
    </div>
    <div class="df-tab-bar" style="display:flex;gap:8px;margin-bottom:10px;">
        {''.join(dataframe_tabs)}
    </div>
    <div>
        {''.join(dataframe_contents)}
    </div>
  </div>
</div>
"""

# --- Build Tabbed HTML Report ---
tab_buttons = []
tab_contents = []

# Add Executive Summary tab
tab_buttons.append('<button type="button" class="tablinks" data-tab="executive_summary_tab">📋 Executive Summary</button>')
tab_contents.append(f"""
<div id="executive_summary_tab" class="tabcontent">
    {executive_summary_html}
</div>
""")

# Add Site Inventory Overview tab
tab_buttons.append('<button type="button" class="tablinks" data-tab="site_inventory_tab">📍 Site Inventory</button>')
tab_contents.append(f"""
<div id="site_inventory_tab" class="tabcontent">
    {site_inventory_html}
</div>
""")

# Add Render-Wise Categorization tab
tab_buttons.append('<button type="button" class="tablinks" data-tab="render_categorization_tab">📊 Render Categorization</button>')
tab_contents.append(f"""
<div id="render_categorization_tab" class="tabcontent">
    {render_analysis_html}
</div>
""")

# Add Prolonging Analysis Timeline tab
tab_buttons.append('<button type="button" class="tablinks" data-tab="prolonging_analysis_tab">⏳ Prolonging Analysis</button>')
tab_contents.append(f"""
<div id="prolonging_analysis_tab" class="tabcontent">
    {prolonging_analysis_html}
</div>
""")

# Add Cell Availability (CA) Analysis tab (now tab 4)
tab_buttons.append('<button type="button" class="tablinks" data-tab="ca_analysis_tab">✅ CA Analysis</button>')
tab_contents.append(f"""
<div id="ca_analysis_tab" class="tabcontent">
    {corrective_action_html}
</div>
""")

# Add Site Value Analysis tab (now tab 5)
tab_buttons.append('<button type="button" class="tablinks" data-tab="site_value_tab">⭐ Site Value Analysis</button>')
tab_contents.append(f"""
<div id="site_value_tab" class="tabcontent">
    {site_value_analysis_html}
</div>
""")

# --- JS for Tabs & Modals ---
js_script = f"""
<script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
<script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/dataTables.buttons.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.html5.min.js"></script>
<script src="https://cdn.datatables.net/buttons/2.4.2/js/buttons.print.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>

<script>
document.addEventListener("DOMContentLoaded", function () {{
    const tabs = document.querySelectorAll(".tablinks");
    const contents = document.querySelectorAll(".tabcontent");

    function openTab(tabId) {{
        contents.forEach(el => {{
            el.classList.remove("active");
            el.style.display = "none";
        }});
        tabs.forEach(btn => btn.classList.remove("active"));
        const target = document.getElementById(tabId);
        if (target) {{
            target.classList.add("active");
            target.style.display = "block";
            // If CA Analysis tab is opened, update the chart
            if (tabId === 'ca_analysis_tab') {{
                updateCaChart();
            }}
            // If Prolonging Analysis tab is opened, update the table
            if (tabId === 'prolonging_analysis_tab') {{
                updateProlongedIssuesTable();
            }}
        }}
    }}

    tabs.forEach(btn => {{
        btn.addEventListener("click", function () {{
            const tabId = btn.getAttribute("data-tab");
            openTab(tabId);
            this.classList.add("active");
        }});
    }});

    // Open the first tab by default on page load.
    if (tabs.length > 0) {{
        tabs[0].click();
    }}

    // --- DataFrame Viewer JS ---
    document.getElementById('openDfViewerBtn').onclick = function() {{
        document.getElementById('dfViewerModal').style.display = 'block';
        var firstTab = document.querySelector('.df-tab-btn');
        if (firstTab) firstTab.click();
    }};

    var dfTabBtns = document.querySelectorAll('.df-tab-btn');
    var dfTabContents = document.querySelectorAll('.df-tab-content');
    dfTabBtns.forEach(function(btn) {{
        btn.onclick = function() {{
            dfTabBtns.forEach(b => b.classList.remove('active'));
            dfTabContents.forEach(c => c.style.display = 'none');
            btn.classList.add('active');
            var tabId = btn.getAttribute('data-df-tab');
            var tabContent = document.getElementById(tabId);
            if (tabContent) {{
                tabContent.style.display = 'block';
                var table = tabContent.querySelector('table');
                if (table && !$.fn.DataTable.isDataTable(table)) {{
                    $(table).DataTable({{
                        scrollX: true,
                        pageLength: 15,
                        lengthMenu: [ [10, 15, 25, 50, -1], [10, 15, 25, 50, "All"] ],
                        dom: 'lBfrtip',
                        buttons: ['excel', 'print'],
                        initComplete: function () {{
                            this.api().columns().every(function () {{
                                var column = this;
                                var select = $('<select class="column-filter-select"><option value="">All</option></select>')
                                    .appendTo($(column.footer()).empty())
                                    .on('change', function () {{
                                        var val = $.fn.dataTable.util.escapeRegex(
                                            $(this).val()
                                        );
                                        column
                                            .search(val ? '^' + val + '$' : '', true, false)
                                            .draw();
                                    }});

                                column.data().unique().sort().each(function (d, j) {{
                                    select.append('<option value="' + d + '">' + d + '</option>')
                                }});
                            }});
                        }}
                    }});
                }} else if (table && $.fn.DataTable.isDataTable(table)) {{
                    // If already initialized, just redraw to adjust columns
                    $(table).DataTable().columns.adjust().draw();
                }}
            }}
        }};
    }});

    // --- CA Trend Chart Logic ---
    const caTrendData = {weekly_ca_trend_json};
    const uniqueRenders = {unique_renders_json};
    let caChart;

    const renderSelect = document.getElementById('renderSelect');
    uniqueRenders.forEach(render => {{
        const option = document.createElement('option');
        option.value = render;
        option.textContent = render;
        renderSelect.appendChild(option);
    }});

    function updateCaChart() {{
        const selectedRender = renderSelect.value;
        const dataForRender = caTrendData[selectedRender];

        if (!dataForRender || dataForRender.labels.length === 0) {{
            if (caChart) {{
                caChart.destroy();
                caChart = null;
            }}
            document.getElementById('caTrendChart').getContext('2d').clearRect(0, 0, document.getElementById('caTrendChart').width, document.getElementById('caTrendChart').height);
            document.getElementById('caTrendChart').style.display = 'none';
            return;
        }} else {{
            document.getElementById('caTrendChart').style.display = 'block';
        }}

        const ctx = document.getElementById('caTrendChart').getContext('2d');

        const datasets = [
            {{
                label: `Average CA Result for ${{selectedRender}}`,
                data: dataForRender.data,
                borderColor: '#1976d2',
                backgroundColor: 'rgba(25, 118, 210, 0.2)',
                tension: 0.3,
                fill: false,
                pointRadius: 7,
                pointBackgroundColor: (context) => {{
                    const index = context.dataIndex;
                    if (index === 0) return '#1976d2'; // First point
                    const change = dataForRender.changes[index];
                    if (change > 0) return 'green';
                    if (change < 0) return 'red';
                    return 'gray';
                }},
                pointBorderColor: (context) => {{
                    const index = context.dataIndex;
                    if (index === 0) return '#1976d2'; // First point
                    const change = dataForRender.changes[index];
                    if (change > 0) return 'green';
                    if (change < 0) return 'red';
                    return 'gray';
                }},
                pointBorderWidth: 2,
            }}
        ];

        if (caChart) {{
            caChart.data.labels = dataForRender.labels;
            caChart.data.datasets = datasets;
            caChart.update();
        }} else {{
            caChart = new Chart(ctx, {{
                type: 'line',
                data: {{
                    labels: dataForRender.labels,
                    datasets: datasets
                }},
                options: {{
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {{
                        title: {{
                            display: true,
                            text: `Weekly Average CA Performance Score Trend for ${{selectedRender}}`,
                            font: {{ size: 16, weight: 'bold' }},
                            color: '#1976d2'
                        }},
                        tooltip: {{
                            callbacks: {{
                                label: function(context) {{
                                    let label = context.dataset.label || '';
                                    if (label) {{
                                        label += ': ';
                                    }}
                                    if (context.parsed.y !== null) {{
                                        label += context.parsed.y; // Removed %
                                    }}
                                    const index = context.dataIndex;
                                    if (index > 0) {{
                                        const change = dataForRender.changes[index];
                                        if (change !== null) {{
                                            let arrow = '';
                                            let changeText = '';
                                            if (change > 0) {{
                                                arrow = '▲';
                                                changeText = ` (+${{Math.abs(change).toFixed(1)}})`; // Removed %
                                            }} else if (change < 0) {{
                                                arrow = '▼';
                                                changeText = ` (-${{Math.abs(change).toFixed(1)}})`; // Removed %
                                            }} else {{
                                                arrow = '━';
                                                changeText = ` (No Change)`;
                                            }}
                                            label += ` ${{arrow}}${{changeText}}`;
                                        }}
                                    }}
                                    return label;
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{
                            title: {{
                                display: true,
                                text: 'Week Number',
                                font: {{ size: 12 }}
                            }}
                        }},
                        y: {{
                            title: {{
                                display: true,
                                text: 'Average CA Performance Score', // Updated label
                                font: {{ size: 12 }}
                            }},
                            beginAtZero: true,
                            max: 100 // CA scores are typically 0-100
                        }}
                    }}
                }}
            }});
        }}
    }}

    renderSelect.addEventListener('change', updateCaChart);

    // --- Prolonging Analysis Interactive Table Logic ---
    const prolongingData = {prolonging_data_json};
    const durationOrder = {json.dumps(duration_order)}; // Pass duration_order to JS
    let prolongingDataTable;

    const prolongRenderSelect = document.getElementById('prolongRenderSelect');
    const prolongDurationSelect = document.getElementById('prolongDurationSelect');
    const prolongRootCauseSelect = document.getElementById('prolongRootCauseSelect');
    const prolongIssueIdentitySelect = document.getElementById('prolongIssueIdentitySelect');
    const prolongedIssuesTableContainer = document.getElementById('prolongedIssuesTableContainer');

    function updateProlongedIssuesTable() {{
        const selectedRender = prolongRenderSelect.value;
        const selectedDuration = prolongDurationSelect.value;
        const selectedRootCause = prolongRootCauseSelect.value;
        const selectedIssueIdentity = prolongIssueIdentitySelect.value;

        let filteredData = prolongingData.filter(item => {{
            const matchRender = (selectedRender === 'All' || item.Render === selectedRender);
            const matchDuration = (selectedDuration === 'All' || item.Duration_Category === selectedDuration);
            const matchRootCause = (selectedRootCause === 'All' || item.STD_RFO === selectedRootCause);
            const matchIssueIdentity = (selectedIssueIdentity === 'All' || item.Issue_Identity === selectedIssueIdentity);
            return matchRender && matchDuration && matchRootCause && matchIssueIdentity;
        }});

        // Destroy existing DataTable if it exists
        if (prolongingDataTable) {{
            prolongingDataTable.destroy();
            prolongedIssuesTableContainer.innerHTML = ''; // Clear content
        }}

        if (filteredData.length === 0) {{
            prolongedIssuesTableContainer.innerHTML = '<p style="text-align:center; color:#555; font-size:0.95rem; margin-top:20px;">No data found for the selected filters.</p>';
            return;
        }}

        // Create table HTML
        let tableHtml = '<table id="prolongedIssuesTable" class="display compact nowrap styled-table"><thead><tr>';
        tableHtml += '<th>Site ID</th><th>Issue Identity</th><th>Render</th><th>Duration Category</th><th>Root Cause</th><th>Prolonging Duration</th>';
        tableHtml += '</tr></thead><tbody>';
        filteredData.forEach(item => {{
            tableHtml += `<tr>
                <td>${{item['Site_ID']}}</td>
                <td>${{item['Issue_Identity']}}</td>
                <td>${{item['Render']}}</td>
                <td>${{item['Duration_Category']}}</td>
                <td>${{item['STD_RFO']}}</td>
                <td>${{item['Prolonging Duration']}}</td>
            </tr>`;
        }});
        tableHtml += '</tbody></table>';
        prolongedIssuesTableContainer.innerHTML = tableHtml;

        // Initialize DataTable
        prolongingDataTable = $('#prolongedIssuesTable').DataTable({{
            scrollX: true,
            pageLength: 10,
            lengthMenu: [ [10, 15, 25, 50, -1], [10, 15, 25, 50, "All"] ],
            dom: 'lBfrtip',
            buttons: ['excel', 'print']
        }});
    }}

    prolongRenderSelect.addEventListener('change', updateProlongedIssuesTable);
    prolongDurationSelect.addEventListener('change', updateProlongedIssuesTable);
    prolongRootCauseSelect.addEventListener('change', updateProlongedIssuesTable);
    prolongIssueIdentitySelect.addEventListener('change', updateProlongedIssuesTable);

    // Initial load for Prolonging Analysis table
    if (document.getElementById('prolonging_analysis_tab').classList.contains('active')) {{
        updateProlongedIssuesTable();
    }}
}});
</script>
"""

# --- Professional Table Styling (CSS) ---
pro_table_style = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    body {
        font-family: 'Inter', sans-serif;
        font-size: 0.875rem;
        background: url('https://plus.unsplash.com/premium_photo-1661347859297-859b8ae1d7c5?w=600&auto=format&fit=crop&q=60&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxzZWFyY2h8MXx8YnVzaW5lc3MlMjBtZWV0aW5nfGVufDB8fDB8fHww');
        background-size: cover;
        position: relative;
    }
    body::before {
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        z-index: -2;
        background: inherit;
        filter: blur(4px) brightness(0.8);
        width: 100vw;
        height: 100vh;
    }
    body::after {
        content: "";
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        z-index: -1;
        background: rgba(255,255,255,0.35);
    }
    .tabcontent, .ao-card, .container, .df-tab-content, .tab-header {
        background: rgba(255,255,255,0.4);
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(30,64,175,0.10);
        padding: 24px;
        margin-bottom: 30px;
    }

    h1 { font-size: 1.8rem; }
    h2 { font-size: 1.5rem; }
    h3 { font-size: 1.1rem; }
    p, ul, li { font-size: 0.9rem; }

    table {
        border-collapse: separate !important;
        border-spacing: 0;
        width: 100%;
        margin: 20px 0;
        font-size: 0.95em;
        background: #fff;
        box-shadow: 0 2px 10px rgba(30,64,175,0.05);
        border-radius: 8px;
    }
    th, td {
        border: 1px solid #eef2f6 !important;
        padding: 10px 12px !important;
        text-align: left;
        vertical-align: middle;
    }
    th {
        background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
        color: #0d47a1;
        font-weight: 700;
        font-size: 1em;
        border-bottom: 2px solid #a7d9f7 !important;
        position: sticky;
        top: 0;
        z-index: 2;
    }
    tr {
        border-bottom: 1px solid #f0f3f6 !important;
        transition: background 0.2s;
    }
    tr:nth-child(even) {
        background: #fdfefe;
    }
    tr:hover {
        background: #e9f5fd;
    }
    td {
        color: #222;
        font-size: 0.95em;
        white-space: nowrap;
    }
    details { margin: 4px 0; }
    summary { font-size: 0.9em; }
    details div { font-size: 0.85em; }

    @media (max-width: 900px) {
        table, thead, tbody, th, td, tr { display: block; }
        th, td { padding: 8px 6px !important; }
        tr { margin-bottom: 8px; }
    }

    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 0.85rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-radius: 6px;
        overflow: hidden;
    }
    .styled-table thead th {
        background-color: #f0f8ff;
        color: #333;
        font-weight: bold;
        padding: 8px 12px;
        border-bottom: 1px solid #a7d9f7;
        text-align: left;
    }
    .styled-table tbody td {
        padding: 8px 12px;
        border-bottom: 1px solid #eef2f6;
        white-space: nowrap;
    }
    .styled-table tbody tr:last-child td { border-bottom: none; }
    .styled-table tbody tr:nth-child(even) { background-color: #fdfefe; }
    .styled-table tbody tr:hover { background-color: #f0faff; }

    body { padding: 20px; }
    .tab-header { position: sticky; top: 0; background: #fff; z-index: 100; padding: 6px 0; border-bottom: 1px solid #e0e0e0; }
    .tablinks {
        background: #e0f0ff; border: none; padding: 8px 14px; margin: 2px;
        cursor: pointer; font-size: 0.95rem; border-radius: 5px; color: #1565c0;
        transition: background-color 0.3s ease, transform 0.1s ease;
    }
    .tablinks:hover {
        background-color: #cce0ff;
        transform: translateY(-1px);
    }
    .tablinks.active {
        background-color: #1565c0; color: #fff; font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15);
        transform: translateY(0px);
    }
    .tabcontent { display: none; padding-top: 15px; }
    .tabcontent.active { display: block; }
    
    #openDfViewerBtn {
        animation: fadeIn 1s ease;
        transition: box-shadow 0.3s;
    }
    #openDfViewerBtn:hover {
        box-shadow: 0 0 15px #1976d2, 0 2px 6px rgba(30, 64, 175, 0.1);
    }
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(-15px);}
        to {opacity: 1; transform: translateY(0);}
    }

    .dataTables_wrapper { font-size: 0.85rem; }
    table.dataTable thead th {
        background-color: #e3f2fd;
        color: #0d47a1;
        font-weight: bold;
        text-align: center;
        padding: 10px 15px !important;
        border-bottom: 1px solid #a7d9f7 !important;
        border-right: 1px solid #eef2f6;
    }
    table.dataTable tbody td {
        padding: 8px 15px !important;
        border-bottom: 1px solid #eef2f6;
        border-right: 1px solid #f4f7f6;
        white-space: nowrap;
    }
    table.dataTable tbody tr:nth-child(even) { background-color: #f7fbff; }
    table.dataTable tbody tr:hover { background-color: #e0f0ff; }
    table.dataTable { border-spacing: 0; }
    table.dataTable thead th:last-child,
    table.dataTable tbody td:last-child { border-right: none; }

    .dataTables_wrapper .dataTables_filter input,
    .dataTables_wrapper .dataTables_length select,
    .column-filter-select {
        border: 1px solid #cbd5e0;
        border-radius: 0.375rem;
        padding: 0.4rem 0.6rem;
        margin-left: 0.4rem;
        margin-right: 0.4rem;
        background-color: #ffffff;
        font-size: 0.8rem;
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.06);
        transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .dataTables_wrapper .dataTables_filter input:focus,
    .dataTables_wrapper .dataTables_length select:focus,
    .column-filter-select:focus {
        border-color: #3b82f6;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25);
        outline: none;
    }

    .dataTables_wrapper .dataTables_paginate .paginate_button,
    .dt-buttons .dt-button {
        background-color: #4299e1;
        color: white;
        padding: 0.4rem 0.8rem;
        border-radius: 0.375rem;
        cursor: pointer;
        border: none;
        margin: 0 0.2rem;
        transition: background-color 0.2s ease-in-out;
        font-size: 0.8rem;
    }
    .dataTables_wrapper .dataTables_paginate .paginate_button.current {
        background-color: #2b6cb0;
        font-weight: bold;
    }
    .dataTables_wrapper .dataTables_info {
        font-size: 0.8rem;
        color: #6b7280;
        margin-top: 1rem;
    }

    .column-filters-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.8rem;
        margin-bottom: 1rem;
        padding: 0.8rem;
        background-color: #edf2f7;
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .column-filters-container label {
        font-weight: 500;
        color: #2d3748;
        display: flex;
        align-items: center;
        font-size: 0.85rem;
    }
    /* Style for DataTables footer filters */
    .dataTables_wrapper tfoot th {
        padding: 5px 10px !important;
        border-top: 1px solid #eef2f6;
    }
    .dataTables_wrapper tfoot th select {
        width: 100%;
        padding: 4px;
        border-radius: 4px;
        border: 1px solid #ccc;
        font-size: 0.8em;
    }
</style>
"""

# --- Final HTML Assembly ---
now_str = datetime.now().strftime("%Y-%m-%d %H:%M")
final_html = f"""
<html>
<head>
<title>🔧 Site Performance Analysis: {TARGET_TOWNSHIP}</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
<link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css"/>
{pro_table_style}
</head>
<body>
<h1 style="font-size:2rem;">🔧 Site Performance Analysis: {TARGET_TOWNSHIP}</h1>
<p style="font-size:0.95rem;"><strong>Reported on:</strong> {now_str}</p>
<div class="tab-header">{''.join(tab_buttons)}</div>
{''.join(tab_contents)}
{dataframe_viewer_html}
{js_script}
<footer style="margin-top: 40px; padding-top: 15px; border-top: 1px solid #e0e0e0; color: #666; font-size: 0.8rem; text-align: center;">
    Report prepared by <strong>AI Assistant</strong><br>
    <em>Data Analyst</em>
</footer>
</body>
</html>
"""

# --- Output and Save (for local execution) ---
# This part is for local execution and will not run in the sandbox.
# You can uncomment and adjust the paths if you run this script on your machine.
output_dir = r'D:\My Base\Share_Analyst\SM Daily Report' # Example: create a 'reports' folder in the script's directory
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, f"kale_Site_analysis-{TARGET_TOWNSHIP}-{datetime.now().strftime('%Y%m%d%H%M%S')}.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(final_html)
print(f"✅ Report saved to: {output_path}")

import webbrowser
webbrowser.open(f"file://{output_path}")

# For demonstration in the sandbox, we'll just print a success message.
print(f"✅ HTML report for {TARGET_TOWNSHIP} generated successfully within the script.")
print("The full HTML content is ready to be displayed.")
