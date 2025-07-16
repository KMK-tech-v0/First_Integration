import pandas as pd
import pyodbc
import folium

# SQL data loading configuration
server = r'DESKTOP-17P73P0\SQLEXPRESS'
database = 'MMP_Analysis'
conn_str = (
    r'DRIVER={SQL Server};'
    f'SERVER={server};'
    f'DATABASE={database};'
    'Trusted_Connection=yes;'
)

# Load data from the 'sgg_fat_list' table
with pyodbc.connect(conn_str) as conn:
    df_sql = pd.read_sql("SELECT * FROM sgg_fat_list", conn)

# Filter by specific Circuit_ID
circuit_id = 'SPLT-002750-SGG-IU'
df_filtered = df_sql[df_sql['Circuit_ID'] == circuit_id]

# Extract needed columns
columns_needed = [
    'Circuit_ID',
    '_1st_Splitter_Name',
    'Lat',
    'Long',
    'Splitter_Name_FAT',
    'Lat2',
    'Long2'
]
df_map = df_filtered[columns_needed]

# Get coordinates and names
# Get coordinates and names
name1 = df_map['_1st_Splitter_Name'].values[0]
lat1 = float(df_map['Lat'].values[0])
long1 = float(df_map['Long'].values[0])

name2 = df_map['Splitter_Name_FAT'].values[0]
lat2 = float(df_map['Lat2'].values[0])
long2 = float(df_map['Long2'].values[0])


# Create map centered between the two points
map_center = [(lat1 + lat2) / 2, (long1 + long2) / 2]
m = folium.Map(location=map_center, zoom_start=15)

# Add marker for _1st_Splitter_Name
folium.Marker(
    location=[lat1, long1],
    popup=name1,
    icon=folium.Icon(color='blue', icon='info-sign')
).add_to(m)

# Add marker for Splitter_Name_FAT
folium.Marker(
    location=[lat2, long2],
    popup=name2,
    icon=folium.Icon(color='green', icon='info-sign')
).add_to(m)

# Draw a line between the two points
folium.PolyLine(locations=[[lat1, long1], [lat2, long2]], color='purple').add_to(m)

# Show map in Jupyter or save to HTML
m.save("map_output.html")


from IPython.display import IFrame
IFrame('map_output.html', width=700, height=500)
