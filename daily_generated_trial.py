import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import base64, os, webbrowser, textwrap, io
from datetime import datetime
import pyodbc
import json
import folium
import re

# --- Data Loading ---
# Define the path to the Excel file. Adjust this path if your file is located elsewhere.
excel_path = r'D:\My Base\Share_Analyst\Regression Of CA.xlsx'
df = pd.read_excel(excel_path, sheet_name='CAX_dt')
df['Site ID'] = df['Site ID'].astype(str) # Ensure 'Site ID' is treated as a string to avoid issues with mixed types.

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
# Establish a connection to the SQL database and load data from 'cax' and 'BKD_SUMMARY' tables.
with pyodbc.connect(conn_str) as conn:
    df_sql = pd.read_sql("SELECT * FROM cax", conn)
    df_sql_bkd = pd.read_sql("SELECT * FROM BKD_SUMMARY", conn)
    df_sql_wo = pd.read_sql("SELECT * FROM wo_file", conn)

# --- WO File Analysis: Site ID & STD_RFO Breakdown ---

# 1. Total distinct Site ID count and list
total_distinct_sites = df_sql_wo['Site_ID'].nunique()

# 2. Prepare datetime columns and downtime
df_sql_wo['Raise_Time_dt'] = pd.to_datetime(df_sql_wo['Raise_Time'], errors='coerce')
df_sql_wo['Clear_Time_dt'] = pd.to_datetime(df_sql_wo['Clear_Time'], errors='coerce')
df_sql_wo['Downtime_Hours'] = (df_sql_wo['Clear_Time_dt'] - df_sql_wo['Raise_Time_dt']).dt.total_seconds() / 3600

# --- 1. By Site_ID: Max WO Count & Shortest Avg Duration (ignore STD_RFO) ---
wo_by_site = df_sql_wo.groupby('Site_ID').agg(
    WO_Count=('Site_ID', 'count'),
    Total_Duration_Hours=('Downtime_Hours', 'sum'),
    Avg_Duration_Hours=('Downtime_Hours', 'mean')
).reset_index()

# MTBF by Site_ID (ignore STD_RFO)
def calc_mtbf_site(group):
    times = group['Raise_Time_dt'].sort_values().dropna()
    if len(times) > 1:
        intervals = times.diff().dt.total_seconds().dropna() / 3600
        return intervals.mean()
    return np.nan

mtbf_by_site = df_sql_wo.groupby('Site_ID').apply(calc_mtbf_site).reset_index(name='MTBF_Hours')
wo_by_site = pd.merge(wo_by_site, mtbf_by_site, on='Site_ID', how='left')

# --- Helper: Matplotlib Figure to Base64 ---
# Function to convert a matplotlib figure to a base64 encoded PNG image for embedding in HTML.
def fig_to_base64img(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight') # Save the figure to a bytes buffer.
    buf.seek(0) # Reset buffer position to the beginning.
    img_base64 = base64.b64encode(buf.read()).decode('utf-8') # Encode to base64.
    plt.close(fig) # Close the figure to free up memory.
    return img_base64

# --- Plots for Site_ID (ignore STD_RFO) ---
# Top 10 by WO Count
top_sites_count = wo_by_site.sort_values('WO_Count', ascending=False).head(10)
fig1, ax1 = plt.subplots(figsize=(12, 6))  # Slightly bigger
colors1 = sns.color_palette("flare", len(top_sites_count))
ax1.bar(top_sites_count['Site_ID'].astype(str), top_sites_count['WO_Count'], color=colors1)
ax1.set_title('Top 10 Sites by WO Count', fontsize=15, color="#1976d2")
ax1.set_xlabel('Site ID', fontsize=12)
ax1.set_ylabel('WO Count', fontsize=12)
ax1.tick_params(axis='x', labelsize=11)
ax1.tick_params(axis='y', labelsize=11)
for i, v in enumerate(top_sites_count['WO_Count']):
    ax1.text(i, v + 0.2, str(int(v)), ha='center', va='bottom', fontsize=10)
fig1.tight_layout()
img_top_sites_count = fig_to_base64img(fig1)

# Top 10 by Shortest Avg Duration
shortest_sites = wo_by_site[wo_by_site['Avg_Duration_Hours'].notna()].sort_values('Avg_Duration_Hours').head(10)
fig2, ax2 = plt.subplots(figsize=(12, 6))  # Slightly bigger
colors2 = sns.color_palette("crest", len(shortest_sites))
ax2.bar(shortest_sites['Site_ID'].astype(str), shortest_sites['Avg_Duration_Hours'], color=colors2)
ax2.set_title('Top 10 Sites by Shortest Avg Duration', fontsize=15, color="#388e3c")
ax2.set_xlabel('Site ID', fontsize=12)
ax2.set_ylabel('Avg Duration (Hours)', fontsize=12)
ax2.tick_params(axis='x', labelsize=11)
ax2.tick_params(axis='y', labelsize=11)
for i, v in enumerate(shortest_sites['Avg_Duration_Hours']):
    ax2.text(i, v + 0.2, f"{v:.1f}", ha='center', va='bottom', fontsize=10)
fig2.tight_layout()
img_shortest_sites = fig_to_base64img(fig2)

# Top 10 by MTBF (lowest to largest)
top_mtbf_sites = wo_by_site[wo_by_site['MTBF_Hours'].notna()].sort_values('MTBF_Hours', ascending=True).head(10)
fig3, ax3 = plt.subplots(figsize=(13, 6))  # Slightly bigger
colors3 = sns.color_palette("mako", len(top_mtbf_sites))
ax3.scatter(top_mtbf_sites['Site_ID'].astype(str), top_mtbf_sites['MTBF_Hours'], color=colors3, s=140, edgecolor="#1976d2")
ax3.set_title('Top 10 Sites by MTBF (Lowest to Largest)', fontsize=15, color="#1976d2")
ax3.set_xlabel('Site ID', fontsize=12)
ax3.set_ylabel('MTBF (Hours)', fontsize=12)
ax3.tick_params(axis='x', labelsize=11)
ax3.tick_params(axis='y', labelsize=11)
for i, (x, y) in enumerate(zip(top_mtbf_sites['Site_ID'], top_mtbf_sites['MTBF_Hours'])):
    ax3.text(i, y + 0.2, f"{y:.1f}", ha='center', va='bottom', fontsize=10)
fig3.tight_layout()
img_top_mtbf_sites = fig_to_base64img(fig3)

# --- 2. By STD_RFO: Prolonging to Repair (MTTR) & Frequency (MTBF) ---
# Try to find the correct column name for STD_RFO (case-insensitive, partial match)
std_rfo_col = None
for col in df_sql_wo.columns:
    if col.lower() == 'std_rfo' or col.lower() == 'std_rfos' or 'std_rfo' in col.lower():
        std_rfo_col = col
        break

if std_rfo_col:
    # MTTR by STD_RFO (top 10)
    mttr_by_rfo = df_sql_wo.groupby(std_rfo_col)['Downtime_Hours'].mean().sort_values(ascending=False).head(10)
    fig4, ax4 = plt.subplots(figsize=(14, 7))  # Bigger
    colors4 = sns.color_palette("rocket", len(mttr_by_rfo))
    ax4.bar(mttr_by_rfo.index.astype(str), mttr_by_rfo.values, color=colors4)
    ax4.set_title('Top 10 STD_RFO by MTTR (Prolonging to Repair)', fontsize=16, color="#d32f2f")
    ax4.set_xlabel('STD_RFO', fontsize=13)
    ax4.set_ylabel('Avg Duration (Hours)', fontsize=13)
    ax4.tick_params(axis='x', labelsize=12, rotation=60)  # Vertical/readable
    ax4.tick_params(axis='y', labelsize=12)
    for i, v in enumerate(mttr_by_rfo.values):
        ax4.text(i, v + 0.2, f"{v:.1f}", ha='center', va='bottom', fontsize=11)
    fig4.tight_layout()
    img_mttr_rfo = fig_to_base64img(fig4)

    # MTBF by STD_RFO (top 10 frequent, i.e., shortest MTBF)
    def calc_mtbf_rfo(group):
        times = group['Raise_Time_dt'].sort_values().dropna()
        if len(times) > 1:
            intervals = times.diff().dt.total_seconds().dropna() / 3600
            return intervals.mean()
        return np.nan
    mtbf_by_rfo = df_sql_wo.groupby(std_rfo_col).apply(calc_mtbf_rfo).dropna().sort_values().head(10)
    fig5, ax5 = plt.subplots(figsize=(14, 7))  # Bigger
    colors5 = sns.color_palette("icefire", len(mtbf_by_rfo))
    ax5.scatter(mtbf_by_rfo.index.astype(str), mtbf_by_rfo.values, color=colors5, s=140, edgecolor="#d32f2f")
    ax5.set_title('Top 10 STD_RFO by Frequency (Shortest MTBF)', fontsize=16, color="#d32f2f")
    ax5.set_xlabel('STD_RFO', fontsize=13)
    ax5.set_ylabel('MTBF (Hours)', fontsize=13)
    ax5.tick_params(axis='x', labelsize=12, rotation=60)  # Vertical/readable
    ax5.tick_params(axis='y', labelsize=12)
    for i, v in enumerate(mtbf_by_rfo.values):
        ax5.text(i, v + 0.2, f"{v:.1f}", ha='center', va='bottom', fontsize=11)
    fig5.tight_layout()
    img_mtbf_rfo = fig_to_base64img(fig5)
else:
    img_mttr_rfo = None
    img_mtbf_rfo = None

# --- Popup HTML for charts ---
popup_htmls = []
def make_popup_html(img, title, popup_id, color="#1976d2"):
    return f"""
    <button onclick="document.getElementById('{popup_id}').style.display='block';" style="background:{color};color:#fff;padding:7px 18px;border:none;border-radius:6px;cursor:pointer;font-size:1rem;margin:10px 0;">Show {title}</button>
    <div id="{popup_id}" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.25); z-index:9999;">
        <div style="background:#fff; margin:40px auto; padding:25px; border-radius:10px; max-width:900px; min-width:320px; position:relative; overflow-y: auto; max-height: calc(100vh - 80px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); border:2px solid {color};">
            <button onclick="document.getElementById('{popup_id}').style.display='none'" style="position:absolute; top:8px; right:8px; font-size:1.1em; background:none; border:none; cursor:pointer; color:#888;">✖</button>
            <h2 style="color:{color}; font-size:1.2rem; margin-bottom:0.5em;">{title}</h2>
            <img src="data:image/png;base64,{img}" style="max-width:100%;border:1px solid {color};margin:10px 0;">
        </div>
    </div>
    """

popup_htmls.append(make_popup_html(img_top_sites_count, "Top 10 Sites by WO Count", "popup_top_sites_count", "#1976d2"))
popup_htmls.append(make_popup_html(img_shortest_sites, "Top 10 Sites by Shortest Avg Duration", "popup_shortest_sites", "#388e3c"))
popup_htmls.append(make_popup_html(img_top_mtbf_sites, "Top 10 Sites by MTBF (Lowest to Largest)", "popup_top_mtbf_sites", "#1976d2"))
if img_mttr_rfo:
    popup_htmls.append(make_popup_html(img_mttr_rfo, "Top 10 STD_RFO by MTTR", "popup_mttr_rfo", "#d32f2f"))
if img_mtbf_rfo:
    popup_htmls.append(make_popup_html(img_mtbf_rfo, "Top 10 STD_RFO by Frequency (Shortest MTBF)", "popup_mtbf_rfo", "#d32f2f"))

# --- Aggregated WO Stats Table (by Site_ID and STD_RFO) ---
if std_rfo_col:
    wo_grouped_table = df_sql_wo.groupby(['Site_ID', std_rfo_col]).agg(
        WO_Count=('Site_ID', 'count'),
        Total_Duration_Hours=('Downtime_Hours', 'sum'),
        Avg_Duration_Hours=('Downtime_Hours', 'mean')
    ).reset_index()
    wo_grouped_table_html = wo_grouped_table.to_html(
        index=False, float_format='%.2f', escape=False, classes="styled-table", border=0
    )
else:
    wo_grouped_table_html = "<i>No STD_RFO data available for grouping.</i>"

# --- HTML Block for WO Analysis ---
wo_analysis_html = f"""
<hr>
<h3 style="color:#1976d2; font-size:1.1rem;">🛠️ Work Order File Analysis (Site & STD_RFO)</h3>
<ul style="font-size:0.95rem;">
    <li><b>Total Distinct Site IDs:</b> {total_distinct_sites}</li>
</ul>
<h4>Aggregated WO Stats by Site ID and STD_RFO</h4>
<div style="max-height:350px;overflow:auto;">
{wo_grouped_table_html}
</div>
<h4>Charts (Click to Expand)</h4>
{''.join(popup_htmls)}
<p style="font-size:0.9rem;"><em>Interpretation:</em> These charts and tables help identify sites or root causes with frequent or long-duration outages, and the relationship between repair time and failure frequency. Click on each chart for a larger view.</p>
<hr>
"""

# --- MTTR, MTBF, and WO Analysis using df_sql_wo (summary block) ---
mttr = df_sql_wo['Downtime_Hours'].mean()
mttr_str = f"{mttr:.2f} hours" if not np.isnan(mttr) else "N/A"

mtbf_list = []
for site_id, group in df_sql_wo.groupby('Site_ID'):
    times = group['Raise_Time_dt'].sort_values().dropna()
    if len(times) > 1:
        intervals = times.diff().dt.total_seconds().dropna() / 3600
        mtbf_list.extend(intervals.tolist())
mtbf = np.mean(mtbf_list) if mtbf_list else np.nan
mtbf_str = f"{mtbf:.2f} hours" if not np.isnan(mtbf) else "N/A"

wo_count = len(df_sql_wo)

mttr_mtbf_html = f"""
{wo_analysis_html}
<h3 style="color:#1976d2; font-size:1.1rem;">🛠️ Work Order Analysis (MTTR & MTBF)</h3>
<ul style="font-size:0.95rem;">
    <li><b>Total Work Orders (WO):</b> {wo_count}</li>
    <li><b>Mean Time To Repair (MTTR):</b> {mttr_str}</li>
    <li><b>Mean Time Between Failures (MTBF):</b> {mtbf_str}</li>
</ul>
<p style="font-size:0.9rem;"><em>Interpretation:</em> MTTR reflects the average time to resolve incidents, while MTBF indicates the average interval between failures. High MTTR or low MTBF in specific root causes or sites highlights areas for process improvement and preventive maintenance focus.</p>
<hr>
"""

# Patch: Insert the MTTR/MTBF HTML into the detail_analysis_report_html after the first <hr>
if 'detail_analysis_report_html' not in locals():
    detail_analysis_report_html = ""
detail_analysis_report_html = re.sub(
    r'(<hr>)',
    r'\1' + mttr_mtbf_html,
    detail_analysis_report_html,
    count=1
)

# --- ATTRACTIVE DATAFRAME/DATATABLE VIEWER FOR ALL DATAFRAMES ---

# --- Data Preparation ---
# Filter out rows where 'Render' is '!SWO' as they are not relevant for the main analysis.
df_filtered = df[df['Render'] != '!SWO'].copy() # Use .copy() to prevent SettingWithCopyWarning

# Prepare a dictionary of all main dataframes to show
dataframe_dict = {
    "Detail Data (df_filtered)": df_filtered,
    "SQL Data (df_sql)": df_sql,
    "BKD Summary (df_sql_bkd)": df_sql_bkd,
    "WO File (df_sql_wo)": df_sql_wo,
}

# Generate HTML for each dataframe (first 100 rows for performance)
dataframe_tabs = []
dataframe_contents = []
for idx, (df_name, df_obj) in enumerate(dataframe_dict.items()):
    safe_id = f"df_tab_{idx}"
    # Use DataTables for interactivity, limit to 100 rows for speed
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



# Add a floating button to open the dataframe viewer
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
    <h2 style="color:#1976d2;">🗂️ DataFrame Explorer</h2>
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
<script>
document.addEventListener("DOMContentLoaded", function() {{
    // Floating button opens modal
    document.getElementById('openDfViewerBtn').onclick = function() {{
        document.getElementById('dfViewerModal').style.display = 'block';
        // Show first tab by default
        var firstTab = document.querySelector('.df-tab-btn');
        if (firstTab) firstTab.click();
    }};
    // Tab switching for dataframes
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
                // Initialize DataTable if not already
                var table = tabContent.querySelector('table');
                if (table && !$.fn.DataTable.isDataTable(table)) {{
                    $(table).DataTable({{
                        scrollX: true,
                        pageLength: 15,
                        lengthMenu: [ [10, 15, 25, 50, -1], [10, 15, 25, 50, "All"] ],
                        dom: 'lBfrtip',
                        buttons: ['excel', 'print']
                    }});
                }}
            }}
        }};
    }});
}});
</script>
<style>
#openDfViewerBtn:hover {{
    background: linear-gradient(90deg,#42a5f5 60%,#1976d2 100%);
    box-shadow: 0 8px 32px rgba(25,118,210,0.28);
}}
.df-tab-bar {{
    border-bottom: 2px solid #e3f2fd;
    padding-bottom: 4px;
}}
.df-tab-btn {{
    background: #e3f2fd;
    color: #1976d2;
    border: none;
    border-radius: 6px 6px 0 0;
    padding: 7px 18px;
    font-size: 1em;
    cursor: pointer;
    font-weight: 500;
    transition: background 0.2s, color 0.2s;
}}
.df-tab-btn.active, .df-tab-btn:hover {{
    background: #1976d2;
    color: #fff;
}}
.df-tab-content {{
    display: none;
    animation: fadeIn 0.3s;
}}
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(10px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.attractive-df-table {{
    font-size: 0.93em;
    border-radius: 7px;
    box-shadow: 0 2px 8px rgba(25,118,210,0.07);
    background: #f9fbfd;
}}
</style>
"""

# The insertion of the dataframe viewer floating button/modal is handled later in the script.
# No need to insert it here to avoid errors or duplicate insertion.

# Patch: Insert the MTTR/MTBF HTML into the detail_analysis_report_html after the first <hr>
# Ensure detail_analysis_report_html is initialized before use
if 'detail_analysis_report_html' not in locals():
    detail_analysis_report_html = ""
detail_analysis_report_html = re.sub(
    r'(<hr>)',
    r'\1' + mttr_mtbf_html,
    detail_analysis_report_html,
    count=1
)

# --- Data Preparation ---
# Filter out rows where 'Render' is '!SWO' as they are not relevant for the main analysis.
df_filtered = df[df['Render'] != '!SWO'].copy() # Use .copy() to prevent SettingWithCopyWarning
# Extract unique 'Render' and 'State/Division' types for dynamic filtering and tab generation.
render_types = df_filtered['Render'].dropna().unique().tolist()
state_filters = df_filtered['State/Division'].dropna().unique().tolist()

# Ensure 'Render' column in df_sql has no missing values for consistent pivot table operations.
df_sql = df_sql[df_sql['Render'].notna()].copy() # Use .copy()

# Add 'Date' column from 'Raise Time' to df_filtered for temporal analysis, coercing errors to NaT.
df_filtered['Raise Time_dt'] = pd.to_datetime(df_filtered['Raise Time'], errors='coerce')


# --- Pivot Tables for SQL Data (based on df_sql) ---
# Calculate average CA_Result by Sub_Office and WeekNumber.
pivot_avg_ca = df_sql.pivot_table(
    index='Sub_Office', columns='WeekNumber', values='CA_Result', aggfunc='mean'
).round(2)
# Calculate unique Site_ID counts by Render, CA_Range, and WeekNumber.
pivot_count = df_sql.pivot_table(
    index=['Render', 'CA_Range'], columns='WeekNumber', values='Site_ID',
    aggfunc=pd.Series.nunique, fill_value=0
)
# Calculate average CA_Result by Township and MonthName, ordering months.
pivot_township_month = df_sql.pivot_table(
    index='Township', columns='MonthName', values='CA_Result', aggfunc='mean'
).round(2)
month_order = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
pivot_township_month.columns = [col.upper() for col in pivot_township_month.columns]
ordered_cols = [m for m in month_order if m in pivot_township_month.columns]
pivot_township_month = pivot_township_month[ordered_cols] # Reorder columns based on calendar months.

# Calculate average CA_Result by Sub_Office and MonthName.
pivot_suboffice_month = df_sql.pivot_table(
    index='Sub_Office', columns='MonthName', values='CA_Result', aggfunc='mean'
).round(2)
# Calculate average CA_Result by WeekNumber and Render.
pivot_week_render = df_sql.pivot_table(
    index='WeekNumber', columns='Render', values='CA_Result', aggfunc='mean'
).round(2)

# --- Site Status Summary Table (based on df_filtered) ---
group_cols = ['Render', 'State/Division', 'Sub Office', 'Township']

# Calculate total unique sites for each group.
total_sites = df_filtered.groupby(group_cols)['Site ID'].nunique().reset_index(name='Total Sites')
# Calculate unique sites that are currently 'down' (i.e., 'Raise Time' is not 'Active' or is null).
down_sites = df_filtered[
    df_filtered['Raise Time'].isnull() | (df_filtered['Raise Time'] != 'Active')
].groupby(group_cols)['Site ID'].nunique().reset_index(name='Current Down Site')
# Calculate unique sites that are 'online' (i.e., 'Raise Time' is 'Active').
online_sites = df_filtered[
    df_filtered['Raise Time'] == 'Active'
].groupby(group_cols)['Site ID'].nunique().reset_index(name='Online Status')

# Merge the summary statistics into a single DataFrame.
summarise = total_sites.merge(down_sites, on=group_cols, how='left')
summarise = summarise.merge(online_sites, on=group_cols, how='left')
# Fill any NaN values with 0 and convert relevant columns to integer type.
summarise = summarise.fillna(0).astype({'Current Down Site': int, 'Online Status': int})
# Calculate the effectiveness percentage based on online sites vs. total sites.
summarise['effectiveness (%)'] = (summarise['Online Status'] / summarise['Total Sites'] * 100).round(2)

# Pivot the summarized data for display in the main report, aggregating by sum.
pivot_status = summarise.pivot_table(
    index=['Render', 'State/Division', 'Sub Office', 'Township'],
    values=['Total Sites', 'Current Down Site', 'Online Status', 'effectiveness (%)'],
    aggfunc='sum',
    fill_value=0
)

# Define a highlighting function for rows based on 'Current Down Site' vs 'Online Status'.
def highlight_down_row(row):
    # Highlight with yellow background and red font if Current Down Site is significantly higher than Online Status.
    color = 'background-color: #ffe066; color: red; font-weight: bold;' if row['Current Down Site'] > 1.5 * row['Online Status'] else ''
    return [
        '',      # Total Sites (no highlight)
        color,   # Current Down Site (conditional highlight)
        ''       # Online Status (no highlight)
    ]

# Define a highlighting function for effectiveness percentage.
def highlight_effectiveness(val):
    # Highlight green if effectiveness % is greater than 50%.
    try:
        # Handle string percentage values by removing '%' and converting to float.
        if isinstance(val, str) and '%' in val:
            val = float(val.replace('%', '').strip())
        elif isinstance(val, (int, float)):
            val = float(val) # Ensure it's a float for comparison.
        if val > 50:
            return 'background-color: #b6fcb6; color: #155724; font-weight: bold;'
    except Exception:
        pass # Gracefully handle conversion errors.
    return ''

# Apply the defined styling functions to the pivot_status table.
styled_status = (
    pivot_status.style
    .apply(highlight_down_row, axis=1, subset=['Total Sites', 'Current Down Site', 'Online Status'])
    .format({'effectiveness (%)': '{:.2f}%'}) # Format effectiveness as percentage string.
    .applymap(highlight_effectiveness, subset=['effectiveness (%)'])
)

# --- NEW: Conditional Highlighting for Site Count Table (adding arrows for trends) ---
def highlight_site_count_tiers_row(row):
    """
    Adds up/down/flat arrows as text, comparing left-to-right (across columns),
    indicating trends in site counts.
    """
    new_row = row.copy()
    for i in range(1, len(row)):
        prev = row.iloc[i - 1]
        curr = row.iloc[i]
        if pd.isna(prev) or pd.isna(curr):
            continue # Skip if either value is missing.
        try:
            prev_val = float(prev)
            curr_val = float(curr)
        except ValueError: # Catch conversion errors.
            continue
        if curr_val > prev_val:
            new_row.iloc[i] = f"{curr} ↑" # Up arrow for increase.
        elif curr_val < prev_val:
            new_row.iloc[i] = f"{curr} ↓" # Down arrow for decrease.
        else:
            new_row.iloc[i] = f"{curr} →" # Right arrow for no change.
    return new_row

# Apply row-wise (axis=1) for trend indicators.
pivot_count_with_arrows = pivot_count.apply(highlight_site_count_tiers_row, axis=1)

# Define a function to color the trend arrows.
def color_arrows(val):
    if isinstance(val, str):
        if "↑" in val:
            return 'color: green; font-weight: bold;' # Green for positive trend.
        elif "↓" in val:
            return 'color: red; font-weight: bold;' # Red for negative trend.
        elif "→" in val:
            return 'color: gray; font-weight: bold;' # Gray for no change.
    return ''

# Apply the coloring to the arrow-annotated pivot table.
styled_pivot_count = pivot_count_with_arrows.style.applymap(color_arrows)

# Define function to add arrows to average CA results by week.
def highlight_avg_ca_week_row(row):
    new_row = row.copy()
    for i in range(1, len(row)):
        prev = row.iloc[i - 1]
        curr = row.iloc[i]
        if pd.isna(prev) or pd.isna(curr):
            continue
        try:
            prev_val = float(prev)
            curr_val = float(curr)
        except ValueError:
            continue
        if curr_val > prev_val:
            new_row.iloc[i] = f"{curr:.2f} ↑"
        elif curr_val < prev_val:
            new_row.iloc[i] = f"{curr:.2f} ↓"
        else:
            new_row.iloc[i] = f"{curr:.2f} →"
    # Format the first column to two decimal places as well.
    if pd.notna(row.iloc[0]):
        try:
            new_row.iloc[0] = f"{float(row.iloc[0]):.2f}"
        except ValueError:
            pass
    return new_row

pivot_avg_ca_with_arrows = pivot_avg_ca.apply(highlight_avg_ca_week_row, axis=1)

def color_arrows_avg_ca(val):
    if isinstance(val, str):
        if "↑" in val:
            return 'color: green; font-weight: bold;'
        elif "↓" in val:
            return 'color: red; font-weight: bold;'
        elif "→" in val:
            return 'color: gray; font-weight: bold;'
    return ''

styled_pivot_avg_ca = pivot_avg_ca_with_arrows.style.applymap(color_arrows_avg_ca)

# Add arrows row-wise for CA trends by township/month.
def highlight_ca_township_month_row(row):
    new_row = row.copy()
    # Format all values to 2 decimals as string.
    for i in range(len(row)):
        val = row.iloc[i]
        if pd.notna(val):
            try:
                new_row.iloc[i] = f"{float(val):.2f}"
            except ValueError:
                pass
    # Add arrows based on comparison with previous month.
    for i in range(1, len(row)):
        prev = row.iloc[i - 1]
        curr = row.iloc[i]
        try:
            prev_val = float(prev)
            curr_val = float(curr)
        except ValueError:
            continue
        if pd.isna(prev_val) or pd.isna(curr_val):
            continue
        if curr_val > prev_val:
            new_row.iloc[i] = f"{new_row.iloc[i]} ↑"
        elif curr_val < prev_val:
            new_row.iloc[i] = f"{new_row.iloc[i]} ↓"
        else:
            new_row.iloc[i] = f"{new_row.iloc[i]} →"
    return new_row

pivot_township_month_with_arrows = pivot_township_month.apply(highlight_ca_township_month_row, axis=1)


def color_arrows_township(val):
    if isinstance(val, str):
        if "↑" in val:
            return 'color: green; font-weight: bold;'
        elif "↓" in val:
            return 'color: red; font-weight: bold;'
        elif "→" in val:
            return 'color: gray; font-weight: bold;'
    return ''

styled_pivot_township_month = pivot_township_month_with_arrows.style.applymap(color_arrows_township)

# --- Helper: Matplotlib Figure to Base64 ---
# Function to convert a matplotlib figure to a base64 encoded PNG image for embedding in HTML.
def fig_to_base64img(fig):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", bbox_inches='tight') # Save the figure to a bytes buffer.
    buf.seek(0) # Reset buffer position to the beginning.
    img_base64 = base64.b64encode(buf.read()).decode('utf-8') # Encode to base64.
    plt.close(fig) # Close the figure to free up memory.
    return img_base64

# --- Generate Performance Overview Figures ---
sns.set(style="whitegrid") # Set seaborn style for plots.
pivot_week_render_reset = pivot_week_render.reset_index()

# 1. Line plot: Average CA by Week and Render
fig1, ax1 = plt.subplots(figsize=(14, 6))
for render in pivot_week_render.columns:
    ax1.plot(pivot_week_render_reset['WeekNumber'], pivot_week_render_reset[render], marker='o', label=render)
    # Add data labels to each point on the line chart.
    for x, y in zip(pivot_week_render_reset['WeekNumber'], pivot_week_render_reset[render]):
        if not pd.isna(y):
            ax1.text(x, y + 1, f"{y:.2f}", ha='center', va='bottom', fontsize=8, color='gray')
ax1.set_title('Average CA by Week and Render', fontsize=12)
ax1.set_xlabel('Week Number', fontsize=10)
ax1.set_ylabel('AVG CA', fontsize=10)
ax1.set_xticks(pivot_week_render_reset['WeekNumber'])
ax1.set_xticklabels([f'W-{w}' for w in pivot_week_render_reset['WeekNumber']])
ax1.legend(title='Render', fontsize=9, title_fontsize=10)
ax1.tick_params(axis='x', labelsize=9)
ax1.tick_params(axis='y', labelsize=9)
fig1.tight_layout() # Adjust layout to prevent labels from overlapping.
img1 = fig_to_base64img(fig1)

# 2. Bar plot: Average CA by Sub Office and Month (months in calendar order)
# Ensure columns are uppercase and ordered correctly before plotting.
month_order = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC']
pivot_suboffice_month.columns = [col.upper() for col in pivot_suboffice_month.columns]
ordered_cols = [m for m in month_order if m in pivot_suboffice_month.columns]
pivot_suboffice_month = pivot_suboffice_month[ordered_cols]
fig2, ax2 = plt.subplots(figsize=(14, 6))
pivot_suboffice_month.plot(kind='bar', ax=ax2)
ax2.set_title('Average CA by Sub Office and Month', fontsize=12)
ax2.set_xlabel('Sub Office', fontsize=10)
ax2.set_ylabel('CA Result', fontsize=10)
ax2.set_xticklabels(pivot_suboffice_month.index, rotation=45, ha='right', fontsize=9)
ax2.legend(title='MonthName', fontsize=9, title_fontsize=10)
ax2.tick_params(axis='y', labelsize=9)
fig2.tight_layout()
img2 = fig_to_base64img(fig2)

# 3. Daily CA bar chart with colors representing months.
df_sql['Date'] = pd.to_datetime(df_sql['Date']) # Convert 'Date' column to datetime objects.
daily_avg = df_sql.groupby('Date')['CA_Result'].mean().reset_index()
daily_avg['MonthName'] = daily_avg['Date'].dt.strftime('%b').str.upper() # Extract month name for coloring.
month_colors = {'JAN': '#1f77b4', 'FEB': '#ff7f0e', 'MAR': '#2ca02c', 'APR': '#d62728', 'MAY': '#9467bd'} # Define colors for months.
colors = daily_avg['MonthName'].map(month_colors).fillna('#CCCCCC') # Map month names to colors, use gray for unmapped.
fig3, ax3 = plt.subplots(figsize=(18, 7))
bars = ax3.bar(daily_avg['Date'], daily_avg['CA_Result'], color=colors, width=0.8)
# Add data labels on top of each bar.
for bar, val in zip(bars, daily_avg['CA_Result']):
    ax3.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.5, f"{val:.2f}",
             ha='center', va='bottom', fontsize=8, rotation=45, color='gray')
ax3.set_title('AVG CA by Date', fontsize=12)
ax3.set_xlabel('Date', fontsize=10)
ax3.set_ylabel('AVG CA', fontsize=10)
# Set x-ticks to display dates at reasonable intervals.
ax3.set_xticks(daily_avg['Date'][::max(1, len(daily_avg)//20)])
ax3.set_xticklabels([d.strftime('%Y-%m-%d') for d in daily_avg['Date'][::max(1, len(daily_avg)//20)]],
                            rotation=60, ha='right', fontsize=8)
# Create custom legend handles for month colors.
handles = [mpatches.Patch(color=clr, label=mn.title()) for mn, clr in month_colors.items()]
ax3.legend(handles=handles, title='MonthName', fontsize=9, title_fontsize=10)
ax3.tick_params(axis='y', labelsize=9)
fig3.tight_layout()
img3 = fig_to_base64img(fig3)

# 4. Arrow trends in table (visualizing week-over-week changes).
def add_arrow(val):
    if pd.isna(val): return ""
    arrow = "↑" if val > 0 else "↓" if val < 0 else "→" # Determine arrow based on value change.
    color = "green" if val > 0 else "red" if val < 0 else "gray" # Color arrow based on trend.
    # Return HTML string with formatted value and colored arrow.
    return f'{val:.2f} <span style="font-weight:bold; font-size:1.5em; color:{color};">{arrow}</span>'
pivot_with_arrows = pivot_week_render.copy()
# Calculate week-over-week difference and apply arrow formatting.
for col in pivot_with_arrows.columns:
    pivot_with_arrows[col] = pivot_with_arrows[col].diff().fillna(0).apply(add_arrow)


# --- Author Info HTML Block ---
# HTML for a fixed author information box, with a toggle function.
author_box_html = """
<div id="authorBox" style="
    position: fixed;
    top: 15px;
    right: 15px;
    background: #f9f9f9;
    border: 1px solid #ccc;
    padding: 8px 12px; /* Reduced padding */
    border-radius: 6px;
    font-family: 'Inter', sans-serif;
    font-size: 0.75rem; /* Reduced font size using rem */
    color: #333;
    z-index: 1000;
    box-shadow: 0 0 5px rgba(0,0,0,0.1);
    max-width: 200px; /* Adjusted max-width */
">
    <div style="display: flex; justify-content: space-between; align-items: center;">
        <strong>📊 Kaung Myat Kyaw</strong>
        <button onclick="toggleAuthorBox()" style="
            background: none;
            border: none;
            font-size: 0.65rem; /* Reduced font size using rem */
            cursor: pointer;
            color: #666;
            margin-left: 8px;
        " title="Hide">✖</button>
    </div>
    <em>Data Analyst</em>
</div>
<script>
function toggleAuthorBox() {
    var box = document.getElementById('authorBox');
    box.style.display = box.style.display === 'none' ? 'block' : 'none';
}
</script>
"""

# --- Prepare df_filtered to an HTML table string for DataTables ---
# Convert df_filtered DataFrame to an HTML table string.
df_filtered_html = df_filtered.to_html(
    index=False,
    classes="display nowrap", # 'display' for DataTables default styling, 'nowrap' for no text wrapping.
    table_id="detailDataTable", # Unique ID for DataTables to target.
    escape=False # Allows HTML content in cells, e.g., for Site IDs in future.
)

# --- NEW: Detail Data Table Modal HTML ---
# This modal will replace the separate detail_data_page.html
detail_data_modal_html = f"""
<div id="detailDataModal" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.25); z-index:9999;">
  <div style="background:#fff; margin:40px auto; padding:25px; border-radius:10px; max-width:1100px; min-width:350px; position:relative; overflow-y: auto; max-height: calc(100vh - 80px); box-shadow: 0 5px 15px rgba(0,0,0,0.3);">
    <button onclick="document.getElementById('detailDataModal').style.display='none'" style="position:absolute; top:8px; right:8px; font-size:1.1em; background:none; border:none; cursor:pointer; color:#888;">✖</button>
    <h2>🗃️ Detail Data Table (Interactive)</h2>
    <p>This interactive table provides advanced search, filtering, and pagination for detailed data.</p>
    <div class="column-filters-container" id="detail-column-filters">
        <!-- Column filter dropdowns will be inserted here by JavaScript -->
        <label>Render: <select class="column-filter-select" data-column-name="Render"><option value="">All</option></select></label>
        <label>State/Division: <select class="column-filter-select" data-column-name="State/Division"><option value="">All</option></select></label>
        <label>Sub Office: <select class="column-filter-select" data-column-name="Sub Office"><option value="">All</option></select></label>
        <label>Township: <select class="column-filter-select" data-column-name="Township"><option value="">All</option></select></label>
        <label>Issue Identity: <select class="column-filter-select" data-column-name="Issue Identity"><option value="">All</option></select></label>
    </div>
    <div class="container" style="overflow-x: auto;">
        {df_filtered_html}
    </div>
  </div>
</div>
"""


# --- Slicer HTML (needs `summarise` data for JS) ---
# Serialize the 'summarise' DataFrame to JSON for use in JavaScript.
summarise_json = summarise.to_dict(orient='records')
summarise_json_str = json.dumps(summarise_json, ensure_ascii=False)

# HTML structure for the interactive slicer modal, including a chart.
slicer_html = f"""
<button id="openSlicerBtn" style="margin:20px 0; padding:8px 20px; font-size:1em; background:#e3f2fd; border: none; border-radius: 5px; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">🔎 Open Interactive Slicer Dashboard</button>
<div id="slicerModal" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.25); z-index:9999;">
  <div style="background:#fff; margin:40px auto; padding:25px; border-radius:10px; max-width:1000px; min-width:350px; position:relative; overflow-y: auto; max-height: calc(100vh - 80px); box-shadow: 0 5px 15px rgba(0,0,0,0.3);">
    <button onclick="document.getElementById('slicerModal').style.display='none'" style="position:absolute; top:8px; right:8px; font-size:1.1em; background:none; border:none; cursor:pointer; color:#888;">✖</button>
    <h2>📊 Interactive Site Status Slicer</h2>
    <label for="slicerSelect" style="font-size:0.9rem;"><b>Group by:</b></label>
    <select id="slicerSelect" style="margin:0 8px 15px 8px; font-size:0.9rem; padding: 4px; border-radius: 4px; border: 1px solid #ccc;">
      <option value="Render">Render</option>
      <option value="State/Division">State/Division</option>
      <option value="Sub Office">Sub Office</option>
      <option value="Township">Township</option>
    </select>
    <div id="slicerTableDiv" style="max-height: 250px; overflow-y: auto;"></div>
    <canvas id="slicerChart" width="900" height="300" style="margin-top:25px;"></canvas>
  </div>
</div>
"""

# --- NEW: arnd_summarise for the Active Render Focus slicer ---
# Filter df_filtered to include only rows where 'Render' is 'active' (case-insensitive).
arnd_filtered_df = df_filtered[df_filtered['Render'].str.lower() == 'active'].copy()

# Calculate total, down, and online sites specifically for 'Active' render.
arnd_total_sites = arnd_filtered_df.groupby(group_cols)['Site ID'].nunique().reset_index(name='Total Sites')
arnd_down_sites = arnd_filtered_df[
    arnd_filtered_df['Raise Time'].isnull() | (arnd_filtered_df['Raise Time'] != 'Active')
].groupby(group_cols)['Site ID'].nunique().reset_index(name='Current Down Site')
arnd_online_sites = arnd_filtered_df[
    arnd_filtered_df['Raise Time'] == 'Active'
].groupby(group_cols)['Site ID'].nunique().reset_index(name='Online Status')

# Merge and calculate effectiveness for 'Active' render.
arnd_summarise = arnd_total_sites.merge(arnd_down_sites, on=group_cols, how='left')
arnd_summarise = arnd_summarise.merge(arnd_online_sites, on=group_cols, how='left')
arnd_summarise = arnd_summarise.fillna(0).astype({'Current Down Site': int, 'Online Status': int})
arnd_summarise['effectiveness (%)'] = (arnd_summarise['Online Status'] / arnd_summarise['Total Sites'] * 100).round(2)

# Serialize for JavaScript use.
arnd_summarise_json = arnd_summarise.to_dict(orient='records')
arnd_summarise_json_str = json.dumps(arnd_summarise_json, ensure_ascii=False)


# HTML structure for the Active Render Focus slicer modal.
arnd_slicer_html = f"""
<button id="openArndSlicerBtn" style="margin:20px 0; padding:8px 20px; font-size:1em; background:#e3f2fd; border: none; border-radius: 5px; cursor: pointer; box-shadow: 0 2px 5px rgba(0,0,0,0.1);">👷 Active_Render_Focus</button>
<div id="arndSlicerModal" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.25); z-index:9999;">
  <div style="background:#fff; margin:40px auto; padding:25px; border-radius:10px; max-width:1000px; min-width:350px; position:relative; overflow-y: auto; max-height: calc(100vh - 80px); box-shadow: 0 5px 15px rgba(0,0,0,0.3);">
    <button onclick="document.getElementById('arndSlicerModal').style.display='none'" style="position:absolute; top:8px; right:8px; font-size:1.1em; background:none; border:none; cursor:pointer; color:#888;">✖</button>
    <h2>👷 Active Render Only</h2>
    <label for="arndSlicerSelect" style="font-size:0.9rem;"><b>Group by:</b></label>
    <select id="arndSlicerSelect" style="margin:0 8px 15px 8px; font-size:0.9rem; padding: 4px; border-radius: 4px; border: 1px solid #ccc;">
      <option value="State/Division">State/Division</option>
      <option value="Sub Office">Sub Office</option>
      <option value="Township">Township</option>
    </select>
    <div id="arndSlicerTableDiv" style="max-height: 250px; overflow-y: auto;"></div>
    <canvas id="arndSlicerChart" width="900" height="300" style="margin-top:25px;"></canvas>
  </div>
</div>
"""

# --- Build Tabbed HTML Report ---
# Initialize lists to store tab buttons and their corresponding content.
tab_buttons = []
tab_contents = []

# Generate tabs for each combination of Render type and State.
for render_type in render_types:
    for state in state_filters:
        # Filter data for the current render and state.
        filtered_df_tab = df_filtered[
            (df_filtered['Render'].str.lower() == render_type.lower()) &
            (df_filtered['State/Division'].str.lower() == state.lower())
        ].copy() # Use .copy() to ensure operations on this filtered DF don't warn.
        if filtered_df_tab.empty:
            continue # Skip if no data for this combination.

        sub_offices = filtered_df_tab['Sub Office'].unique()
        # Create a unique ID for the tab content div.
        section_id = f"{render_type}_{state}".replace(" ", "_").replace("/", "_") # Replace '/' as well for valid ID.
        tab_buttons.append(f'<button type="button" class="tablinks" data-tab="{section_id}">{render_type} | {state}</button>')

        # --- Executive Summary for the current tab ---
        issue_summary_all = []
        html_parts = []
        for sub_office in sub_offices:
            sub_sites = filtered_df_tab[filtered_df_tab['Sub Office'] == sub_office]
            num_sites = sub_sites.shape[0]
            if num_sites == 0:
                continue
            
            # CRITICAL FIX: Exclude 'Active' and 'PIC Finder is not Active' from issue counts.
            issue_counts = sub_sites[
                ~sub_sites['Issue Identity'].isin(['Active', 'PIC Finder is not Active'])
            ]['Issue Identity'].value_counts()
            
            issue_total = issue_counts.sum()
            top_issues = issue_counts.head(10).to_dict()
            note = f"{round(100 * issue_total / num_sites, 1)}% sites have issues"
            issue_summary_all.append({
                "Sub Office": sub_office,
                "Top Issues": ", ".join([f"{k} ({v})" for k, v in top_issues.items()]),
                "Total Issues": issue_total,
                "Note": note
            })

            issue_percent = (issue_counts / num_sites * 100).round(2)
            summary = pd.DataFrame({'Count': issue_counts, 'Percentage': issue_percent})
            # Generate HTML for site IDs within details/summary tags for expandability.
            newline_char = '\n'  # Define backslash outside f-string
            summary['Site IDs'] = summary.index.map(
                lambda x: f"<details><summary>Show Site IDs</summary><div style='white-space: normal;'>{textwrap.fill(', '.join(map(str, sub_sites.loc[sub_sites['Issue Identity'] == x, 'Site ID'].tolist())), 100).replace(newline_char, '<br>')}</div></details>"
            )
            html_parts.append(f"<h3>Sub Office: {sub_office}</h3>{summary.to_html(escape=False)}")

        executive_df = pd.DataFrame(issue_summary_all)
        executive_html_table = executive_df.to_html(index=False)
        executive_summary_html = f"""
        <h2>📌 Executive Summary</h2>
        <p>This section highlights top issues by sub-office excluding 'Active' status (which denotes online status, not an operational issue).</p>
        {executive_html_table}
        """

        # --- Chart for Executive Summary (Proportion of Issues) ---
        fig, ax = plt.subplots(figsize=(10, 6))
        sorted_df = executive_df.sort_values(by="Total Issues", ascending=True)
        colors = sns.color_palette("pastel", len(sorted_df)) # Use pastel colors for bars.
        sns.barplot(data=sorted_df, x="Total Issues", y="Sub Office", palette=colors, ax=ax)
        ax.set_title(f"📊 Proportion of Issues - {state} | {render_type}", fontsize=11)
        ax.set_xlabel("Total Issues (excluding 'Active' status)", fontsize=9) # Clarify xlabel.
        ax.set_ylabel("Sub Office", fontsize=9)
        ax.tick_params(axis='x', labelsize=8)
        ax.tick_params(axis='y', labelsize=8)
        # Add text labels on the bars.
        for i, v in enumerate(sorted_df["Total Issues"]):
            ax.text(v + 0.5, i, str(v), va='center', fontsize=8, color='black')
        plt.tight_layout()
        img_base64 = fig_to_base64img(fig)
        visuals_html = f"""
        <h2>📈 Visual Overview</h2>
        <img src="data:image/png;base64,{img_base64}" style="max-width:100%;border:1px solid #ccc;margin:20px 0;">
    """
        tab_contents.append(f"""
        <div id="{section_id}" class="tabcontent">
            <h2>{render_type} — {state}</h2>
            {executive_summary_html}
            {visuals_html}
            {"<br><br>".join(html_parts)}
        </div>
        """)

# --- Update Detail Data tab to open modal ---
# This button will now open the new modal.
detail_data_button = '<button type="button" class="tablinks" onclick="openDetailDataModal()">🗃️ Detail Data</button>'
detail_data_content = f"""
<div id="detail_data_tab" class="tabcontent">
    <h2>🗃️ Detail Data Table</h2>
    <p>Click the button below to open the interactive detail data table.</p>
    <button onclick="openDetailDataModal()" style="
        background: #4CAF50; /* Green */
        color: white;
        padding: 8px 12px; /* Adjusted padding */
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 0.9rem; /* Adjusted font size */
        margin-top: 10px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    ">Open Detail Data Table</button>
</div>
"""
tab_buttons.append(detail_data_button)
tab_contents.append(detail_data_content)


# --- NEW: Detail Data Analysis Tab ---
# Perform comprehensive analysis on df_filtered for the new report tab.
total_sites_detail = df_filtered.shape[0]

# 1. Top 5 Issue Identities (EXCLUDING 'Active' and 'PIC Finder is not Active')
top_issues_detail = df_filtered[
    ~df_filtered['Issue Identity'].isin(['Active', 'PIC Finder is not Active'])
]['Issue Identity'].value_counts().head(10) # Top 10 for more detailed insight.

top_issues_html = "<ul>"
if not top_issues_detail.empty:
    for issue, count in top_issues_detail.items():
        top_issues_html += f"<li><strong>{issue}:</strong> {count} instances</li>"
else:
    top_issues_html += "<li>No specific operational issues identified.</li>"
top_issues_html += "</ul>"

# 2. Issues by Render Type (Excluding 'Active' status)
issues_by_render = df_filtered[
    ~df_filtered['Issue Identity'].isin(['Active', 'PIC Finder is not Active'])
].groupby('Render')['Issue Identity'].value_counts().unstack(fill_value=0)
issues_by_render_html = issues_by_render.to_html(classes="styled-table", escape=False)

# 3. Sub Offices with most issues (excluding 'Active' status)
# CRITICAL FIX: Ensure 'PIC Finder is not Active' is also excluded here for consistency.
issues_per_suboffice = df_filtered[
    ~df_filtered['Issue Identity'].isin(['Active', 'PIC Finder is not Active'])
].groupby('Sub Office')['Issue Identity'].count().nlargest(5) # Top 5 now for better insight.

most_problematic_suboffices_html = "<ul>"
if not issues_per_suboffice.empty:
    for sub_office, count in issues_per_suboffice.items():
        most_problematic_suboffices_html += f"<li><strong>{sub_office}:</strong> {count} total issues</li>"
else:
    most_problematic_suboffices_html += "<li>No specific sub-offices with issues found (excluding 'Active' and 'PIC Finder is not Active').</li>"
most_problematic_suboffices_html += "</ul>"

# Chart for Geographical Hotspots (Sub-Offices)
fig_geo_hotspots, ax_geo_hotspots = plt.subplots(figsize=(10, 6))
if not issues_per_suboffice.empty:
    issues_per_suboffice_sorted = issues_per_suboffice.sort_values(ascending=True)
    sns.barplot(x=issues_per_suboffice_sorted.values, y=issues_per_suboffice_sorted.index, ax=ax_geo_hotspots, palette="viridis")
    ax_geo_hotspots.set_title('Top 5 Sub-Offices with Most Issues', fontsize=12)
    ax_geo_hotspots.set_xlabel('Number of Issues (excluding online status)', fontsize=10)
    ax_geo_hotspots.set_ylabel('Sub Office', fontsize=10)
    for i, v in enumerate(issues_per_suboffice_sorted.values):
        ax_geo_hotspots.text(v + 0.5, i, str(v), color='black', va='center', fontsize=8)
else:
    ax_geo_hotspots.text(0.5, 0.5, "No issue data to display for Sub-Offices.",
                         horizontalalignment='center', verticalalignment='center',
                         transform=ax_geo_hotspots.transAxes, fontsize=12, color='gray')
fig_geo_hotspots.tight_layout()
img_geo_hotspots = fig_to_base64img(fig_geo_hotspots)
geo_hotspots_chart_html = f"""
    <h3 style="color:#388e3c; font-size:1.1rem;">4. Geographical Hotspots: Sub-Offices Requiring Immediate Attention</h3>
    <p style="font-size:0.9rem;">Identifying the geographical areas with the highest concentration of non-active issues is vital for resource allocation:</p>
    {most_problematic_suboffices_html}
    <img src="data:image/png;base64,{img_geo_hotspots}" style="max-width:100%;border:1px solid #ccc;margin:10px 0;">
    <p style="font-size:0.9rem;"><em>Interpretation:</em> The bar chart visually emphasizes the sub-offices with the most significant operational bottlenecks. This direct visualization aids in rapid resource deployment decisions. Prioritizing these areas can lead to a quicker overall restoration of service efficiency and improved network stability.</p>
"""


# 4. Time-based analysis for 'Raise Time' (temporal trends in new issues)
# Filter for actual 'down' events: where Raise Time is a valid datetime and not 'Active' or 'PIC Finder is not Active'.
down_events = df_filtered[
    df_filtered['Raise Time_dt'].notna() &
    ~df_filtered['Issue Identity'].isin(['Active', 'PIC Finder is not Active'])
].copy()

# Count issues by month of 'Raise Time'.
issues_by_month = down_events['Raise Time_dt'].dt.to_period('M').value_counts().sort_index()

issues_by_month_html = "<ul>"
if not issues_by_month.empty:
    for month, count in issues_by_month.items():
        issues_by_month_html += f"<li><strong>{month.strftime('%Y-%m')}:</strong> {count} new issues</li>"
else:
    issues_by_month_html += "<li>No significant time-based issue trends observed in non-active issues.</li>"
issues_by_month_html += "</ul>"

# Chart for Temporal Trends (Cleaner Version)
import matplotlib.dates as mdates

fig_temporal_trends, ax_temporal_trends = plt.subplots(figsize=(12, 6))
if not issues_by_month.empty:
    # Bar chart for monthly issues
    bars = ax_temporal_trends.bar(
        issues_by_month.index.to_timestamp(), issues_by_month.values,
        color="#1976d2", alpha=0.85, width=20
    )
    # Line plot overlay for trend
    ax_temporal_trends.plot(
        issues_by_month.index.to_timestamp(), issues_by_month.values,
        color="#ff9800", marker="o", linewidth=2, markersize=7, label="Monthly Issues Trend"
    )
    # Annotate bars
    for dt, val in zip(issues_by_month.index, issues_by_month.values):
        ax_temporal_trends.text(
            dt.to_timestamp(), val + 0.5, str(val),
            ha='center', va='bottom', fontsize=9, color='#333'
        )
    # Formatting
    ax_temporal_trends.set_title('Monthly Trends in New Operational Issues', fontsize=14, fontweight='bold', color="#1976d2")
    ax_temporal_trends.set_xlabel('Month', fontsize=11)
    ax_temporal_trends.set_ylabel('Number of New Issues', fontsize=11)
    ax_temporal_trends.xaxis.set_major_locator(mdates.MonthLocator())
    ax_temporal_trends.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%b'))
    plt.setp(ax_temporal_trends.get_xticklabels(), rotation=45, ha='right', fontsize=9)
    ax_temporal_trends.grid(axis='y', linestyle='--', alpha=0.5)
    ax_temporal_trends.legend(fontsize=10)
    ax_temporal_trends.spines['top'].set_visible(False)
    ax_temporal_trends.spines['right'].set_visible(False)
else:
    ax_temporal_trends.text(
        0.5, 0.5, "No temporal issue data to display.",
        horizontalalignment='center', verticalalignment='center',
        transform=ax_temporal_trends.transAxes, fontsize=13, color='gray'
    )
fig_temporal_trends.tight_layout()
img_temporal_trends = fig_to_base64img(fig_temporal_trends)
temporal_trends_chart_html = f"""
    <h3 style="color:#673ab7; font-size:1.1rem;">5. Temporal Trends in New Issues</h3>
    <p style="font-size:0.9rem;">Understanding the seasonality or trend of new operational issues (based on 'Raise Time' for non-online status events) can help in predictive maintenance and resource planning:</p>
    {issues_by_month_html}
    <img src="data:image/png;base64,{img_temporal_trends}" style="max-width:100%;border:1px solid #ccc;margin:10px 0;">
    <p style="font-size:0.9rem;"><em>Interpretation:</em> The line chart clearly illustrates peaks and troughs in issue occurrences over time. Observing spikes in new issues during specific months (e.g., due to seasonal weather patterns, increased network activity, or maintenance cycles) allows for pre-emptive measures, such as pre-stocking critical parts or increasing on-call staff during high-risk periods, leading to better resource scheduling and reduced impact.</p>
"""
# 5. Geospatial Analysis: Mapping Issue Hotspots (using Latitude & Longitude)
# Check if 'Latitude' and 'Longitude' columns exist and are not all null.
if 'Latitude' in df_filtered.columns and 'Longitude' in df_filtered.columns and \
    df_filtered['Latitude'].notnull().any() and df_filtered['Longitude'].notnull().any():

     # Filter for rows with valid coordinates and non-'Active' issues.
     geo_issues = df_filtered[
          df_filtered['Latitude'].notnull() &
          df_filtered['Longitude'].notnull() &
          (~df_filtered['Issue Identity'].isin(['Active', 'PIC Finder is not Active']))
     ].copy()

     # If there are enough points, generate a map.
     if not geo_issues.empty:
          # Center map on mean coordinates.
          map_center = [geo_issues['Latitude'].mean(), geo_issues['Longitude'].mean()]
          m = folium.Map(location=map_center, zoom_start=7, tiles='CartoDB positron')

          # Add markers for each issue.
          for _, row in geo_issues.iterrows():
                popup_text = f"""
                <b>Site ID:</b> {row['Site ID']}<br>
                <b>Issue:</b> {row['Issue Identity']}<br>
                <b>Sub Office:</b> {row['Sub Office']}<br>
                <b>Township:</b> {row['Township']}<br>
                <b>Raise Time:</b> {row['Raise Time']}
                """
                folium.CircleMarker(
                     location=[row['Latitude'], row['Longitude']],
                     radius=5,
                     color='#d32f2f',
                     fill=True,
                     fill_color='#f44336',
                     fill_opacity=0.7,
                     popup=folium.Popup(popup_text, max_width=300)
                ).add_to(m)

          # Save map to HTML and embed as iframe.
          # We no longer save to a separate file, instead embed the HTML directly
          # folium.Map.get_root().render() returns the full HTML, which is too much.
          # Instead, we'll indicate if map generation is possible and provide a prompt.
          geo_map_iframe_html = f"""
          <h3 style="color:#009688; font-size:1.1rem;">5. Geospatial Hotspots: Map of Issue Locations</h3>
          <p style="font-size:0.9rem;">The interactive map below visualizes the geographic distribution of operational issues (excluding online status). Each marker represents a site with a reported issue. Use this map to identify spatial clusters and potential regional patterns for targeted field response.</p>
          <div id="foliumMapContainer" style="width: 100%; height: 450px; border:1px solid #ccc; border-radius:8px; margin:10px 0;"></div>
          <button onclick="loadFoliumMap()" style="
              background: #009688; /* Teal */
              color: white;
              padding: 8px 12px;
              border: none;
              border-radius: 5px;
              cursor: pointer;
              font-size: 0.9rem;
              margin-top: 10px;
              box-shadow: 0 2px 5px rgba(0,0,0,0.2);
          ">Load Interactive Map</button>
          <p style="font-size:0.9rem;"><em>Note: The interactive map is loaded on demand to optimize initial page load performance.</em></p>
          <p style="font-size:0.9rem;"><em>Interpretation:</em> Clusters of markers may indicate regional vulnerabilities, infrastructure challenges, or environmental factors affecting network stability. Prioritizing these areas for inspection or preventive maintenance can yield significant improvements in service reliability.</p>
          <script>
              // This script will be part of the main js_script
              let foliumMapHtml = `{m.get_root()._repr_html_()}`; // Get the raw HTML string for the map
              function loadFoliumMap() {{
                  document.getElementById('foliumMapContainer').innerHTML = foliumMapHtml;
                  // Remove the button after loading
                  document.querySelector('#foliumMapContainer + button').style.display = 'none';
              }}
          </script>
          """
     else:
          geo_map_iframe_html = """
          <h3 style="color:#009688; font-size:1.1rem;">5. Geospatial Hotspots: Map of Issue Locations</h3>
          <p style="font-size:0.9rem;">No valid latitude/longitude data available for mapping operational issues after filtering for non-active issues.</p>
          """
else:
     geo_map_iframe_html = """
     <h3 style="color:#009688; font-size:1.1rem;">5. Geospatial Hotspots: Map of Issue Locations</h3>
     <p style="font-size:0.9rem;">Latitude and Longitude columns are not present or contain no valid data in the detail data, so a geospatial analysis cannot be performed.</p>
     """

# Initialize the detail_analysis_report_html variable before appending to it.
detail_analysis_report_html = ""
detail_analysis_report_html += geo_map_iframe_html
# 5. Prolonged Operational Challenges (Focus on issues that are down and not 'Active')
# This assumes 'Raise Time' marks the start of an issue (if it's a timestamp).
# We are looking at sites that have a recorded 'Raise Time' (meaning they went down)
# and their 'Issue Identity' is not 'Active' or 'PIC Finder is not Active'.
# Group by Issue Identity and calculate average prolonging duration (in days)
# --- Prolonged Issues Grouping and Visualization ---

# --- Prolonged Issues Analysis: Render-wise Grouping with Popup Details and Larger Headings ---

prolonged_issues = df_filtered[
    (df_filtered['Raise Time_dt'].notna()) &
    (~df_filtered['Issue Identity'].isin(['Active', 'PIC Finder is not Active']))
].copy()

now = pd.Timestamp.now()
prolonged_issues['Prolonging Duration'] = prolonged_issues['Raise Time_dt'].apply(
    lambda x: now - x if pd.notna(x) else pd.Timedelta(0)
)
prolonged_issues['Prolonging Days'] = prolonged_issues['Prolonging Duration'].dt.total_seconds() / (24 * 3600)

def format_timedelta_month_day_hour(td):
    if pd.isna(td):
        return "-"
    total_days = td.days
    months = total_days // 30
    days = total_days % 30
    hours = td.seconds // 3600
    parts = []
    if months > 0:
        parts.append(f"{months}M")
    if days > 0 or months > 0:
        parts.append(f"{days}D")
    parts.append(f"{hours}Hr")
    return "-".join(parts)

prolonged_issues_html = ""
scatter_plot_html = ""

popup_counter = 0  # For unique popup IDs

# Group by Render first
for render_val, render_group in prolonged_issues.groupby('Render'):
    avg_prolonging_timedelta = render_group.groupby('Issue Identity')['Prolonging Duration'].mean().sort_values(ascending=False)
    avg_prolonging_days = render_group.groupby('Issue Identity')['Prolonging Days'].mean().sort_values(ascending=False)
    site_counts = render_group.groupby('Issue Identity')['Site ID'].nunique().reindex(avg_prolonging_timedelta.index)

    n = len(avg_prolonging_timedelta)
    if n >= 3:
        group_size = n // 3
        top_idx = avg_prolonging_timedelta.index[:group_size]
        mid_idx = avg_prolonging_timedelta.index[group_size:2*group_size]
        bottom_idx = avg_prolonging_timedelta.index[2*group_size:]
    else:
        top_idx, mid_idx, bottom_idx = avg_prolonging_timedelta.index, [], []

    group_labels = [
        ("Top Prolonging Issues", top_idx, "#ffebee", "#d32f2f"),
        ("Mid Prolonging Issues", mid_idx, "#e3f2fd", "#1976d2"),
        ("Other Prolonging Issues", bottom_idx, "#e8f5e9", "#388e3c")
    ]

    # Larger heading for Render
    prolonged_issues_html += f"<h2 style='color:#1976d2; font-size:1.35rem; margin-top:2em;'>{render_val} — Prolonged Issues</h2>"

    for group_name, idx, bg_color, accent_color in group_labels:
        if len(idx) == 0:
            continue
        group_td = avg_prolonging_timedelta.loc[idx]
        group_days = avg_prolonging_days.loc[idx]
        group_sites = site_counts.loc[idx]

        group_table = pd.DataFrame({
            'Issue Identity': group_td.index,
            'Average Prolonging Duration': group_td.values,
            'Number of Sites': group_sites.values
        })
        group_table['Average Prolonging Duration'] = group_table['Average Prolonging Duration'].apply(format_timedelta_month_day_hour)
        group_table_html = group_table.to_html(
            index=False, escape=False,
            classes="styled-table",
            border=0
        )
        group_table_html = group_table_html.replace(
            '<table ',
            f'<table style="background-color:{bg_color}; border:2px solid {accent_color};" '
        )
        group_table_html = group_table_html.replace(
            '<thead>',
            f'<thead style="background-color:{accent_color}; color:#fff;">'
        )

        import matplotlib.dates as mdates
        fig_scatter, ax_scatter = plt.subplots(figsize=(8, 5))
        if not group_days.empty:
            sns.scatterplot(
                x=group_days.index,
                y=group_days.values,
                s=120,
                color=accent_color,
                ax=ax_scatter
            )
            ax_scatter.set_title(f'{group_name}: Avg Prolonging Duration', fontsize=13, color=accent_color)
            ax_scatter.set_xlabel('Issue Identity', fontsize=10)
            ax_scatter.set_ylabel('Avg Prolonging Duration (days)', fontsize=10)
            ax_scatter.tick_params(axis='x', rotation=45)
            ax_scatter.grid(axis='y', linestyle='--', alpha=0.5)
            ax_scatter.spines['top'].set_color(accent_color)
            ax_scatter.spines['right'].set_color(accent_color)
            ax_scatter.spines['left'].set_color(accent_color)
            ax_scatter.spines['bottom'].set_color(accent_color)
        else:
            ax_scatter.text(
                0.5, 0.5, "No prolonged issues to display.",
                horizontalalignment='center', verticalalignment='center',
                transform=ax_scatter.transAxes, fontsize=12, color='gray'
            )
        fig_scatter.tight_layout()
        img_scatter = fig_to_base64img(fig_scatter)
        # Popup HTML for this group
        popup_id = f"popup_{popup_counter}"
        popup_counter += 1
        scatter_html = f"""
            <button onclick="document.getElementById('{popup_id}').style.display='block';" style="background:{accent_color};color:#fff;padding:7px 18px;border:none;border-radius:6px;cursor:pointer;font-size:1rem;margin:10px 0;">Show {group_name} Details</button>
            <div id="{popup_id}" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.25); z-index:9999;">
                <div style="background:#fff; margin:40px auto; padding:25px; border-radius:10px; max-width:700px; min-width:320px; position:relative; overflow-y: auto; max-height: calc(100vh - 80px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); border:2px solid {accent_color};">
                    <button onclick="document.getElementById('{popup_id}').style.display='none'" style="position:absolute; top:8px; right:8px; font-size:1.1em; background:none; border:none; cursor:pointer; color:#888;">✖</button>
                    <h2 style="color:{accent_color}; font-size:1.2rem; margin-bottom:0.5em;">{group_name} — {render_val}</h2>
                    <div style="background:{bg_color}; border-radius:8px; padding:8px;">
                        <img src="data:image/png;base64,{img_scatter}" style="max-width:100%;border:1px solid {accent_color};margin:10px 0;">
                        {group_table_html}
                    </div>
                </div>
            </div>
        """
        group_ul = f"<ul style='background:{bg_color}; border-left:4px solid {accent_color}; padding:8px 16px;'>"
        for issue in group_td.index:
            avg_td = group_td[issue]
            num_sites = group_sites[issue]
            # Get all unique Site IDs for this issue in this render group
            site_ids = render_group[render_group['Issue Identity'] == issue]['Site ID'].unique()
            site_ids_str = ", ".join(map(str, site_ids))
            # Add details/summary for site ids
            site_ids_html = f"<details><summary>Show Site IDs</summary><div style='white-space: normal;'>{site_ids_str}</div></details>"
            group_ul += (
            f"<li><strong style='color:{accent_color};'>{issue}:</strong> "
            f"{format_timedelta_month_day_hour(avg_td)} (average prolonging duration), "
            f"<strong>{num_sites}</strong> site(s) {site_ids_html}</li>"
            )
        group_ul += "</ul>"

        # Larger heading for group
        prolonged_issues_html += f"""
        <div style="margin-bottom:2em;">
            <h3 style="color:{accent_color}; font-size:1.15rem;">{group_name}</h3>
            <p style="font-size:1em;">Below are the <b>{group_name.lower()}</b> for <b>{render_val}</b> based on average prolonging duration. Click the button for details and chart.</p>
            {group_ul}
            {scatter_html}
        </div>
        """

if not prolonged_issues_html:
    prolonged_issues_html = "<ul><li>No specific prolonged operational issues identified from current data (excluding 'Active' and 'PIC Finder is not Active').</li></ul>"

detail_analysis_report_html += ""  # scatter_plot_html is now included per group above


# --- Focused CA Fluctuation Analysis: Fluctuated Sites with Grading and Popup Details ---

# Calculate CA fluctuation (standard deviation) for each site in df_sql
site_fluctuation = (
    df_sql.groupby('Site_ID')['CA_Result']
    .std()
    .sort_values(ascending=False)
    .dropna()
)

# Assign fluctuation grades (A: top 20%, B: next 30%, C: rest)
n_sites = len(site_fluctuation)
grade_a_cut = int(n_sites * 0.2)
grade_b_cut = int(n_sites * 0.5)
fluctuation_grades = {}
for idx, site_id in enumerate(site_fluctuation.index):
    if idx < grade_a_cut:
        fluctuation_grades[site_id] = 'A'
    elif idx < grade_b_cut:
        fluctuation_grades[site_id] = 'B'
    else:
        fluctuation_grades[site_id] = 'C'

# Helper to get top N sites for each grade
def get_top_sites_by_grade(grade, n=10):
    return [site_id for site_id in site_fluctuation.index if fluctuation_grades[site_id] == grade][:n]

# Prepare HTML for site list with grades and popups for details (A, B, C groups)
fluctuated_site_list_html = ""
fluctuated_site_popup_html = ""
popup_counter = 0

for grade, color in [('A', '#d32f2f'), ('B', '#fbc02d'), ('C', '#388e3c')]:
    top_sites = get_top_sites_by_grade(grade, n=10)
    if not top_sites:
        continue
    fluctuated_site_list_html += f"<h4 style='color:{color};margin-top:1em;'>Grade {grade} Sites (Top 10)</h4><ul style='font-size:1em;'>"
    for site_id in top_sites:
        std_val = site_fluctuation[site_id]
        popup_id = f"fluctuated_site_popup_{popup_counter}"
        popup_counter += 1

        # Prepare popup content: CA trend chart and issue info
        site_ca = df_sql[df_sql['Site_ID'].astype(str) == str(site_id)].copy()
        site_ca['Date'] = pd.to_datetime(site_ca['Date'], errors='coerce')
        site_ca = site_ca.dropna(subset=['Date'])
        # Most frequent issue
        issues = df_filtered[df_filtered['Site ID'].astype(str) == str(site_id)]['Issue Identity']
        issues = issues[~issues.isin(['Active', 'PIC Finder is not Active'])]
        issue_counts = issues.value_counts()
        top_issue = issue_counts.idxmax() if not issue_counts.empty else "N/A"
        # Weekly trend
        site_ca['YearWeek'] = site_ca['Date'].dt.strftime('%Y-W%U')
        ca_week = site_ca.groupby('YearWeek')['CA_Result'].mean().reset_index()
        fig_w, ax_w = plt.subplots(figsize=(7, 2.7))
        ax_w.plot(ca_week['YearWeek'], ca_week['CA_Result'], marker='o', color=color, label='Weekly AVG CA')
        ax_w.set_title(f"Weekly CA Trend: Site ID {site_id}", fontsize=10)
        ax_w.set_xlabel('Year-Week', fontsize=9)
        ax_w.set_ylabel('CA Result', fontsize=9)
        ax_w.xaxis.set_major_locator(plt.MaxNLocator(10))
        plt.setp(ax_w.get_xticklabels(), rotation=45, ha='right', fontsize=8)
        for x, y in zip(ca_week['YearWeek'], ca_week['CA_Result']):
            if not pd.isna(y):
                ax_w.text(x, y, f"{y:.1f}", fontsize=7, color='#444', ha='center', va='bottom')
        fig_w.tight_layout()
        # --- Make figure zoomable: Save as SVG for better zoom, and add zoom CSS ---
        buf = io.BytesIO()
        fig_w.savefig(buf, format="svg", bbox_inches='tight')
        buf.seek(0)
        img_trend_w_svg = buf.getvalue().decode('utf-8')
        plt.close(fig_w)

        fluctuated_site_popup_html += f"""
        <div id="{popup_id}" style="display:none; position:fixed; top:0; left:0; width:100vw; height:100vh; background:rgba(0,0,0,0.25); z-index:9999;">
            <div style="background:#fff; margin:40px auto; padding:25px; border-radius:10px; max-width:520px; min-width:220px; position:relative; box-shadow: 0 5px 15px rgba(0,0,0,0.3);">
                <button onclick="document.getElementById('{popup_id}').style.display='none'" style="position:absolute; top:8px; right:8px; font-size:1.1em; background:none; border:none; cursor:pointer; color:#888;">✖</button>
                <h3 style="color:{color}; font-size:1.1rem;">Fluctuated Site Detail</h3>
                <div style="font-size:1.1em; color:#222; text-align:center; margin:10px 0;"><b>Site ID: {site_id}</b></div>
                <div style="margin-bottom:8px;"><b>Fluctuation Grade:</b> <span style="color:{color};">{grade}</span> &nbsp; <b>Std:</b> {std_val:.2f}</div>
                <div style="margin-bottom:8px;"><b>Most Frequent Issue:</b> {top_issue}</div>
                <div style="margin-bottom:8px;"><b>Weekly CA Trend (Zoom: Ctrl+Scroll or Pinch):</b></div>
                <div style="overflow:auto; border:1px solid #ccc; border-radius:6px; background:#fafafa; max-width:100%; max-height:350px;">
                    {img_trend_w_svg}
                </div>
                <div style="margin-top:10px; font-size:0.95em; color:#444;">
                    <b>Interpretation:</b> This site shows CA fluctuation (Grade {grade}). Frequent issue: <b>{top_issue}</b>. Investigate for recurring root causes or unstable conditions.
                </div>
            </div>
        </div>
        """

        # List item with clickable site id
        fluctuated_site_list_html += f"""
        <li>
            <button onclick="document.getElementById('{popup_id}').style.display='block';" style="background:{color};color:#fff;padding:2px 10px;border:none;border-radius:4px;cursor:pointer;font-size:0.95em;">
                {site_id}
            </button>
            &nbsp; <b>Grade:</b> <span style="color:{color};">{grade}</span>
        </li>
        """
    fluctuated_site_list_html += "</ul>"

if not fluctuated_site_list_html:
    fluctuated_site_list_html = "<p>No highly fluctuated sites found.</p>"

# --- Analyst Interpretation for Fluctuated Sites CA Analysis ---
analyst_interpretation_html_std = f"""
<hr>
<h3 style="color:#009688; font-size:1.1rem;">🔎 Most Fluctuated Sites CA Analysis (Grades A/B/C)</h3>
<p style="font-size:0.95rem;">
    <b>Key Findings:</b>
    <ul>
        <li>Sites are graded by CA Result fluctuation: <b>A</b> (top 20%), <b>B</b> (next 30%), <b>C</b> (rest).</li>
        <li>Click on a Site ID to view its CA trend and most frequent operational issue. The chart is zoomable (use Ctrl+Scroll or pinch on touch devices).</li>
        <li>Grade A sites are most unstable and should be prioritized for investigation. Grades B and C are also shown for broader monitoring.</li>
    </ul>
</p>
{fluctuated_site_list_html}
{fluctuated_site_popup_html}
<p style="font-size:0.95rem;">
    <b>Strategic Recommendation:</b><br>
    Focus on Grade A sites for root cause analysis and stabilization. Persistent CA volatility signals underlying systemic or environmental problems. Monitor Grades B and C for emerging risks.
</p>
"""


detail_analysis_report_html = f"""
<div id="detail_data_analysis_tab" class="tabcontent">
    <h2 style="font-size:1.5rem;">📊 Detail Data Analysis Report: A Deep Dive</h2>
    <p style="font-size:0.9rem;">This section provides a deeper analytical perspective, leveraging the granular data from the 'Detail Data Table' and connecting it with key performance indicators from the 'Analyst Overview'.</p>
    
    <h3 style="color:#1976d2; font-size:1.1rem;">1. Data Volume and Granularity</h3>
    <ul style="font-size:0.9rem;">
        <li>The detailed dataset encompasses <strong>{total_sites_detail} individual site records</strong>, offering a robust foundation for identifying specific operational challenges at a granular level.</li>
        <li>This granularity is crucial for pinpointing not just <em>what</em> is happening, but <em>where</em> and to <em>which specific assets</em>, enabling highly targeted interventions.</li>
    </ul>

    <hr>

    <h3 style="color:#d32f2f; font-size:1.1rem;">2. Leading Causes of Operational Disruption</h3>
    <p style="font-size:0.9rem;">A concentrated effort on the most frequent 'Issue Identities' (excluding 'Active' and 'PIC Finder is not Active' which denote online status rather than actual issues) will yield the highest impact on overall maintenance stability:</p>
    {top_issues_html}
    <p style="font-size:0.9rem;"><em>Interpretation:</em> The dominance of these top issues indicates clear and recurring problem areas. Addressing these root causes systematically, perhaps through enhanced training, equipment upgrades, or revised operational protocols, can significantly reduce overall downtime and improve service reliability.</p>

    <hr>

    <h3 style="color:#f57c00; font-size:1.1rem;">3. Render Type Performance and Issue Correlation</h3>
    <p style="font-size:0.9rem;">Analyzing issues by 'Render' type reveals whether certain operational models or equipment configurations are more susceptible to particular problems. This excludes 'Active' and 'PIC Finder is not Active' statuses.</p>
    <div class="table-container" style="max-height: 250px; overflow-y: auto;">
        {issues_by_render_html}
    </div>
    <p style="font-size:0.9rem;"><em>Interpretation:</em> This matrix allows for a highly targeted approach to problem-solving. For instance, if 'Fiber Cut' issues are disproportionately high in a specific 'Render' type, it strongly suggests a need to review deployment practices, cabling standards, or environmental factors unique to that category, leading to more effective and efficient mitigation strategies.</p>

    <hr>

    {geo_hotspots_chart_html}

    <hr>

    {temporal_trends_chart_html}

    <hr>

    <h3 style="color:#ffc107; font-size:1.1rem;">6. Prolonged Operational Challenges</h3>
    <p style="font-size:0.9rem;">Identifying issues that persist for extended periods is crucial, as they often indicate potential systemic problems, complex failures, or resource bottlenecks. This analysis specifically looks at non-active issues with a recorded 'Raise Time':</p>
    {prolonged_issues_html}
    {scatter_plot_html}
    {mttr_mtbf_html}
    {dataframe_viewer_html}
    {analyst_interpretation_html_std}
    <p style="font-size:0.9rem;"><em>Interpretation:</em> These prolonged issues are critical areas where standard troubleshooting might not be sufficient. They typically require specialized teams, deeper engineering investigation, or a comprehensive review of current resolution protocols. Rapid escalation and dedicated task forces for these specific issue types are recommended to minimize long-term impact on service availability and customer satisfaction.</p>
    
    <hr>

    <h3 style="color:#1565c0; font-size:1.1rem;">🎯 Strategic Recommendations from Detail Analysis</h3>
    <blockquote style="border-left: 4px solid #1976d2; padding-left: 12px; color: #333; font-style: italic; font-size:0.9rem; background-color: #eef7ff; padding: 15px; border-radius: 8px;">
        "The in-depth analysis of the detailed data reveals not only the immediate operational challenges but also crucial underlying patterns and potential systemic vulnerabilities. To proactively optimize network performance and enhance overall reliability, we strongly recommend the following strategic actions:
        <ol style="font-size:0.9rem; margin-top: 8px; padding-left: 20px;">
            <li><strong>Targeted Remediation & Root Cause Analysis:</strong> Prioritize intensive efforts on the identified 'Top 5 Most Prevalent Issues' (e.g., Fiber Back Bone, Unsafe, Uplink Unsafe). Conduct thorough root cause analyses for these recurring issues, especially in the 'Geographical Hotspots', to implement sustainable solutions rather than reactive fixes.</li>
            <li><strong>Proactive Resource Allocation & Predictive Maintenance:</strong> Utilize the insights from 'Temporal Trends' to anticipate periods of increased risk (e.g., specific months with higher issue counts). Allocate resources (personnel, spare parts, equipment) proactively to these periods and regions, shifting from a reactive to a more predictive maintenance model.</li>
            <li><strong>Escalated Resolution for Persistent Issues:</strong> Establish dedicated, cross-functional task forces for 'Prolonged Operational Challenges'. These teams should be empowered to escalate, bypass standard protocols if necessary, and bring specialized expertise to bear, preventing long-term degradation of service quality.</li>
            <li><strong>Render-Specific Operational Playbooks:</strong> Develop or refine tailored troubleshooting guides and maintenance playbooks based on the 'Distribution of Issues by Render Type'. This ensures that interventions are highly effective and specific to the unique characteristics and common vulnerabilities of each network segment or technology type.</li>
            <li><strong>Continuous Monitoring & Feedback Loop:</strong> Implement enhanced monitoring mechanisms to track the effectiveness of implemented solutions. Foster a continuous feedback loop between field operations, technical teams, and data analysts to refine strategies based on real-world outcomes, ensuring iterative improvement in network stability."</li>
        </ol>
        This comprehensive, data-driven approach will enable more efficient resource allocation, significantly faster issue resolution times, and ultimately, cultivate a more resilient, high-performing, and customer saftisfying severvice provider."
    </blockquote>
</div>
"""
tab_buttons.append('<button type="button" class="tablinks" data-tab="detail_data_analysis_tab">📈 Detail Data Analysis</button>')
tab_contents.append(detail_analysis_report_html)


# Add Site Status Summary tab
tab_buttons.append('<button type="button" class="tablinks" data-tab="site_status_summary">📋 Site Status Summary</button>')
tab_contents.append(f"""
<div id="site_status_summary" class="tabcontent">
    <h2>📋 Site Status Summary Table</h2>
    <p>This table shows Total Sites, Current Down Sites, and Online Status grouped by State/Division, Sub Office, Township, and Render.</p>
    {styled_status.to_html(escape=False)}
</div>
""")

# Add Analyst Overview tab
tab_buttons.append('<button type="button" class="tablinks" data-tab="analyst_overview">📊 Analyst Overview</button>')
tab_contents.append(f"""
<div id="analyst_overview" class="tabcontent">
    <h2>📊 Analyst Overview</h2>
    <h3 style="font-size:1.1rem;">1. Average CA by Week and Render</h3>
    <img src="data:image/png;base64,{img1}" style="max-width:100%;border:1px solid #ccc;margin:20px 0;">
    <h3 style="font-size:1.1rem;">2. Average CA by Sub Office and Month</h3>
    <img src="data:image/png;base64,{img2}" style="max-width:100%;border:1px solid #ccc;margin:20px 0;">
    <h3 style="font-size:1.1rem;">3. Average CA by Date</h3>
    <img src="data:image/png;base64,{img3}" style="max-width:100%;border:1px solid #ccc;margin:20px 0;">
    <h3 style="font-size:1.1rem;">4. Average CA by Sub Office and Week</h3>
    {styled_pivot_avg_ca.to_html(escape=False)}
    <h3 style="font-size:1.1rem;">5. Weekly CA Trends (with arrows)</h3>
    {pivot_with_arrows.to_html(escape=False)}
    <h3 style="font-size:1.1rem;">6. Site Count by Render and Week</h3>
    {styled_pivot_count.to_html(escape=False)}
    <h3 style="font-size:1.1rem;">7. CA by Township and Month</h3>
    {styled_pivot_township_month.to_html(escape=False)}
</div>
""")

# --- JS for Tabs & Modals ---
# JavaScript to handle tab switching and responsive behavior for DataTables and Chart.js.
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
            // Trigger Chart.js redraw for slicer modals to ensure they render correctly when visible.
            if (tabId === 'slicerModal' && window.slicerChartObj) {{
                window.slicerChartObj.resize();
            }}
            if (tabId === 'arndSlicerModal' && window.arndSlicerChartObj) {{
                window.arndSlicerChartObj.resize();
            }}
        }}
    }}
    tabs.forEach(btn => {{
        btn.addEventListener("click", function () {{
            const tabId = btn.getAttribute("data-tab");
            // Only open tab content if it's not the detail data modal button
            if (tabId !== null && tabId !== undefined) {{ // Ensure data-tab attribute exists
                openTab(tabId);
                this.classList.add("active");
            }}
        }});
    }});
    // Open the first tab by default on page load.
    if (tabs.length) {{
        // Filter out buttons that specifically open modals (e.g., detail data)
        const initialTabButton = Array.from(tabs).find(btn => !btn.onclick);
        if (initialTabButton) {{
            initialTabButton.click();
        }}
    }}

    // --- Slicer Modal JS ---
    const summariseData = {summarise_json_str};
    function highlightCell(col, val, row) {{
      if (col === 'Current Down Site' && row['Current Down Site'] > 1.5 * row['Online Status']) {{
        return 'background-color: #ffe066; color: red; font-weight: bold;';
      }}
      if (col === 'effectiveness (%)' && parseFloat(val) > 50) {{
        return 'background-color: #b6fcb6; color: #155724; font-weight: bold;';
      }}
      return '';
    }}
    function groupAndSummarise(groupBy) {{
      const groups = {{}};
      summariseData.forEach(row => {{
        const key = row[groupBy];
        if (!groups[key]) {{
          groups[key] = {{ 'Total Sites': 0, 'Current Down Site': 0, 'Online Status': 0, rows: [] }};
        }}
        groups[key]['Total Sites'] += row['Total Sites'];
        groups[key]['Current Down Site'] += row['Current Down Site'];
        groups[key]['Online Status'] += row['Online Status'];
        groups[key].rows.push(row);
      }});
      Object.entries(groups).forEach(([key, g]) => {{
        g['effectiveness (%)'] = g['Total Sites'] ? (g['Online Status'] / g['Total Sites'] * 100).toFixed(2) : '0.00';
      }});
      return groups;
    }}
    function renderTableAndChart(groupBy) {{
      const groups = groupAndSummarise(groupBy);
      
      let sortedGroups = Object.entries(groups);
      if (groupBy === 'Township') {{
        sortedGroups.sort((a, b) => parseFloat(b[1]['effectiveness (%)']) - parseFloat(a[1]['effectiveness (%)']));
        sortedGroups = sortedGroups.slice(0, 20);
      }}
      
      let html = `<table class="styled-table"><thead><tr>
        <th style="text-align: center;">${{groupBy}}</th>
        <th style="text-align: center;">Total Sites</th>
        <th style="text-align: center;">Current Down Site</th>
        <th style="text-align: center;">Online Status</th>
        <th style="text-align: center;">effectiveness (%)</th>
      </tr></thead><tbody>`;
      
      sortedGroups.forEach(([key, g]) => {{
        html += `<tr>
          <td>${{key}}</td>
          <td style="text-align: center;">${{g['Total Sites']}}</td>
          <td style="text-align: center; ${{highlightCell('Current Down Site', g['Current Down Site'], g)}}">${{g['Current Down Site']}}</td>
          <td style="text-align: center;">${{g['Online Status']}}</td>
          <td style="text-align: center; ${{highlightCell('effectiveness (%)', g['effectiveness (%)'], g)}}">${{g['effectiveness (%)']}}%</td>
        </tr>`;
      }});
      html += '</tbody></table>';
      document.getElementById('slicerTableDiv').innerHTML = html;
      
      const ctx = document.getElementById('slicerChart').getContext('2d');
      if (window.slicerChartObj) window.slicerChartObj.destroy(); // Destroy previous chart instance.
      
      const labels = sortedGroups.map(entry => entry[0]);
      const totalSites = sortedGroups.map(entry => entry[1]['Total Sites']);
      const downSites = sortedGroups.map(entry => entry[1]['Current Down Site']);
      const onlineSites = sortedGroups.map(entry => entry[1]['Online Status']);
      const effectiveness = sortedGroups.map(entry => parseFloat(entry[1]['effectiveness (%)']));
      
      window.slicerChartObj = new Chart(ctx, {{
        type: 'bar',
        data: {{
          labels: labels,
          datasets: [
            {{ label: 'Total Sites', data: totalSites, backgroundColor: '#90caf9' }},
            {{ label: 'Current Down Site', data: downSites, backgroundColor: '#ffe066' }},
            {{ label: 'Online Status', data: onlineSites, backgroundColor: '#b6fcb6' }},
            {{ label: 'Effectiveness (%)', data: effectiveness, type: 'line', borderColor: '#388e3c', backgroundColor: 'rgba(56,142,60,0.15)', yAxisID: 'y1', fill: false }}
          ]
        }},
        options: {{
          responsive: true,
          plugins: {{ legend: {{ position: 'top' }} }},
          scales: {{
            y: {{ beginAtZero: true, title: {{ display: true, text: 'Site Count', font: {{ size: 12 }} }} }},
            y1: {{ beginAtZero: true, position: 'right', title: {{ display: true, text: 'Effectiveness (%)', font: {{ size: 12 }} }}, grid: {{ drawOnChartArea: false }} }}
          }}
        }}
      }});
    }}
    document.getElementById('openSlicerBtn').onclick = function() {{
      document.getElementById('slicerModal').style.display = 'block';
      renderTableAndChart(document.getElementById('slicerSelect').value);
    }};
    document.getElementById('slicerSelect').onchange = function() {{
      renderTableAndChart(this.value);
    }};

    // --- Active Render Focus Slicer JS ---
    const arndSummariseData = {arnd_summarise_json_str};
    function arndHighlightCell(col, val, row) {{
      if (col === 'Current Down Site' && row['Current Down Site'] > 1.5 * row['Online Status']) {{
        return 'background-color: #ffe066; color: red; font-weight: bold;';
      }}
      if (col === 'effectiveness (%)' && parseFloat(val) > 50) {{
        return 'background-color: #b6fcb6; color: #155724; font-weight: bold;';
      }}
      return '';
    }}
    function arndGroupAndSummarise(groupBy) {{
      const groups = {{}};
      arndSummariseData.forEach(row => {{
        const key = row[groupBy];
        if (!groups[key]) {{
          groups[key] = {{ 'Total Sites': 0, 'Current Down Site': 0, 'Online Status': 0, rows: [] }};
        }}
        groups[key]['Total Sites'] += row['Total Sites'];
        groups[key]['Current Down Site'] += row['Current Down Site'];
        groups[key]['Online Status'] += row['Online Status'];
        groups[key].rows.push(row);
      }});
      Object.entries(groups).forEach(([key, g]) => {{
        g['effectiveness (%)'] = g['Total Sites'] ? (g['Online Status'] / g['Total Sites'] * 100).toFixed(2) : '0.00';
      }});
      return groups;
    }}
    function arndRenderTableAndChart(groupBy) {{
      const groups = arndGroupAndSummarise(groupBy);
      let sortedGroups = Object.entries(groups);
      if (groupBy === 'Township') {{
        sortedGroups.sort((a, b) => parseFloat(b[1]['effectiveness (%)']) - parseFloat(a[1]['effectiveness (%)']));
        sortedGroups = sortedGroups.slice(0, 20);
      }}
      let html = `<table class="styled-table"><thead><tr>
        <th style="text-align: center;">${{groupBy}}</th>
        <th style="text-align: center;">Total Sites</th>
        <th style="text-align: center;">Current Down Site</th>
        <th style="text-align: center;">Online Status</th>
        <th style="text-align: center;">effectiveness (%)</th>
      </tr></thead><tbody>`;
      sortedGroups.forEach(([key, g]) => {{
        html += `<tr>
          <td>${{key}}</td>
          <td style="text-align: center;">${{g['Total Sites']}}</td>
          <td style="text-align: center; ${{arndHighlightCell('Current Down Site', g['Current Down Site'], g)}}">${{g['Current Down Site']}}</td>
          <td style="text-align: center;">${{g['Online Status']}}</td>
          <td style="text-align: center; ${{arndHighlightCell('effectiveness (%)', g['effectiveness (%)'], g)}}">${{g['effectiveness (%)']}}%</td>
        </tr>`;
      }});
      html += '</tbody></table>';
      document.getElementById('arndSlicerTableDiv').innerHTML = html;
      const ctx = document.getElementById('arndSlicerChart').getContext('2d');
      if (window.arndSlicerChartObj) window.arndSlicerChartObj.destroy();
      const labels = sortedGroups.map(entry => entry[0]);
      const totalSites = sortedGroups.map(entry => entry[1]['Total Sites']);
      const downSites = sortedGroups.map(entry => entry[1]['Current Down Site']);
      const onlineSites = sortedGroups.map(entry => entry[1]['Online Status']);
      const effectiveness = sortedGroups.map(entry => parseFloat(entry[1]['effectiveness (%)']));
      window.arndSlicerChartObj = new Chart(ctx, {{
        type: 'bar',
        data: {{
          labels: labels,
          datasets: [
            {{ label: 'Total Sites', data: totalSites, backgroundColor: '#90caf9' }},
            {{ label: 'Current Down Site', data: downSites, backgroundColor: '#ffe066' }},
            {{ label: 'Online Status', data: onlineSites, backgroundColor: '#b6fcb6' }},
            {{ label: 'Effectiveness (%)', data: effectiveness, type: 'line', borderColor: '#388e3c', backgroundColor: 'rgba(56,142,60,0.15)', yAxisID: 'y1', fill: false }}
          ]
        }},
        options: {{
          responsive: true,
          plugins: {{ legend: {{ position: 'top' }} }},
          scales: {{
            y: {{ beginAtZero: true, title: {{ display: true, text: 'Site Count', font: {{ size: 12 }} }} }},
            y1: {{ beginAtZero: true, position: 'right', title: {{ display: true, text: 'Effectiveness (%)', font: {{ size: 12 }} }}, grid: {{ drawOnChartArea: false }} }}
          }}
        }}
      }});
    }}
    document.getElementById('openArndSlicerBtn').onclick = function() {{
      document.getElementById('arndSlicerModal').style.display = 'block';
      arndRenderTableAndChart(document.getElementById('arndSlicerSelect').value);
    }};
    document.getElementById('arndSlicerSelect').onchange = function() {{
      arndRenderTableAndChart(this.value);
    }};

    // --- Detail Data Table Modal JS ---
    let detailDataTableInstance = null; // Variable to hold DataTable instance

    window.openDetailDataModal = function() {{
        document.getElementById('detailDataModal').style.display = 'block';

        // Check if DataTable is already initialized on this table
        if ($.fn.DataTable.isDataTable('#detailDataTable')) {{
            detailDataTableInstance = $('#detailDataTable').DataTable();
            detailDataTableInstance.columns.adjust().draw(); // Adjust columns if modal was hidden
        }} else {{
            detailDataTableInstance = $('#detailDataTable').DataTable({{
                scrollX: true, // Enable horizontal scrolling for responsiveness
                pageLength: 20, // Default number of entries per page
                lengthMenu: [ [10, 15, 25, 50, -1], [10, 15, 25, 50, "All"] ], // Options for entries per page
                dom: 'lBfrtip', // 'l'ength, 'B'uttons, 'f'ilter (search), 'r'processing, 't'able, 'i'nfo, 'p'agination
                buttons: [
                    'excel', 'print'
                ],
                initComplete: function () {{
                    var api = this.api();
                    // For each select dropdown, populate options and add change listener
                    api.columns().every(function () {{
                        var column = this;
                        var columnHeader = $(column.header()).text(); // Get the column header text

                        const filterableColumnNames = [
                            'Render', 'State/Division', 'Sub Office', 'Township', 'Issue Identity'
                        ];

                        if (filterableColumnNames.includes(columnHeader)) {{
                            var select = $('select[data-column-name="' + columnHeader + '"]'); // Find the specific select for this column

                            // Clear existing options first to avoid duplication on re-init
                            select.find('option').not(':first').remove();

                            // Populate the select dropdown with unique values from the column
                            column.data().unique().sort().each(function (d, j) {{
                                if (d !== null && d !== undefined && String(d).trim() !== '') {{
                                    select.append('<option value="' + d + '">' + d + '</option>');
                                }}
                            }});

                            // Add change event listener to apply filter
                            select.off('change').on('change', function () {{ // Use .off().on() to prevent multiple bindings
                                var val = $.fn.dataTable.util.escapeRegex($(this).val());
                                column.search(val ? '^' + val + '$' : '', true, false).draw();
                            }});
                        }}
                    }});
                }}
            }});
        }}
    }};

    // --- Folium Map Loading ---
    // The foliumMapHtml variable is generated and embedded directly by Python
    // and the loadFoliumMap function is defined inline in the Python-generated HTML.

    // Toggle author box function is already defined in author_box_html.
}});
</script>
"""

# --- Professional Table Styling (CSS) ---
# Comprehensive CSS for a professional and responsive look for all tables and general page elements.
pro_table_style = """
<style>
    /* Google Fonts for 'Inter' */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    body { font-family: 'Inter', sans-serif; font-size: 0.875rem; /* Base font size, effectively 14px if default is 16px */ }

    h1 { font-size: 1.8rem; } /* Adjusted from 2.5em */
    h2 { font-size: 1.5rem; } /* Adjusted from 1.8em */
    h3 { font-size: 1.1rem; } /* Adjusted from 1.3em */
    p { font-size: 0.9rem; } /* Adjusted from 1em */
    ul { font-size: 0.9rem; } /* Adjusted from 1em */
    li { font-size: 0.9rem; } /* Adjusted from 1em */

    table {
        border-collapse: separate !important; /* Use separate borders for better rounding */
        border-spacing: 0; /* Remove space between cells */
        width: 100%;
        margin: 20px 0; /* Adjusted margin */
        font-size: 0.95em; /* Adjusted base table font size */
        background: #fff;
        box-shadow: 0 2px 10px rgba(30,64,175,0.05); /* Lighter shadow */
        border-radius: 8px; /* Slightly smaller radius */
    }
    th, td {
        border: 1px solid #eef2f6 !important; /* Lighter, cleaner borders */
        padding: 10px 12px !important; /* Adjusted padding */
        text-align: left;
        vertical-align: middle;
    }
    th {
        background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%); /* Gradient header */
        color: #0d47a1;
        font-weight: 700;
        font-size: 1em; /* Kept relative to table font-size */
        border-bottom: 2px solid #a7d9f7 !important; /* Stronger bottom border for header */
        position: sticky; /* Make header sticky when scrolling table */
        top: 0;
        z-index: 2; /* Ensure header stays on top */
    }
    tr {
        border-bottom: 1px solid #f0f3f6 !important; /* Very light row separators */
        transition: background 0.2s; /* Smooth transition for hover effects */
    }
    tr:nth-child(even) {
        background: #fdfefe; /* Very slight alternate row color */
    }
    tr:hover {
        background: #e9f5fd; /* Light hover effect */
    }
    td {
        color: #222;
        font-size: 0.95em; /* Adjusted relative to table font-size */
        white-space: nowrap; /* Ensures no text wrapping for main report tables */
    }
    td[style*="background-color"] {
        border-radius: 4px; /* Smaller radius for highlighted cells */
    }
    details {
        margin: 4px 0; /* Adjusted margin */
    }
    summary { font-size: 0.9em; } /* Adjusted font size for details summary */
    details div { font-size: 0.85em; } /* Adjusted font size for details content */

    /* Responsive table behavior for smaller screens */
    @media (max-width: 900px) {
        table, thead, tbody, th, td, tr {
            display: block; /* Stack table elements */
        }
        th, td {
            padding: 8px 6px !important; /* Further reduced for mobile */
        }
        tr {
            margin-bottom: 8px; /* Adjusted margin between stacked rows */
        }
    }
    /* Blinking effect for AI message */
    .kmk-blink {
        animation: blink-animation 1s steps(5, start) infinite;
        font-size: 1rem; /* Adjusted for overall scaling */
    }
    @keyframes blink-animation {
        to { visibility: hidden; }
    }

    /* Custom style for tables within the new analysis tab (nested tables) */
    .styled-table {
        width: 100%;
        border-collapse: collapse;
        margin: 15px 0;
        font-size: 0.85rem; /* Adjusted font size for nested tables */
        box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        border-radius: 6px;
        overflow: hidden; /* Ensures rounded corners on container */
    }
    .styled-table thead th {
        background-color: #f0f8ff; /* Light blue header */
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
    .styled-table tbody tr:last-child td {
        border-bottom: none; /* No border on the last row's cells */
    }
    .styled-table tbody tr:nth-child(even) {
        background-color: #fdfefe;
    }
    .styled-table tbody tr:hover {
        background-color: #f0faff;
    }
    /* Specific styles for the main report, overriding or complementing pro_table_style */
    body { padding: 20px; } /* Keep padding */
    .tab-header { position: sticky; top: 0; background: #fff; z-index: 100; padding: 6px 0; border-bottom: 1px solid #e0e0e0; } /* Adjusted padding and border */
    .tablinks {
        background: #e0f0ff; border: none; padding: 8px 14px; margin: 2px; /* Adjusted padding and margin */
        cursor: pointer; font-size: 0.95rem; border-radius: 5px; color: #1565c0; /* Adjusted font size */
        transition: background-color 0.3s ease, transform 0.1s ease;
    }
    .tablinks:hover {
        background-color: #cce0ff;
        transform: translateY(-1px); /* More subtle hover */
    }
    .tablinks.active {
        background-color: #1565c0; color: #fff; font-weight: bold;
        box-shadow: 0 2px 4px rgba(0,0,0,0.15); /* Lighter shadow */
        transform: translateY(0px); /* No lift on active */
    }
    .tabcontent { display: none; padding-top: 15px; /* Adjusted padding */ }
    .tabcontent.active { display: block; }
    
    /* Author Box specific adjustments */
    #authorBox {
        animation: fadeIn 1s ease;
        transition: box-shadow 0.3s;
    }
    #authorBox:hover {
        box-shadow: 0 0 15px #1976d2, 0 2px 6px rgba(30, 64, 175, 0.1); /* Slightly reduced hover shadow */
    }
    @keyframes fadeIn {
        from {opacity: 0; transform: translateY(-15px);} /* Adjusted for smaller scale */
        to {opacity: 1; transform: translateY(0);}
    }

    /* DataTables custom styling for better appearance */
    .dataTables_wrapper { font-size: 0.85rem; } /* Slightly smaller than body for table controls */
    table.dataTable thead th {
        background-color: #e3f2fd;
        color: #0d47a1;
        font-weight: bold; /* Bold as requested */
        text-align: center; /* Centered as requested */
        padding: 10px 15px !important; /* Adjusted padding */
        border-bottom: 1px solid #a7d9f7 !important; /* Cleaner border */
        border-right: 1px solid #eef2f6; /* Vertical border */
    }
    table.dataTable tbody td {
        padding: 8px 15px !important; /* Adjusted padding */
        border-bottom: 1px solid #eef2f6; /* Cleaner border */
        border-right: 1px solid #f4f7f6; /* Subtle vertical border */
        white-space: nowrap; /* Ensures no text wrapping */
    }
    table.dataTable tbody tr:nth-child(even) { background-color: #f7fbff; }
    table.dataTable tbody tr:hover { background-color: #e0f0ff; }
    table.dataTable { border-spacing: 0; } /* Ensure borders are tight */
    table.dataTable thead th:last-child,
    table.dataTable tbody td:last-child {
        border-right: none; /* No border on the last column */
    }


    /* Input and Select styling for DataTables controls */
    .dataTables_wrapper .dataTables_filter input,
    .dataTables_wrapper .dataTables_length select,
    .column-filter-select {
        border: 1px solid #cbd5e0;
        border-radius: 0.375rem; /* rounded-md */
        padding: 0.4rem 0.6rem; /* py-2 px-3 adjusted */
        margin-left: 0.4rem;
        margin-right: 0.4rem;
        background-color: #ffffff;
        font-size: 0.8rem; /* Adjusted font size */
        box-shadow: inset 0 1px 2px rgba(0,0,0,0.06);
        transition: border-color 0.2s ease-in-out, box-shadow 0.2s ease-in-out;
    }
    .dataTables_wrapper .dataTables_filter input:focus,
    .dataTables_wrapper .dataTables_length select:focus,
    .column-filter-select:focus {
        border-color: #3b82f6; /* blue-500 */
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.25); /* ring-blue-200 */
        outline: none;
    }

    /* Buttons for pagination and DataTables export buttons */
    .dataTables_wrapper .dataTables_paginate .paginate_button,
    .dt-buttons .dt-button {
        background-color: #4299e1; /* blue-500 */
        color: white;
        padding: 0.4rem 0.8rem; /* Adjusted padding */
        border-radius: 0.375rem;
        cursor: pointer;
        border: none;
        margin: 0 0.2rem; /* Adjusted margin */
        transition: background-color 0.2s ease-in-out;
        font-size: 0.8rem; /* Adjusted font size */
    }
    .dataTables_wrapper .dataTables_paginate .paginate_button:hover,
    .dt-buttons .dt-button:hover {
        background-color: #3182ce; /* blue-600 */
    }
    .dataTables_wrapper .dataTables_paginate .paginate_button.current {
        background-color: #2b6cb0; /* blue-700 */
        font-weight: bold;
    }
    .dataTables_wrapper .dataTables_info {
        font-size: 0.8rem; /* Adjusted font size */
        color: #6b7280;
        margin-top: 1rem;
    }

    /* Layout for column filters */
    .column-filters-container {
        display: flex;
        flex-wrap: wrap;
        gap: 0.8rem; /* Adjusted gap */
        margin-bottom: 1rem;
        padding: 0.8rem; /* Adjusted padding */
        background-color: #edf2f7; /* gray-100 */
        border-radius: 0.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .column-filters-container label {
        font-weight: 500;
        color: #2d3748;
        display: flex;
        align-items: center;
        font-size: 0.85rem; /* Adjusted font size */
    }

    body {
    font-family: 'Inter', sans-serif;
    font-size: 0.875rem;
    /* Modern business background image, blurred */
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
    filter: blur(4px) brightness(0.8); /* Less blur, slightly brighter */
    width: 100vw;
    height: 100vh;
}
    body::after {
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    z-index: -1;
    background: rgba(255,255,255,0.35); /* White overlay for readability */
}
.tabcontent, .ao-card, .container, .df-tab-content, .tab-header {
    background: rgba(255,255,255,0.4); /* More transparent */
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(30,64,175,0.10);
    padding: 24px;
    margin-bottom: 30px;
}
}
</style>
"""

# --- Final HTML Assembly ---
# Assemble the complete HTML report with all generated components.
now_str = datetime.now().strftime("%Y-%m-%d %H:%M") # Current timestamp for report generation.
final_html = f"""
<html>
<head>
<title>🔧 Operational Status Summary: Sagaing & Kachin</title>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.min.css"/>
<link rel="stylesheet" href="https://cdn.datatables.net/buttons/2.4.2/css/buttons.dataTables.min.css"/>
{pro_table_style}
</head>
<body>
    {author_box_html}
<h1 style="font-size:2rem;">🔧 Operational Status Summary: Sagaing & Kachin</h1>
<p style="font-size:0.95rem;"><strong>Reported on:</strong> {now_str}</p>
<div class="tab-header">{''.join(tab_buttons)}</div>
{''.join(tab_contents)}
{slicer_html}
{arnd_slicer_html}
{detail_data_modal_html} <!-- Include the new detail data modal here -->
{js_script}
<footer style="margin-top: 40px; padding-top: 15px; border-top: 1px solid #e0e0e0; color: #666; font-size: 0.8rem; text-align: center;">
    Report prepared by <strong>Kaung Myat Kyaw</strong><br>
    <em>Data Analyst</em><br>
    📞 <a href="tel:09446844590" style="color:#1565c0; text-decoration:none;">09446844590</a> &nbsp;|&nbsp;
    📧 <a href="mailto:kaungmyatkyaw@myanmarpadauk.com" style="color:#1565c0; text-decoration:none;">kaungmyatkyaw@myanmarpadauk.com</a>
</footer>
</body>
</html>
"""

# ==== Paths and File Saving ====
today = datetime.now().strftime("%Y-%m-%d")  # Current date for file naming.
# Define the output directory and file path for the main report.
output_dir = r'D:\My Base\Share_Analyst'
os.makedirs(output_dir, exist_ok=True) # Ensure directory exists
output_path = os.path.join(output_dir, f"site_perf_overview_trial-{today}.html")
with open(output_path, "w", encoding="utf-8") as f:
    f.write(final_html)
print(f"✅ Operational Status Summary saved: {output_path}")

# Automatically open the generated report in the default web browser.
webbrowser.open(f"file://{output_path}")
