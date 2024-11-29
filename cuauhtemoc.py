import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import geopandas as gpd

url="C:/users/claud/Downloads/cuauhtemoc.gpkg"


colonias=gpd.read_file(url)
#Filtrar cve_ent=9 y cve_mun=015
colonias=colonias[(colonias.cve_ent=="09") & (colonias.cve_mun=="015")]


st.markdown("<p style='font-family: Century Gothic; font-weight: bold;font-size: 35px; text-align: center'>Cuauhtémoc</p>", unsafe_allow_html=True)

# Dropdown for selecting colonia
selected_colonia = st.selectbox('Select a colonia', ['All'] + colonias['nom_colonia'].tolist())

# iniciar mapa de alcaldía Cuauhtémoc
m = folium.Map(location=[19.4326, -99.1332], zoom_start=12)


# Adding Google Satellite tile layer
google_satellite = folium.TileLayer(
    tiles='https://www.google.com/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}',
    attr='Google',
    name='Google Satellite',
    overlay=False,
    control=True
)
google_satellite.add_to(m)

# Adding CartoDB Positron tile layer
cartodb_positron = folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
    attr='CartoDB',
    name='CartoDB Positron',
    overlay=False,
    control=True
).add_to(m)

# Add GeoJSON
if selected_colonia == 'All':
    folium.GeoJson(colonias).add_to(m)
else:
    selected_gdf = colonias[colonias['nom_colonia'] == selected_colonia]
    folium.GeoJson(selected_gdf).add_to(m)


# Add a section for loading the CSV
st.sidebar.header("Upload CSV or Enter Coordinates")

# Option 1: Upload a CSV
uploaded_file = st.sidebar.file_uploader("Upload a CSV with lat/lon columns", type=["csv"])
if uploaded_file:
    # Read the CSV
    data = pd.read_csv(uploaded_file)

    # Check if required columns exist
    if {'lat', 'lon'}.issubset(data.columns):
        st.success("CSV loaded successfully!")
        # Add points to the map
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in data.iterrows():
            folium.Marker(location=[row['lat'], row['lon']], tooltip=f"Point: {row['lat']}, {row['lon']}").add_to(marker_cluster)
    else:
        st.error("The CSV must contain 'lat' and 'lon' columns.")


# Option 2: Manual Input for a Single Coordinate
st.sidebar.markdown("### OR")
lat = st.sidebar.text_input("Enter Latitude")
lon = st.sidebar.text_input("Enter Longitude")

if lat and lon:
    try:
        lat, lon = float(lat), float(lon)
        folium.Marker(location=[lat, lon], tooltip=f"Manual Point: {lat}, {lon}").add_to(m)
        st.success("Point added to the map!")
    except ValueError:
        st.error("Please enter valid numeric coordinates.")


folium.LayerControl().add_to(m)

# Render map
st_folium(m, width=1000, height=800)
