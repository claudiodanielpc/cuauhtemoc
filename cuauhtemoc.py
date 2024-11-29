import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import pyogrio


# Cache GeoJSON loading
@st.cache_data
def load_colonias():
    return gpd.read_file(
        "https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/refs/heads/main/cuauhtemoc.geojson",
        engine="pyogrio")


# Initialize session state for dynamic layers
if "map_layers" not in st.session_state:
    st.session_state["map_layers"] = {
        "colonias": True,  # Toggle for GeoJSON layer
        "csv_points": True,  # Toggle for CSV points
        "manual_points": []  # List of manually added points
    }

if "csv_data" not in st.session_state:
    st.session_state["csv_data"] = pd.DataFrame(columns=["lat", "lon"])

# Load GeoJSON data (cached)
colonias = load_colonias()

# App layout
st.markdown(
    "<p style='font-family: Century Gothic; font-weight: bold;font-size: 35px; text-align: center'>Cuauhtémoc GIS</p>",
    unsafe_allow_html=True)

# Sidebar for layer controls and data input
st.sidebar.header("Opciones del mapa")

# Layer controls
st.sidebar.subheader("Capas del mapa")
st.session_state["map_layers"]["colonias"] = st.sidebar.checkbox("Mostrar colonias (GeoJSON)",
                                                                 value=st.session_state["map_layers"]["colonias"])
st.session_state["map_layers"]["csv_points"] = st.sidebar.checkbox("Mostrar puntos CSV",
                                                                   value=st.session_state["map_layers"]["csv_points"])

# Upload CSV
st.sidebar.subheader("Carga de datos")
uploaded_file = st.sidebar.file_uploader("Carga CSV con columnas lat y lon", type=["csv"])
if uploaded_file:
    # Read and validate CSV
    data = pd.read_csv(uploaded_file)
    if {"lat", "lon"}.issubset(data.columns):
        data = data.dropna(subset=["lat", "lon"])
        data = data[(data["lat"].between(-90, 90)) & (data["lon"].between(-180, 180))]

        if data.empty:
            st.error("El CSV no contiene coordenadas válidas.")
        else:
            st.success("¡CSV cargado con éxito!")
            st.session_state["csv_data"] = data
    else:
        st.error("El CSV debe tener las columnas 'lat' y 'lon'.")

# Manual Input for a Single Coordinate
st.sidebar.subheader("Agregar punto manualmente")
coordinates = st.sidebar.text_input("Inserta coordenadas (formato: lat, lon)")
if coordinates:
    try:
        lat, lon = map(float, coordinates.split(","))
        st.session_state["map_layers"]["manual_points"].append((lat, lon))
        st.success(f"Punto añadido: ({lat}, {lon})")
    except ValueError:
        st.error("Por favor ingresa coordenadas válidas en el formato: lat, lon")

# Initialize the map
m = folium.Map(location=[19.4326, -99.1332], zoom_start=12)

# Add base tile layers
folium.TileLayer(
    tiles='https://www.google.com/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}',
    attr='Google',
    name='Google Satellite',
    overlay=False,
    control=True
).add_to(m)

folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
    attr='CartoDB',
    name='CartoDB Positron',
    overlay=False,
    control=True
).add_to(m)

# Add GeoJSON layer dynamically based on toggle
if st.session_state["map_layers"]["colonias"]:
    folium.GeoJson(colonias, name="Colonias").add_to(m)

# Add CSV points dynamically based on toggle
if st.session_state["map_layers"]["csv_points"] and not st.session_state["csv_data"].empty:
    marker_cluster = MarkerCluster(name="Puntos CSV").add_to(m)
    for _, row in st.session_state["csv_data"].iterrows():
        folium.Marker(location=[row["lat"], row["lon"]], tooltip=f"Point: {row['lat']}, {row['lon']}").add_to(
            marker_cluster)

# Add manual points
if st.session_state["map_layers"]["manual_points"]:
    for lat, lon in st.session_state["map_layers"]["manual_points"]:
        folium.Marker(location=[lat, lon], tooltip=f"Punto: {lat}, {lon}", icon=folium.Icon(color="red")).add_to(m)

# Add LayerControl
folium.LayerControl().add_to(m)

# Render the map
st_folium(m, width=1000, height=800)
