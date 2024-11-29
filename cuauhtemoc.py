import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import geopandas as gpd


colonias=gpd.read_file("https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/refs/heads/main/cuauhtemoc.geojson",engine="pyogrio" )


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
st.sidebar.header("Ubicación de puntos en el mapa")

# Option 1: Upload a CSV
uploaded_file = st.sidebar.file_uploader("Carga CSV con columnas lat y lon", type=["csv"])
if uploaded_file:
    # Read the CSV
    data = pd.read_csv(uploaded_file)

    # Check if required columns exist
    if {'lat', 'lon'}.issubset(data.columns):
        st.success("¡CSV cargado con éxito!")
        # Add points to the map
        marker_cluster = MarkerCluster().add_to(m)
        for _, row in data.iterrows():
            folium.Marker(location=[row['lat'], row['lon']], tooltip=f"Point: {row['lat']}, {row['lon']}").add_to(marker_cluster)
    else:
        st.error("El CSV debe tener las columnas 'lat' y 'lon'.")


# Option 2: Manual Input for a Single Coordinate
st.sidebar.markdown("### Ubicación manual")
coordinates = st.sidebar.text_input("Inserta coordenadas (formato: lat, lon)")

if coordinates:
    try:
        # Split the input into latitude and longitude
        lat, lon = map(float, coordinates.split(','))
        folium.Marker(location=[lat, lon], tooltip=f"Punto: {lat}, {lon}").add_to(m)
        st.success("Punto añadido al mapa")
    except ValueError:
        st.error("Por favor ingresa coordenadas válidas en el formato: lat, lon")



folium.LayerControl().add_to(m)

# Render map
st_folium(m, width=1000, height=800)
