import pandas as pd
import datetime
import os
import re
import logging
from pathlib import Path
import folium
from folium.plugins import MiniMap, Fullscreen, MeasureControl, HeatMap
import branca.element
import shutil # Added for file copying

# --- Configuration Constants ---
# Define the base directory for your B2B project.
# This should be the parent directory containing 'Share_Analyst/B2B'.
# IMPORTANT: Change this path to your actual base directory.
BASE_DIR = Path('D:/My Base/Share_Analyst/B2B')

EXCEL_FILE_PATH = BASE_DIR / 'ME' / 'To Do' / 'B2B_summary.xlsx'
EXCEL_SHEET_NAME = 'Records'
HTML_REPORT_DIR = BASE_DIR / 'ME' / 'To Do'
GALLERY_DIR = BASE_DIR / 'Gallery'

# Configure logging for better output management
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Columns to apply cleaning (case-insensitive, spaces normalized)
TARGET_CLEANING_COLUMNS = [
    "CASE TITLE", "CIRCUIT ID", "SERVICE TERMINATION POINT", "ADDRESS",
    "Status", "STATE/REGION", "TOWNSHIP", "TICKET STATUS",
    "SUB-ROOT CAUSE (EXTERNAL AFFECT)", "ROOT CAUSE (DIRECT AFFECT)",
    "ACTION TAKEN", "MATERIAL REPLACEMENT (IF HAS)",
    "TYPE OF AFFECTED SERVICE", "WORK ORDER FROM(FSC/TSC/FM1 ETC...)",
    "PIC", "DT_RANGE", "REPORTED"
]

# Columns to display in the Management Report
MANAGEMENT_REPORT_COLS = [
    "CASE TITLE", "CIRCUIT ID", "STATUS", "DT_RANGE", "DT_DAYS", "DT_WEEKS",
    "FOLLOW_UP_CONDITION", "RECENT_CONVER", "PIC", "TOWNSHIP",
    "COMPLAINT ISSUE TIME", "RECOVERY TIME", "DURATION"
]

# Key columns for Folium map popups
MAP_POPUP_KEY_COLUMNS = [
    "CASE TITLE", "CIRCUIT ID", "STATUS", "STATE/REGION", "TOWNSHIP",
    "PIC", "COMPLAINT ISSUE TIME", "RECOVERY TIME", "TICKET STATUS",
    "ROOT CAUSE (DIRECT AFFECT)", "ACTION TAKEN", "TYPE OF AFFECTED SERVICE",
    "DT_RANGE", "DT_DAYS", "DT_WEEKS", "REPORTED"
]

# --- Helper Functions ---

def normalize_header(text: str) -> str:
    """Normalizes column headers for consistent matching."""
    return text.strip().upper().replace('\xa0', ' ')

def clean_text_value(value: any) -> any:
    """Cleans and uppercases string values, preserving non-string types."""
    if not isinstance(value, str):
        return value
    cleaned = re.sub(r'[\x00-\x1F]+', '', value).strip()
    return cleaned.upper()

def parse_excel_date(val: any) -> datetime.date | None:
    """Parses various Excel date formats into a datetime.date object."""
    if isinstance(val, (datetime.datetime, datetime.date)):
        return val.date() if isinstance(val, datetime.datetime) else val
    try:
        # Try common date formats
        if isinstance(val, str):
            for fmt in ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d", "%m/%d/%Y", "%d-%m-%Y"]:
                try:
                    return datetime.datetime.strptime(val, fmt).date()
                except ValueError:
                    continue
        return None
    except Exception as e:
        logging.debug(f"Could not parse date '{val}': {e}")
        return None

def fmt_dt(dt: any) -> str:
    """Formats datetime objects for display in reports."""
    if dt is None or pd.isna(dt):
        return "N/A"
    if isinstance(dt, pd.Timestamp):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    if isinstance(dt, datetime.datetime):
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    return str(dt)

# --- Core Data Processing Functions ---

def load_and_preprocess_data(file_path: Path, sheet_name: str) -> pd.DataFrame:
    """
    Loads data from an Excel file, cleans specified text columns,
    and calculates 'REPORT_IN' based on weekly ranges.

    Args:
        file_path (Path): Path to the Excel file.
        sheet_name (str): Name of the sheet to load.

    Returns:
        pd.DataFrame: The processed DataFrame.
    """
    logging.info(f"Loading data from {file_path}...")
    try:
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        logging.info("Data loaded successfully.")
    except FileNotFoundError:
        logging.error(f"Error: Excel file not found at {file_path}")
        return pd.DataFrame()
    except Exception as e:
        logging.error(f"Error loading Excel file: {e}")
        return pd.DataFrame()

    # Ensure DT_DAYS and DT_WEEKS are numeric
    df['DT_DAYS'] = pd.to_numeric(df["DT_DAYS"], errors='coerce').round(2)
    df['DT_WEEKS'] = pd.to_numeric(df["DT_WEEKS"], errors='coerce').round(2)

    # Normalize DataFrame columns to uppercase for consistent access
    df.columns = [normalize_header(col) for col in df.columns]

    # Identify columns for cleaning
    cols_to_clean_indices = []
    for col_name in TARGET_CLEANING_COLUMNS:
        normalized_col_name = normalize_header(col_name)
        if normalized_col_name in df.columns:
            cols_to_clean_indices.append(df.columns.get_loc(normalized_col_name))
        else:
            logging.warning(f"Column '{col_name}' (normalized to '{normalized_col_name}') not found in DataFrame. Skipping cleaning.")

    # Apply cleaning to identified columns
    logging.info("Applying text cleaning and uppercasing...")
    for col_idx in cols_to_clean_indices:
        col_name = df.columns[col_idx]
        df[col_name] = df[col_name].apply(clean_text_value)
    logging.info("Text cleaning complete.")

    # Convert 'COMPLAINT ISSUE TIME' to datetime objects
    df['COMPLAINT ISSUE TIME'] = pd.to_datetime(df['COMPLAINT ISSUE TIME'], errors='coerce')
    df['RECOVERY TIME'] = pd.to_datetime(df['RECOVERY TIME'], errors='coerce')

    # Calculate 'REPORT_IN' based on weekly ranges
    logging.info("Calculating 'REPORT_IN' (weekly ranges)...")
    if 'COMPLAINT ISSUE TIME' in df.columns:
        valid_complaint_dates = df['COMPLAINT ISSUE TIME'].dropna().apply(lambda x: x.date()).tolist()
        if valid_complaint_dates:
            last_date = max(valid_complaint_dates)
        else:
            last_date = datetime.date.today() # Fallback if no valid dates

        start_date = datetime.date(2022, 4, 2)
        while start_date.weekday() != 4:  # 4 = Friday
            start_date += datetime.timedelta(days=1)

        week_ranges = []
        current_start = start_date
        while current_start <= last_date:
            current_end = current_start + datetime.timedelta(days=6)  # Thursday
            week_ranges.append((current_start, current_end))
            current_start = current_end + datetime.timedelta(days=1)

        def get_week_label(date_val):
            if pd.isna(date_val):
                return ""
            date_val = date_val.date() # Ensure it's a date object
            for i, (w_start, w_end) in enumerate(week_ranges):
                if w_start <= date_val <= w_end:
                    return f"Week {i+1}: {w_start} to {w_end}"
            return ""

        df['REPORT_IN'] = df['COMPLAINT ISSUE TIME'].apply(get_week_label)
    else:
        logging.warning("'COMPLAINT ISSUE TIME' column not found. Cannot calculate 'REPORT_IN'.")
        df['REPORT_IN'] = '' # Add empty column if missing

    logging.info("Data preprocessing complete.")
    return df

def generate_b2b_map(df: pd.DataFrame, user_status: str, reported_filter: str, output_dir: Path):
    """
    Generates an interactive Folium map with case markers.

    Args:
        df (pd.DataFrame): The filtered DataFrame containing case data.
        user_status (str): The status used for filtering (e.g., 'pending').
        reported_filter (str): The 'REPORTED' filter (e.g., 'ME', 'HANDOVER', 'ALL').
        output_dir (Path): Directory to save the HTML map.
    """
    logging.info(f"Generating map for Status: '{user_status}', Reported: '{reported_filter}'...")

    base_filter = (
        df['LAT'].notna() &
        df['LONG'].notna() &
        df['STATUS'].notna() &
        df['REPORTED'].notna() &
        (df['STATUS'].astype(str).str.lower() == user_status.lower())
    )

    if reported_filter.upper() == 'ALL':
        filtered_map_df = df[base_filter]
    else:
        filtered_map_df = df[base_filter & (df['REPORTED'].astype(str).str.upper() == reported_filter.upper())]

    if filtered_map_df.empty:
        logging.warning("No data found for map generation with the specified criteria.")
        return

    # Create map centered on mean location
    m = folium.Map(
        location=[filtered_map_df['LAT'].mean(), filtered_map_df['LONG'].mean()],
        zoom_start=7,
        tiles='OpenStreetMap'
    )

    # Add markers with detailed popups
    for _, row in filtered_map_df.iterrows():
        popup_html = "<div style='font-size:15px; color:#222; background:#fff; padding:8px 12px;'>"
        for col in MAP_POPUP_KEY_COLUMNS:
            val = row.get(col, "")
            if pd.isna(val):
                val = ""
            elif isinstance(val, pd.Timestamp):
                val = val.strftime("%Y-%m-%d %H:%M:%S")
            popup_html += f"<b>{col}:</b> {val}<br>"
        popup_html += "</div>"

        folium.Marker(
            location=[row['LAT'], row['LONG']],
            popup=folium.Popup(popup_html, max_width=400),
            tooltip=folium.Tooltip(
                f"<span style='font-size:15px; color:#fff; background:#d9534f; padding:4px 8px; border-radius:5px;'>{row.get('CASE TITLE', '')}</span>",
                sticky=True
            )
        ).add_to(m)

    # Add header and info box
    header_html = f"""
        <div style='
            background-color:#1a3e72;
            color:#fff;
            padding:16px 0 8px 0;
            text-align:center;
            font-size:22px;
            font-weight:bold;
            border-radius:10px 10px 0 0;
            box-shadow:0 2px 8px #0003;
            margin-bottom:0;
        '>
            B2B Complaints Map
        </div>
    """
    m.get_root().html.add_child(branca.element.Element(header_html))

    info_html = f"""
        <div style='
            background:#f8f9fa;
            color:#222;
            padding:10px 18px;
            font-size:16px;
            border-radius:0 0 10px 10px;
            margin-bottom:18px;
            border-bottom:2px solid #1a3e72;
            box-shadow:0 2px 8px #0001;
        '>
            <b>Status:</b> <span style='color:#1a3e72'>{user_status.capitalize()}</span> &nbsp; | &nbsp;
            <b>REPORTED:</b> <span style='color:#d9534f'>{reported_filter}</span> &nbsp; | &nbsp;
            <b>Cases:</b> <span style='color:#5cb85c'>{len(filtered_map_df)}</span>
        </div>
    """
    m.get_root().html.add_child(branca.element.Element(info_html))

    # Add minimap, fullscreen, measure tool, and layer control
    minimap = MiniMap(toggle_display=True, position="bottomright")
    m.add_child(minimap)
    Fullscreen(position="topright").add_to(m)
    m.add_child(MeasureControl(primary_length_unit='kilometers', primary_color='#ff0000', active_color='#ff0000'))
    folium.LayerControl().add_to(m)

    # Add a heatmap if enough points
    if len(filtered_map_df) > 1:
        heat_data = filtered_map_df[['LAT', 'LONG']].dropna().values.tolist()
        HeatMap(heat_data, radius=18, blur=12, min_opacity=0.3).add_to(m)

    map_filename = output_dir / f"B2B_complaints_map_{user_status}_{reported_filter}.html"
    try:
        m.save(map_filename)
        logging.info(f"Map saved as {map_filename}. Open it in your browser to view.")
        # Note: In a standalone script, webbrowser.open might open a new tab.
        # import webbrowser
        # webbrowser.open(f'file://{map_filename.resolve()}')
    except Exception as e:
        logging.error(f"Failed to save map: {e}")

def generate_single_html_report(df: pd.DataFrame, from_dt_val: datetime.datetime | None,
                               to_dt_val: datetime.datetime | None,
                               reported_val: str, status_val: str,
                               township_val: str, pic_val: str, circuit_val: str,
                               output_dir: Path):
    """
    Generates a single HTML report for the filtered B2B cases.

    Args:
        df (pd.DataFrame): The filtered DataFrame.
        from_dt_val (datetime.datetime | None): Start date for filtering.
        to_dt_val (datetime.datetime | None): End date for filtering.
        reported_val (str): Value of the 'REPORTED' filter.
        status_val (str): Value of the 'STATUS' filter.
        township_val (str): Value of the 'TOWNSHIP' filter.
        pic_val (str): Value of the 'PIC' filter.
        circuit_val (str): Value of the 'CIRCUIT ID' filter.
        output_dir (Path): Directory to save the HTML report.
    """
    logging.info("Generating single HTML report...")

    from_str = from_dt_val.strftime("%Y-%m-%d") if from_dt_val else "all"
    to_str = to_dt_val.strftime("%Y-%m-%d") if to_dt_val else "all"

    html_filename = output_dir / f"report_{from_str}_to_{to_str}_{status_val}.html"

    html_content = f"""
    <html>
    <head>
        <meta charset='utf-8'>
        <title>B2B ACCOMPLISHMENT REPORT</title>
        <style>
            body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
            .header {{ background: #1976d2; color: #fff; padding: 18px 24px 10px 24px; border-radius: 10px 10px 0 0; font-size: 22px; font-weight: bold; box-shadow: 0 2px 8px #0002; margin-bottom: 0; letter-spacing: 1px; text-align: center; }}
            .info-bar {{ background: #f5f7fa; color: #1976d2; padding: 10px 24px 14px 24px; border-radius: 0 0 10px 10px; font-size: 15px; margin-bottom: 18px; border-bottom: 2px solid #1976d2; box-shadow: 0 2px 8px #0001; text-align: center; }}
            .section-title {{ color: #1976d2; font-weight: 700; font-size: 20px; margin: 28px 0 12px 0; letter-spacing: 1px; border-left: 6px solid #1976d2; padding-left: 10px; background: linear-gradient(90deg,#f5f7fa 60%,#e3eaf2 100%); border-radius: 6px; }}
            .case-box {{ background: #f5f7fa; color: #222; margin: 14px 0; padding: 16px 24px; border-left: 6px solid #1976d2; border-radius: 8px; box-shadow: 0 2px 8px #0001; font-size: 15px; line-height: 1.7; }}
            .case-box.other {{ border-left: 6px solid #90a4ae; background: linear-gradient(90deg,#f8f9fa 80%,#e3eaf2 100%); }}
            .case-label {{ font-weight: bold; color: #1976d2; }}
            .case-label.status {{ color: #d84315; }} .case-label.township {{ color: #1565c0; }} .case-label.pic {{ color: #6d4c41; }} .case-label.complaint {{ color: #1976d2; }}
            .case-label.range, .case-label.days, .case-label.weeks {{ color: #607d8b; }}
            .case-label.follow {{ color: #ff9800; background: #ff9800; color: #fff; padding: 2px 8px; border-radius: 4px; margin-right: 6px;}}
            .case-label.remark {{ color: #607d8b; background: #607d8b; color: #fff; padding: 2px 8px; border-radius: 4px; margin-right: 6px;}}
            .case-title {{ font-size: 17px; color: #1976d2; font-weight: 700; margin-bottom: 4px; word-break: break-all; }}
            .case-title.other {{ color: #607d8b; }}
            .summary-box {{ margin: 18px 0 24px 0; padding: 18px 24px; background: linear-gradient(90deg,#e3eaf2 0,#f5f7fa 100%); border-radius: 12px; box-shadow: 0 2px 8px #0001; font-size: 15px; }}
            .summary-label {{ color: #1976d2; font-size: 16px; font-weight: bold; }}
            .summary-label.township {{ color: #607d8b; }}
            .summary-count {{ color: #1976d2; font-weight: 600; }}
            .summary-count.township {{ color: #607d8b; }}
            .toggle-btn {{ margin-top: 8px; background: #e3eaf2; color: #1976d2; border: none; border-radius: 4px; padding: 4px 12px; cursor: pointer; font-size: 13px; }}
            .recent-conv {{ display: none; margin-top: 8px; color: #607d8b; font-size: 13px; background: #e3eaf2; padding: 10px; border-radius: 4px; white-space: pre-wrap; word-break: break-all; }}
        </style>
        <script>
            function toggleConv(btn) {{
                var d = btn.nextElementSibling;
                d.style.display = d.style.display === 'block' ? 'none' : 'block';
            }}
        </script>
    </head>
    <body>
        <div class='header'>B2B ACCOMPLISHMENT REPORT</div>
        <div class='info-bar'>
            <b>Date Range:</b> <span style='color:#1976d2;'>{fmt_dt(from_dt_val)}</span> &rarr;
            <span style='color:#1976d2;'>{fmt_dt(to_dt_val)}</span><br>
            <b>Reported:</b> <span style='color:#388e3c;'>{reported_val}</span> &nbsp;
            <b>Status:</b> <span style='color:#d84315;'>{status_val}</span> &nbsp;
            <b>Township:</b> <span style='color:#1565c0;'>{township_val}</span> &nbsp;
            <b>PIC:</b> <span style='color:#6d4c41;'>{pic_val}</span> &nbsp;
            <b>Circuit ID:</b> <span style='color:#8e24aa;'>{circuit_val}</span><br>
            <span style='color:#607d8b;'>{len(df)} case(s) in this report</span>
        </div>
    """

    priority_result = df[
        (df["REPORTED"].astype(str).str.upper() == "ME") &
        (df["STATUS"].astype(str).str.upper().isin(["PENDING", "ONGOING"]))
    ]

    if priority_result.empty:
        html_content += "<div style='color:#888;font-size:16px;margin:18px 0;text-align:center;'>No priority (ME, Pending/Ongoing) cases in this date range.</div>"
    else:
        html_content += "<div class='section-title'>Priority List (REPORTED = ME, Status = Pending/Ongoing)</div>"
        for _, row in priority_result.iterrows():
            html_content += f"""
            <div class='case-box'>
                <div class='case-title'>{row.get("CASE TITLE", "")}</div>
                <div>
                    <span class='case-label status'>Status:</span> <b>{row.get("STATUS", "")}</b> &nbsp;
                    <span class='case-label township'>Township:</span> {row.get("TOWNSHIP", "")} &nbsp;
                    <span class='case-label pic'>PIC:</span> {row.get("PIC", "")}
                </div>
                <div>
                    <span class='case-label complaint'>Complaint Time:</span> {fmt_dt(row.get("COMPLAINT ISSUE TIME", ""))} &nbsp;
                    <span class='case-label complaint'>Recovery Time:</span> {fmt_dt(row.get("RECOVERY TIME", ""))} &nbsp;
                    <span class='case-label complaint'>Duration:</span> {row.get("DURATION", "N/A") if pd.notnull(row.get("DURATION")) else 'N/A'} &nbsp;
                    <span class='case-label range'>DT_RANGE:</span> {row.get("DT_RANGE", "")} &nbsp;
                    <span class='case-label weeks'>DT_WEEKS:</span> {row.get("DT_WEEKS", "")}
                </div>
                <div>
                    <span class='case-label'>Address:</span> {row.get("ADDRESS", "") if pd.notnull(row.get("ADDRESS")) else '<span style="color:#bbb;">N/A</span>'}
                </div>
                <div>
                    <span class='case-label follow'>Follow Up:</span>
                    <span style='color:#ff9800; font-weight:600;'>{row.get("FOLLOW_UP_CONDITION", "") if pd.notnull(row.get("FOLLOW_UP_CONDITION")) and str(row.get("FOLLOW_UP_CONDITION")).strip() else '<span style="color:#bbb;">N/A</span>'}</span>
                </div>
                <div>
                    <span class='case-label remark'>Remark:</span>
                    <span style='color:#607d8b; font-weight:600;'>{row.get("REMARK", "") if pd.notnull(row.get("REMARK")) and str(row.get("REMARK")).strip() else '<span style="color:#bbb;">N/A</span>'}</span>
                </div>
                {f"<button class='toggle-btn' onclick='toggleConv(this)'>Show/Hide Recent Conversation</button><div class='recent-conv'>{str(row.get('RECENT_CONVER', '')).replace(chr(10), '<br>') if pd.notnull(row.get('RECENT_CONVER')) else ''}</div>" if pd.notnull(row.get('RECENT_CONVER')) and str(row.get('RECENT_CONVER')).strip() else ""}
            </div>
            """

    # Other List
    other_reported_mask = df["REPORTED"].astype(str).str.upper() != "ME" if reported_val.upper() == "ALL" else df["REPORTED"].astype(str) == reported_val
    other_status_mask = df["STATUS"].astype(str).str.upper() != "COMPLETED" if status_val.upper() == "ALL" else df["STATUS"].astype(str) == status_val
    other_result = df[other_reported_mask & other_status_mask]

    if other_result.empty:
        html_content += "<div style='color:#888;font-size:16px;margin:18px 0;text-align:center;'>No other cases in this date range.</div>"
    else:
        status_counts = other_result['STATUS'].value_counts().to_dict()
        township_counts = other_result['TOWNSHIP'].value_counts().to_dict()
        html_content += f"""
        <div class='summary-box'>
            <div style='margin-bottom:6px;'>
                <span class='summary-label'>Status Summary:</span>
                <span style='margin-left:8px;'>
                    {" | ".join([f"{k}: <span class='summary-count'>{v}</span>" for k, v in status_counts.items()])}
                </span>
            </div>
            <div>
                <span class='summary-label township'>Township Summary:</span>
                <span style='margin-left:8px;'>
                    {" | ".join([f"{k}: <span class='summary-count township'>{v}</span>" for k, v in township_counts.items()])}
                </span>
            </div>
        </div>
        """
        html_content += "<div class='section-title' style='color:#607d8b;border-left:6px solid #90a4ae;'>Other List (Handovered)</div>"
        for _, row in other_result.iterrows():
            html_content += f"""
            <div class='case-box other'>
                <div class='case-title other'>{row.get("CASE TITLE", "")}</div>
                <div>
                    <span class='case-label status'>Status:</span> <b style='color:#607d8b'>{row.get("STATUS", "")}</b> &nbsp;
                    <span class='case-label township'>Township:</span> {row.get("TOWNSHIP", "")} &nbsp;
                    <span class='case-label pic'>PIC:</span> {row.get("PIC", "")}
                </div>
                <div>
                    <span class='case-label complaint'>Complaint Time:</span> {fmt_dt(row.get("COMPLAINT ISSUE TIME", ""))} &nbsp;
                    <span class='case-label complaint'>Recovery Time:</span> {fmt_dt(row.get("RECOVERY TIME", ""))} &nbsp;
                    <span class='case-label complaint'>Duration:</span> {row.get("DURATION", "N/A") if pd.notnull(row.get("DURATION")) else 'N/A'} &nbsp;
                    <span class='case-label range'>DT_RANGE:</span> {row.get("DT_RANGE", "")} &nbsp;
                    <span class='case-label weeks'>DT_WEEKS:</span> {row.get("DT_WEEKS", "")}
                </div>
                <div>
                    <span class='case-label'>Address:</span> {row.get("ADDRESS", "") if pd.notnull(row.get("ADDRESS")) and str(row.get("ADDRESS")).strip() else '<span style="color:#bbb;">N/A</span>'}
                </div>
                <div>
                    <span class='case-label follow'>Follow Up:</span>
                    <span style='color:#ff9800; font-weight:600;'>{row.get("FOLLOW_UP_CONDITION", "") if pd.notnull(row.get("FOLLOW_UP_CONDITION")) and str(row.get("FOLLOW_UP_CONDITION")).strip() else '<span style="color:#bbb;">N/A</span>'}</span>
                </div>
                <div>
                    <span class='case-label remark'>Remark:</span>
                    <span style='color:#607d8b; font-weight:600;'>{row.get("REMARK", "") if pd.notnull(row.get("REMARK")) and str(row.get("REMARK")).strip() else '<span style="color:#bbb;">N/A</span>'}</span>
                </div>
                {f"<button class='toggle-btn' onclick='toggleConv(this)'>Show/Hide Recent Conversation</button><div class='recent-conv'>{str(row.get('RECENT_CONVER', '')).replace(chr(10), '<br>') if pd.notnull(row.get('RECENT_CONVER')) else ''}</div>" if pd.notnull(row.get('RECENT_CONVER')) and str(row.get('RECENT_CONVER')).strip() else ""}
            </div>
            """
    html_content += "</body></html>"

    try:
        with open(html_filename, "w", encoding="utf-8") as f:
            f.write(html_content)
        # Corrected: Use html_filename instead of html_full_path
        logging.info(f"B2B ACCOMPLISHMENT REPORT exported as HTML to '{html_filename.name}'")
    except OSError as e:
        logging.error(f"Failed to export HTML report. Error: {e}")
        # Corrected: Use html_filename instead of html_full_path
        logging.error(f"Filename attempted: '{html_filename}'")

def generate_grouped_html_reports(df: pd.DataFrame, from_dt_val: datetime.datetime | None,
                                 to_dt_val: datetime.datetime | None, output_dir: Path):
    """
    Generates separate HTML reports, grouped by Township and Status.

    Args:
        df (pd.DataFrame): The filtered DataFrame.
        from_dt_val (datetime.datetime | None): Start date for filtering.
        to_dt_val (datetime.datetime | None): End date for filtering.
        output_dir (Path): Directory to save the HTML reports.
    """
    logging.info("Generating separate grouped reports (by Township and Status)...")

    from_str = from_dt_val.strftime("%Y-%m-%d") if from_dt_val else "all"
    to_str = to_dt_val.strftime("%Y-%m-%d") if to_dt_val else "all"

    if df.empty:
        logging.warning("No data available to generate grouped reports.")
        return

    unique_combinations = df[['TOWNSHIP', 'STATUS']].drop_duplicates()

    if unique_combinations.empty:
        logging.warning("No unique Township-Status combinations found in the filtered data.")
        return

    for _, combo_row in unique_combinations.iterrows():
        current_township = combo_row['TOWNSHIP']
        current_status = combo_row['STATUS']

        current_group_df = df[
            (df['TOWNSHIP'] == current_township) &
            (df['STATUS'] == current_status)
        ].copy()

        if current_group_df.empty:
            continue

        # Sanitize names for filename
        township_for_filename = str(current_township).replace(' ', '_').replace('/', '_').replace('\\', '_')
        status_for_filename = str(current_status).replace(' ', '_').replace('/', '_').replace('\\', '_')

        report_filename = f"{township_for_filename}_{status_for_filename}_{from_str}_to_{to_str}.html"
        html_full_path = output_dir / report_filename

        html_content = f"""
        <html>
        <head>
            <meta charset='utf-8'>
            <title>B2B Accomplishment Report - {current_township} ({current_status})</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
                .header {{ background: #1976d2; color: #fff; padding: 18px 24px 10px 24px; border-radius: 10px; font-size: 24px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.2); margin-bottom: 20px; text-align: center; letter-spacing: 1px; }}
                .info-bar {{ background: #e3eaf2; color: #1976d2; padding: 15px 25px; border-radius: 8px; font-size: 16px; margin-bottom: 30px; border: 1px solid #c0d9ed; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }}
                .group-section {{ margin-bottom: 40px; border: 1px solid #d0e0f0; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); background-color: #ffffff; }}
                .group-header {{ background: linear-gradient(90deg, #1976d2 0%, #2196f3 100%); color: #fff; padding: 15px 25px; font-size: 20px; font-weight: bold; border-bottom: 2px solid #1565c0; display: flex; justify-content: space-between; align-items: center; }}
                .group-header.status-group {{ background: linear-gradient(90deg, #d84315 0%, #ff5722 100%); border-bottom: 2px solid #bf360c; }}
                .group-header span {{ flex-grow: 1; }}
                .group-header .count {{ background-color: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 5px; font-size: 16px; }}
                .case-box {{ background: #fdfdfd; color: #333; margin: 15px 25px; padding: 18px 25px; border-left: 6px solid #2196f3; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); font-size: 14px; line-height: 1.6; }}
                .case-box.status-group {{ border-left: 6px solid #ff5722; }}
                .case-title {{ font-size: 18px; color: #1976d2; font-weight: 700; margin-bottom: 8px; word-break: break-all; }}
                .case-title.status-group {{ color: #d84315; }}
                .case-label {{ font-weight: bold; color: #424242; margin-right: 5px; }}
                .case-label.status {{ color: #d84315; }} .case-label.township {{ color: #1565c0; }} .case-label.pic {{ color: #6d4c41; }} .case-label.time {{ color: #00796b; }}
                .case-label.range, .case-label.days, .case-label.weeks {{ color: #607d8b; }}
                .case-label.follow {{ color: #ff9800; background: #ff9800; color: #fff; padding: 2px 8px; border-radius: 4px; margin-right: 6px;}}
                .case-label.remark {{ color: #607d8b; background: #607d8b; color: #fff; padding: 2px 8px; border-radius: 4px; margin-right: 6px;}}
                .detail-row {{ margin-bottom: 5px; }}
                .toggle-btn {{ margin-top: 10px; background: #e0e0e0; color: #333; border: none; border-radius: 5px; padding: 6px 15px; cursor: pointer; font-size: 13px; transition: background-color 0.3s ease; }}
                .toggle-btn:hover {{ background-color: #d0d0d0; }}
                .recent-conv {{ display: none; margin-top: 10px; color: #555; font-size: 13px; background: #f0f0f0; padding: 12px; border-radius: 5px; white-space: pre-wrap; word-break: break-all; border: 1px dashed #ccc; }}
            </style>
            <script>
                function toggleConv(btn) {{
                    var d = btn.nextElementSibling;
                    d.style.display = d.style.display === 'block' ? 'none' : 'block';
                }}
            </script>
        </head>
        <body>
            <div class='header'>B2B Accomplishment Report - {current_township} ({current_status})</div>
            <div class='info-bar'>
                <b>Date Range:</b> <span style='color:#1976d2;'>{fmt_dt(from_dt_val)}</span> &rarr;
                <span style='color:#1976d2;'>{fmt_dt(to_dt_val)}</span><br>
                <b>Township:</b> <span style='color:#1565c0;'>{current_township}</span> &nbsp;
                <b>Status:</b> <span style='color:#d84315;'>{current_status}</span> &nbsp;
                <span style='color:#607d8b;'>{len(current_group_df)} case(s) in this report</span>
            </div>
            <div class='group-section'>
                <div class='group-header'>
                    <span>Township: {current_township}</span>
                    <span class='count'>{len(current_group_df)} Cases</span>
                </div>
                <div class='group-header status-group'>
                    <span>Status: {current_status}</span>
                    <span class='count'>{len(current_group_df)} Cases</span>
                </div>
        """

        for _, row in current_group_df.iterrows():
            html_content += f"""
            <div class='case-box status-group'>
                <div class='case-title status-group'>{row.get("CASE TITLE", "")}</div>
                <div class='detail-row'>
                    <span class='case-label'>Circuit ID:</span> {row.get("CIRCUIT ID", "")} &nbsp;
                    <span class='case-label pic'>PIC:</span> {row.get("PIC", "")}
                </div>
                <div class='detail-row'>
                    <span class='case-label time'>Complaint Time:</span> {fmt_dt(row.get("COMPLAINT ISSUE TIME", ""))} &nbsp;
                    <span class='case-label time'>Recovery Time:</span> {fmt_dt(row.get("RECOVERY TIME", ""))} &nbsp;
                    <span class='case-label time'>Duration:</span> {row.get("DURATION", "N/A") if pd.notnull(row.get("DURATION")) else 'N/A'}
                </div>
                <div class='detail-row'>
                    <span class='case-label range'>DT_RANGE:</span> {row.get("DT_RANGE", "")} &nbsp;
                    <span class='case-label days'>DT_DAYS:</span> {row.get("DT_DAYS", "")} &nbsp;
                    <span class='case-label weeks'>DT_WEEKS:</span> {row.get("DT_WEEKS", "")}
                </div>
                <div class='detail-row'>
                    <span class='case-label'>Address:</span> {row.get("ADDRESS", "") if pd.notnull(row.get("ADDRESS")) and str(row.get("ADDRESS")).strip() else '<span style="color:#bbb;">N/A</span>'}
                </div>
                <div class='detail-row'>
                    <span class='case-label follow'>Follow Up:</span>
                    <span style='color:#ff9800; font-weight:600;'>{row.get("FOLLOW_UP_CONDITION", "") if pd.notnull(row.get("FOLLOW_UP_CONDITION")) and str(row.get("FOLLOW_UP_CONDITION")).strip() else '<span style="color:#bbb;">N/A</span>'}</span>
                </div>
                <div class='detail-row'>
                    <span class='case-label remark'>Remark:</span>
                    <span style='color:#607d8b; font-weight:600;'>{row.get("REMARK", "") if pd.notnull(row.get("REMARK")) and str(row.get("REMARK")).strip() else '<span style="color:#bbb;">N/A</span>'}</span>
                </div>
                {f"<button class='toggle-btn' onclick='toggleConv(this)'>Show/Hide Recent Conversation</button><div class='recent-conv'>{str(row.get('RECENT_CONVER', '')).replace(chr(10), '<br>') if pd.notnull(row.get('RECENT_CONVER')) else ''}</div>" if pd.notnull(row.get('RECENT_CONVER')) and str(row.get('RECENT_CONVER')).strip() else ""}
            </div>
            """
        html_content += "</div>" # Close group-section div
        html_content += "</body></html>"

        try:
            with open(html_full_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logging.info(f"Generated report: '{html_full_path.name}'")
        except OSError as e:
            logging.error(f"Failed to export '{html_full_path.name}'. Error: {e}")
    logging.info("All grouped reports generated!")

def generate_grouped_pic_status_reports(df: pd.DataFrame, from_dt_val: datetime.datetime | None,
                                      to_dt_val: datetime.datetime | None, output_dir: Path):
    """
    Generates separate HTML reports, grouped by PIC and Status.

    Args:
        df (pd.DataFrame): The filtered DataFrame.
        from_dt_val (datetime.datetime | None): Start date for filtering.
        to_dt_val (datetime.datetime | None): End date for filtering.
        output_dir (Path): Directory to save the HTML reports.
    """
    logging.info("Generating separate grouped reports (by PIC and Status)...")

    from_str = from_dt_val.strftime("%Y-%m-%d") if from_dt_val else "all"
    to_str = to_dt_val.strftime("%Y-%m-%d") if to_dt_val else "all"

    if df.empty:
        logging.warning("No data available to generate grouped reports.")
        return

    # Group by PIC and Status
    unique_combinations = df[['PIC', 'STATUS']].drop_duplicates()

    if unique_combinations.empty:
        logging.warning("No unique PIC-Status combinations found in the filtered data.")
        return

    for _, combo_row in unique_combinations.iterrows():
        current_pic = combo_row['PIC']
        current_status = combo_row['STATUS']

        # Filter data for the current PIC and Status combination
        current_group_df = df[
            (df['PIC'] == current_pic) &
            (df['STATUS'] == current_status)
        ].copy()

        if current_group_df.empty:
            continue

        # Sanitize names for filename
        pic_for_filename = str(current_pic).replace(' ', '_').replace('/', '_').replace('\\', '_')
        status_for_filename = str(current_status).replace(' ', '_').replace('/', '_').replace('\\', '_')

        report_filename = f"PIC_{pic_for_filename}_Status_{status_for_filename}_{from_str}_to_{to_str}.html"
        html_full_path = output_dir / report_filename

        html_content = f"""
        <html>
        <head>
            <meta charset='utf-8'>
            <title>B2B Accomplishment Report - PIC: {current_pic} (Status: {current_status})</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; margin: 0; padding: 20px; }}
                .header {{ background: #1976d2; color: #fff; padding: 18px 24px 10px 24px; border-radius: 10px; font-size: 24px; font-weight: bold; box-shadow: 0 4px 10px rgba(0,0,0,0.2); margin-bottom: 20px; text-align: center; letter-spacing: 1px; }}
                .info-bar {{ background: #e3eaf2; color: #1976d2; padding: 15px 25px; border-radius: 8px; font-size: 16px; margin-bottom: 30px; border: 1px solid #c0d9ed; box-shadow: 0 2px 5px rgba(0,0,0,0.1); text-align: center; }}
                .group-section {{ margin-bottom: 40px; border: 1px solid #d0e0f0; border-radius: 10px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); background-color: #ffffff; }}
                .group-header {{ background: linear-gradient(90deg, #1976d2 0%, #2196f3 100%); color: #fff; padding: 15px 25px; font-size: 20px; font-weight: bold; border-bottom: 2px solid #1565c0; display: flex; justify-content: space-between; align-items: center; }}
                .group-header.status-group {{ background: linear-gradient(90deg, #d84315 0%, #ff5722 100%); border-bottom: 2px solid #bf360c; }}
                .group-header span {{ flex-grow: 1; }}
                .group-header .count {{ background-color: rgba(255,255,255,0.2); padding: 5px 10px; border-radius: 5px; font-size: 16px; }}
                .case-box {{ background: #fdfdfd; color: #333; margin: 15px 25px; padding: 18px 25px; border-left: 6px solid #2196f3; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.08); font-size: 14px; line-height: 1.6; }}
                .case-box.status-group {{ border-left: 6px solid #ff5722; }}
                .case-title {{ font-size: 18px; color: #1976d2; font-weight: 700; margin-bottom: 8px; word-break: break-all; }}
                .case-title.status-group {{ color: #d84315; }}
                .case-label {{ font-weight: bold; color: #424242; margin-right: 5px; }}
                .case-label.status {{ color: #d84315; }} .case-label.township {{ color: #1565c0; }} .case-label.pic {{ color: #6d4c41; }} .case-label.time {{ color: #00796b; }}
                .case-label.range, .case-label.days, .case-label.weeks {{ color: #607d8b; }}
                .case-label.follow {{ color: #ff9800; background: #ff9800; color: #fff; padding: 2px 8px; border-radius: 4px; margin-right: 6px;}}
                .case-label.remark {{ color: #607d8b; background: #607d8b; color: #fff; padding: 2px 8px; border-radius: 4px; margin-right: 6px;}}
                .detail-row {{ margin-bottom: 5px; }}
                .toggle-btn {{ margin-top: 10px; background: #e0e0e0; color: #333; border: none; border-radius: 5px; padding: 6px 15px; cursor: pointer; font-size: 13px; transition: background-color 0.3s ease; }}
                .toggle-btn:hover {{ background-color: #d0d0d0; }}
                .recent-conv {{ display: none; margin-top: 10px; color: #555; font-size: 13px; background: #f0f0f0; padding: 12px; border-radius: 5px; white-space: pre-wrap; word-break: break-all; border: 1px dashed #ccc; }}
            </style>
            <script>
                function toggleConv(btn) {{
                    var d = btn.nextElementSibling;
                    d.style.display = d.style.display === 'block' ? 'none' : 'block';
                }}
            </script>
        </head>
        <body>
            <div class='header'>B2B Accomplishment Report - PIC: {current_pic} (Status: {current_status})</div>
            <div class='info-bar'>
                <b>Date Range:</b> <span style='color:#1976d2;'>{fmt_dt(from_dt_val)}</span> &rarr;
                <span style='color:#1976d2;'>{fmt_dt(to_dt_val)}</span><br>
                <b>PIC:</b> <span style='color:#6d4c41;'>{current_pic}</span> &nbsp;
                <b>Status:</b> <span style='color:#d84315;'>{current_status}</span> &nbsp;
                <span style='color:#607d8b;'>{len(current_group_df)} case(s) in this report</span>
            </div>
            <div class='group-section'>
                <div class='group-header'>
                    <span>PIC: {current_pic}</span>
                    <span class='count'>{len(current_group_df)} Cases</span>
                </div>
                <div class='group-header status-group'>
                    <span>Status: {current_status}</span>
                    <span class='count'>{len(current_group_df)} Cases</span>
                </div>
        """

        for _, row in current_group_df.iterrows():
            html_content += f"""
            <div class='case-box status-group'>
                <div class='case-title status-group'>{row.get("CASE TITLE", "")}</div>
                <div class='detail-row'>
                    <span class='case-label'>Circuit ID:</span> {row.get("CIRCUIT ID", "")} &nbsp;
                    <span class='case-label pic'>PIC:</span> {row.get("PIC", "")}
                </div>
                <div class='detail-row'>
                    <span class='case-label time'>Complaint Time:</span> {fmt_dt(row.get("COMPLAINT ISSUE TIME", ""))} &nbsp;
                    <span class='case-label time'>Recovery Time:</span> {fmt_dt(row.get("RECOVERY TIME", ""))} &nbsp;
                    <span class='case-label time'>Duration:</span> {row.get("DURATION", "N/A") if pd.notnull(row.get("DURATION")) else 'N/A'}
                </div>
                <div class='detail-row'>
                    <span class='case-label range'>DT_RANGE:</span> {row.get("DT_RANGE", "")} &nbsp;
                    <span class='case-label days'>DT_DAYS:</span> {row.get("DT_DAYS", "")} &nbsp;
                    <span class='case-label weeks'>DT_WEEKS:</span> {row.get("DT_WEEKS", "")}
                </div>
                <div class='detail-row'>
                    <span class='case-label'>Address:</span> {row.get("ADDRESS", "") if pd.notnull(row.get("ADDRESS")) and str(row.get("ADDRESS")).strip() else '<span style="color:#bbb;">N/A</span>'}
                </div>
                <div class='detail-row'>
                    <span class='case-label follow'>Follow Up:</span>
                    <span style='color:#ff9800; font-weight:600;'>{row.get("FOLLOW_UP_CONDITION", "") if pd.notnull(row.get("FOLLOW_UP_CONDITION")) and str(row.get("FOLLOW_UP_CONDITION")).strip() else '<span style="color:#bbb;">N/A</span>'}</span>
                </div>
                <div class='detail-row'>
                    <span class='case-label remark'>Remark:</span>
                    <span style='color:#607d8b; font-weight:600;'>{row.get("REMARK", "") if pd.notnull(row.get("REMARK")) and str(row.get("REMARK")).strip() else '<span style="color:#bbb;">N/A</span>'}</span>
                </div>
                {f"<button class='toggle-btn' onclick='toggleConv(this)'>Show/Hide Recent Conversation</button><div class='recent-conv'>{str(row.get('RECENT_CONVER', '')).replace(chr(10), '<br>') if pd.notnull(row.get('RECENT_CONVER')) else ''}</div>" if pd.notnull(row.get('RECENT_CONVER')) and str(row.get('RECENT_CONVER')).strip() else ""}
            </div>
            """
        html_content += "</div>" # Close group-section div
        html_content += "</body></html>"

        try:
            with open(html_full_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            logging.info(f"Generated report: '{html_full_path.name}'")
        except OSError as e:
            logging.error(f"Failed to export '{html_full_path.name}'. Error: {e}")
    logging.info("All grouped reports generated!")

def get_user_input(prompt: str, options: list[str] | None = None, is_date: bool = False, allow_empty: bool = True) -> any:
    """
    Gets user input from the command line, with optional validation for choices or dates.

    Args:
        prompt (str): The message to display to the user.
        options (list[str], optional): A list of valid choices. Defaults to None.
        is_date (bool, optional): If True, attempts to parse input as a datetime. Defaults to False.
        allow_empty (bool, optional): If True, allows an empty input to be returned. Defaults to True.

    Returns:
        any: The user's input, parsed as datetime if is_date, or None if empty/invalid.
    """
    while True:
        user_input = input(prompt).strip()
        if not user_input:
            if allow_empty:
                return "ALL" if options else None # Return "ALL" for dropdowns, None for optional dates/strings
            else:
                logging.warning("Input cannot be empty. Please provide a value.")
                continue

        if is_date:
            try:
                # Try parsing with time, then without
                return datetime.datetime.strptime(user_input, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                try:
                    return datetime.datetime.strptime(user_input, "%Y-%m-%d")
                except ValueError:
                    logging.warning("Invalid date format. Please use YYYY-MM-DD or YYYY-MM-DD HH:MM:SS.")
                    continue
        elif options:
            if user_input.upper() in [o.upper() for o in options]:
                # Return the canonical casing from options if a match is found
                for opt in options:
                    if user_input.upper() == opt.upper():
                        return opt
            else:
                logging.warning(f"Invalid input. Please enter one of: {', '.join(options)}")
                continue
        return user_input # Return raw input if no options or date parsing

def print_management_report(filtered_df: pd.DataFrame):
    """
    Prints a simplified management report to the console.

    Args:
        filtered_df (pd.DataFrame): The DataFrame to report on.
    """
    logging.info("\n--- Management Report / NOTE ---")
    if filtered_df.empty:
        logging.info("No data found for the selected criteria.")
        return

    for idx, row in filtered_df[MANAGEMENT_REPORT_COLS].iterrows():
        logging.info("------------------------------")
        for col in MANAGEMENT_REPORT_COLS:
            label = col.replace('_', ' ').title() # Format column name for display
            value = row.get(col, 'N/A')
            if pd.isna(value):
                value = 'N/A'
            elif isinstance(value, pd.Timestamp):
                value = value.strftime("%Y-%m-%d %H:%M:%S")
            elif isinstance(value, str):
                value = value.strip()
                if not value: # Handle empty strings after stripping
                    value = 'N/A'

            # Special handling for RECENT_CONVER to ensure multiline display
            if col == "RECENT_CONVER":
                logging.info(f"{label}:")
                logging.info(f"  {value}")
            else:
                logging.info(f"{label}: {value}")
    logging.info("------------------------------\n")

def handle_photo_upload(filtered_df: pd.DataFrame, gallery_dir: Path):
    """
    Handles the command-line photo upload process.

    Args:
        filtered_df (pd.DataFrame): The currently filtered DataFrame to select cases from.
        gallery_dir (Path): The base directory for storing uploaded photos.
    """
    logging.info("\n--- Photo Upload ---")
    if filtered_df.empty:
        logging.warning("No cases available in the current filter to attach photos to.")
        return

    # List cases for user selection
    logging.info("Available cases for photo upload:")
    case_options = []
    for i, (_, row) in enumerate(filtered_df.iterrows()):
        case_title = str(row.get("CASE TITLE", "Unknown Case"))
        complaint_time = row.get("COMPLAINT ISSUE TIME", "")
        time_str = fmt_dt(complaint_time)
        display_str = f"{i+1}. {case_title} | {time_str}"
        case_options.append(display_str)
        logging.info(display_str)

    try:
        case_choice = int(input("Enter the number of the case to upload a photo for: ").strip())
        if not (1 <= case_choice <= len(case_options)):
            logging.error("Invalid case number selected.")
            return
    except ValueError:
        logging.error("Invalid input. Please enter a number.")
        return

    selected_row = filtered_df.iloc[case_choice - 1]

    # Get source photo file path from user
    photo_path_str = get_user_input("Enter the full path to the photo file (e.g., C:/Users/YourUser/image.jpg): ", allow_empty=False)
    source_photo_path = Path(photo_path_str)

    if not source_photo_path.is_file():
        logging.error(f"Error: Photo file not found at '{source_photo_path}'.")
        return
    if source_photo_path.suffix.lower() not in ['.jpg', '.jpeg', '.png']:
        logging.warning("Warning: Only .jpg, .jpeg, .png files are typically supported for evidence photos.")

    # Determine destination folder
    case_title_clean = str(selected_row.get("CASE TITLE", "Unknown")).strip().replace(" ", "_").replace("/", "_").replace("\\", "_")
    complaint_time_val = selected_row.get("COMPLAINT ISSUE TIME", None)

    if isinstance(complaint_time_val, pd.Timestamp):
        folder_time = complaint_time_val.strftime("%Y-%m-%d_%H-%M-%S")
    else:
        folder_time = "unknown_time"

    target_folder_name = f"{case_title_clean}_{folder_time}"
    destination_folder_path = gallery_dir / target_folder_name
    destination_folder_path.mkdir(parents=True, exist_ok=True)

    # Copy the file, handling duplicates
    original_filename = source_photo_path.name
    destination_file_path = destination_folder_path / original_filename
    
    counter = 1
    while destination_file_path.exists():
        base_name = source_photo_path.stem
        extension = source_photo_path.suffix
        new_filename = f"{base_name}_{counter}{extension}"
        destination_file_path = destination_folder_path / new_filename
        counter += 1

    try:
        shutil.copy2(source_photo_path, destination_file_path)
        logging.info(f"Successfully uploaded '{original_filename}' to '{destination_file_path}'")
    except Exception as e:
        logging.error(f"Failed to copy photo '{original_filename}'. Error: {e}")


def main():
    """Main function to run the B2B report generator."""
    logging.info("Starting B2B Report Generator...")

    # 1. Load and preprocess data
    df = load_and_preprocess_data(EXCEL_FILE_PATH, EXCEL_SHEET_NAME)
    if df.empty:
        logging.error("Exiting due to no data or error in loading/preprocessing.")
        return

    # Get unique options for dropdowns from the full dataset
    reported_options = ['ALL'] + sorted(df['REPORTED'].dropna().unique().tolist())
    status_options = ['ALL'] + sorted(df['STATUS'].dropna().unique().tolist())
    township_options = ['ALL'] + sorted(df['TOWNSHIP'].dropna().unique().tolist())
    pic_options = ['ALL'] + sorted(df['PIC'].dropna().unique().tolist())
    circuit_options = ['ALL'] + sorted(df['CIRCUIT ID'].dropna().unique().tolist())

    # 2. Get user input for filters
    logging.info("\nPlease enter filter criteria (leave blank for 'ALL' or 'N/A'):")
    from_dt_val = get_user_input("Enter 'From' Date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS): ", is_date=True)
    to_dt_val = get_user_input("Enter 'To' Date (YYYY-MM-DD or YYYY-MM-DD HH:MM:SS): ", is_date=True)
    township_val = get_user_input(f"Enter Township ({', '.join(township_options)}): ", township_options)
    status_val = get_user_input(f"Enter Status ({', '.join(status_options)}): ", status_options)
    pic_val = get_user_input(f"Enter PIC ({', '.join(pic_options)}): ", pic_options)
    reported_val = get_user_input(f"Enter REPORTED ({', '.join(reported_options)}): ", reported_options)
    circuit_val = get_user_input(f"Enter CIRCUIT ID ({', '.join(circuit_options)}): ", circuit_options)

    # 3. Apply filters to the DataFrame
    filtered_df = df.copy()

    if from_dt_val:
        filtered_df = filtered_df[filtered_df['COMPLAINT ISSUE TIME'] >= from_dt_val]
    if to_dt_val:
        filtered_df = filtered_df[filtered_df['COMPLAINT ISSUE TIME'] <= to_dt_val]

    if reported_val != 'ALL':
        filtered_df = filtered_df[filtered_df['REPORTED'] == reported_val]
    if status_val != 'ALL':
        filtered_df = filtered_df[filtered_df['STATUS'] == status_val]
    if township_val != 'ALL':
        filtered_df = filtered_df[filtered_df['TOWNSHIP'] == township_val]
    if pic_val != 'ALL':
        filtered_df = filtered_df[filtered_df['PIC'] == pic_val]
    if circuit_val != 'ALL':
        filtered_df = filtered_df[filtered_df['CIRCUIT ID'] == circuit_val]

    if filtered_df.empty:
        logging.info("\nNo data found for your selected filter criteria. No reports will be generated.")
        return

    logging.info(f"\nFound {len(filtered_df)} case(s) matching your criteria.")

    # 4. Print Management Report to console
    print_management_report(filtered_df)

    # 5. Offer report generation options
    while True:
        action = input("\nChoose an action:\n"
                       "1. Generate Single HTML Report\n"
                       "2. Generate Grouped HTML Reports (by Township & Status)\n"
                       "3. Generate Grouped HTML Reports (by PIC & Status)\n" # New option
                       "4. Generate B2B Map\n"
                       "5. Upload Photo for a Case\n"
                       "6. Exit\n" # Updated exit option
                       "Enter choice (1/2/3/4/5/6): ").strip() # Updated prompt

        if action == '1':
            generate_single_html_report(filtered_df, from_dt_val, to_dt_val,
                                        reported_val, status_val, township_val,
                                        pic_val, circuit_val, HTML_REPORT_DIR)
        elif action == '2':
            generate_grouped_html_reports(filtered_df, from_dt_val, to_dt_val, HTML_REPORT_DIR)
        elif action == '3': # New action
            generate_grouped_pic_status_reports(filtered_df, from_dt_val, to_dt_val, HTML_REPORT_DIR)
        elif action == '4':
            # For map, need specific status and reported filter from user
            map_status = get_user_input("Enter Status for Map (e.g., pending, ongoing, completed): ", ['pending', 'ongoing', 'completed'])
            map_reported = get_user_input("Filter Map by REPORTED (ME, HANDOVER, or ALL): ", ['ME', 'HANDOVER', 'ALL'])
            generate_b2b_map(df, map_status, map_reported, HTML_REPORT_DIR) # Pass original df for map filtering
        elif action == '5':
            handle_photo_upload(filtered_df, GALLERY_DIR)
        elif action == '6': # Updated exit option
            logging.info("Exiting B2B Report Generator. Goodbye!")
            break
        else:
            logging.warning("Invalid choice. Please enter 1, 2, 3, 4, 5, or 6.") # Updated warning

if __name__ == "__main__":
    main()
