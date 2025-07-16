import geopandas as gpd
import matplotlib.pyplot as plt
import folium
import json
from shapely.geometry import shape
import os

# Embedded GeoJSON data for Myanmar states
MYANMAR_STATES_GEOJSON = {
  "type": "FeatureCollection",
  "features": [
    {
      "type": "Feature",
      "properties": {
        "ST": "Kachin",
        "ST_PCODE": "MMR001"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[97.375, 28.335], [97.375, 27.335], [98.375, 27.335], [98.375, 28.335], [97.375, 28.335]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Kayah",
        "ST_PCODE": "MMR002"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[97.125, 19.625], [97.125, 18.625], [98.125, 18.625], [98.125, 19.625], [97.125, 19.625]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Kayin",
        "ST_PCODE": "MMR003"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[97.5, 18.0], [97.5, 17.0], [98.5, 17.0], [98.5, 18.0], [97.5, 18.0]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Chin",
        "ST_PCODE": "MMR004"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[93.5, 24.0], [93.5, 23.0], [94.5, 23.0], [94.5, 24.0], [93.5, 24.0]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Sagaing",
        "ST_PCODE": "MMR005"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[94.0, 26.0], [94.0, 25.0], [95.0, 25.0], [95.0, 26.0], [94.0, 26.0]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Tanintharyi",
        "ST_PCODE": "MMR006"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[98.0, 14.0], [98.0, 13.0], [99.0, 13.0], [99.0, 14.0], [98.0, 14.0]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Bago",
        "ST_PCODE": "MMR007"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[95.5, 19.0], [95.5, 18.0], [96.5, 18.0], [96.5, 19.0], [95.5, 19.0]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Magway",
        "ST_PCODE": "MMR008"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[94.5, 21.5], [94.5, 20.5], [95.5, 20.5], [95.5, 21.5], [94.5, 21.5]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Mandalay",
        "ST_PCODE": "MMR009"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[95.5, 22.0], [95.5, 21.0], [96.5, 21.0], [96.5, 22.0], [95.5, 22.0]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Mon",
        "ST_PCODE": "MMR010"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[97.0, 17.0], [97.0, 16.0], [98.0, 16.0], [98.0, 17.0], [97.0, 17.0]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Rakhine",
        "ST_PCODE": "MMR011"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[92.5, 20.5], [92.5, 19.5], [93.5, 19.5], [93.5, 20.5], [92.5, 20.5]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Yangon",
        "ST_PCODE": "MMR012"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[96.0, 17.0], [96.0, 16.0], [97.0, 16.0], [97.0, 17.0], [96.0, 17.0]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Shan",
        "ST_PCODE": "MMR013"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[97.0, 23.0], [97.0, 22.0], [98.0, 22.0], [98.0, 23.0], [97.0, 23.0]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Ayeyarwady",
        "ST_PCODE": "MMR014"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[95.0, 17.5], [95.0, 16.5], [96.0, 16.5], [96.0, 17.5], [95.0, 17.5]]]
      }
    },
    {
      "type": "Feature",
      "properties": {
        "ST": "Naypyitaw",
        "ST_PCODE": "MMR015"
      },
      "geometry": {
        "type": "Polygon",
        "coordinates": [[[96.0, 19.5], [96.0, 19.0], [96.5, 19.0], [96.5, 19.5], [96.0, 19.5]]]
      }
    }
  ]
}

# 1. Function to plot Myanmar states and regions
def plot_myanmar_states():
    try:
        # Create GeoDataFrame from embedded data
        features = MYANMAR_STATES_GEOJSON['features']
        gdf = gpd.GeoDataFrame.from_features(features)
        gdf['geometry'] = gdf['geometry'].apply(shape)
        
        # Plot the map
        fig, ax = plt.subplots(figsize=(12, 12))
        gdf.plot(ax=ax, edgecolor='black', column='ST', legend=True, cmap='tab20')
        plt.title("မြန်မာနိုင်ငံ၏ ပြည်နယ်နှင့်တိုင်းများ")
        plt.axis('off')
        plt.show()
        
        # Save GeoJSON
        gdf.to_file("myanmar_states.geojson", driver='GeoJSON')
        print("ပြည်နယ်နှင့်တိုင်းများ GeoJSON ဖိုင်သိမ်းပြီး")
        
    except Exception as e:
        print(f"Error in plot_myanmar_states: {str(e)}")

# 2. Interactive map with Folium
def plot_interactive_map():
    try:
        # Try to load from saved file or use embedded data
        if os.path.exists("myanmar_states.geojson"):
            states_gdf = gpd.read_file("myanmar_states.geojson")
        else:
            features = MYANMAR_STATES_GEOJSON['features']
            states_gdf = gpd.GeoDataFrame.from_features(features)
            states_gdf['geometry'] = states_gdf['geometry'].apply(shape)
        
        # Create Folium map
        myanmar_center = [21.9162, 95.9560]
        m = folium.Map(location=myanmar_center, zoom_start=6, tiles='CartoDB positron')
        
        # Add states with better styling
        folium.GeoJson(
            states_gdf,
            name='မြန်မာပြည်နယ်နှင့်တိုင်းများ',
            style_function=lambda feature: {
                'fillColor': '#ffff00',
                'color': 'black',
                'weight': 1,
                'fillOpacity': 0.6
            },
            highlight_function=lambda x: {'weight': 3, 'fillOpacity': 0.9},
            tooltip=folium.GeoJsonTooltip(
                fields=['ST', 'ST_PCODE'],
                aliases=['ပြည်နယ်/တိုင်း: ', 'P-Code: '],
                localize=True
            )
        ).add_to(m)
        
        # Add layer control and save
        folium.LayerControl().add_to(m)
        m.save('myanmar_states_map.html')
        print("Interactive မြေပုံသိမ်းပြီး - myanmar_states_map.html")
        
    except Exception as e:
        print(f"Error in plot_interactive_map: {str(e)}")

# 3. Simple township data example for Yangon
def filter_townships():
    try:
        # Sample Yangon townships data
        yangon_townships = [
            {"TS": "Ahlon", "TS_PCODE": "MMR012001"},
            {"TS": "Bahan", "TS_PCODE": "MMR012002"},
            {"TS": "Dagon", "TS_PCODE": "MMR012003"},
            {"TS": "Hlaing", "TS_PCODE": "MMR012004"},
            {"TS": "Kamayut", "TS_PCODE": "MMR012005"},
            {"TS": "Kyauktada", "TS_PCODE": "MMR012006"},
            {"TS": "Lanmadaw", "TS_PCODE": "MMR012007"},
            {"TS": "Latha", "TS_PCODE": "MMR012008"},
            {"TS": "Mayangon", "TS_PCODE": "MMR012009"},
            {"TS": "Pabedan", "TS_PCODE": "MMR012010"},
            {"TS": "Sanchaung", "TS_PCODE": "MMR012011"},
            {"TS": "Seikkan", "TS_PCODE": "MMR012012"}
        ]
        
        print("ရန်ကုန်တိုင်းရှိ မြို့နယ်များ:")
        for township in yangon_townships:
            print(f"{township['TS']} ({township['TS_PCODE']})")
        
        # Save as JSON (since we don't have geometries)
        with open("yangon_townships.json", "w") as f:
            json.dump(yangon_townships, f)
        print("\nရန်ကုန်မြို့နယ်များ JSON ဖိုင်သိမ်းပြီး")
        
    except Exception as e:
        print(f"Error in filter_townships: {str(e)}")

if __name__ == "__main__":
    plot_myanmar_states()
    plot_interactive_map()
    filter_townships()