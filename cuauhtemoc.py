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


# Cache base map creation
@st.cache_data
def create_base_map():
    # Create base map
    m = folium.Map(location=[19.4326, -99.1332], zoom_start=12)

    # Add Google Satellite tile layer
    folium.TileLayer(
        tiles='https://www.google.com/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}',
        attr='Google',
        name='Google Satellite',
        overlay=False,
        control=True
    ).add_to(m)

    # Add CartoDB Positron tile layer
    folium.TileLayer(
        tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
        attr='CartoDB',
        name='CartoDB Positron',
        overlay=False,
        control=True
    ).add_to(m)

    # Add LayerControl
    folium.LayerControl().add_to(m)

    return m


# Load GeoJSON data (cached)
colonias = load_colonias()

# Initialize session state for selected colonia and CSV data
if "selected_colonia" not in st.session_state:
    st.session_state["selected_colonia"] = "Todas"

if "csv_data" not in st.session_state:
    st.session_state["csv_data"] = pd.DataFrame(columns=["lat", "lon"])

# App layout
st.markdown(
    "<p style='font-family: Century Gothic; font-weight: bold;font-size: 35px; text-align: center'>Cuauhtémoc</p>",
    unsafe_allow_html=True)

# Dropdown for selecting a colonia
selected_colonia = st.selectbox('Selecciona una colonia', ['Todas'] + colonias['nom_colonia'].tolist(),
                                key="selected_colonia")

# Create the base map (cached)
m = create_base_map()

# Add GeoJSON layer dynamically
if st.session_state["selected_colonia"] == "Todas":
    folium.GeoJson(colonias).add_to(m)
else:
    selected_gdf = colonias[colonias['nom_colonia'] == st.session_state["selected_colonia"]]
    folium.GeoJson(selected_gdf).add_to(m)

# Sidebar for CSV upload
st.sidebar.header("Ubicación de puntos en el mapa")

# Option 1: Upload a CSV
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

# Add points from uploaded CSV (if any)
if not st.session_state["csv_data"].empty:
    marker_cluster = MarkerCluster().add_to(m)
    for _, row in st.session_state["csv_data"].iterrows():
        folium.Marker(location=[row["lat"], row["lon"]], tooltip=f"Point: {row['lat']}, {row['lon']}").add_to(
            marker_cluster)

# Option 2: Manual Input for a Single Coordinate
st.sidebar.markdown("### Ubicación manual")
coordinates = st.sidebar.text_input("Inserta coordenadas (formato: lat, lon)")

if coordinates:
    try:
        lat, lon = map(float, coordinates.split(","))
        folium.Marker(location=[lat, lon], tooltip=f"Punto: {lat}, {lon}").add_to(m)
        st.success("Punto añadido al mapa")
    except ValueError:
        st.error("Por favor ingresa coordenadas válidas en el formato: lat, lon")

# Render the map
st_folium(m, width=1000, height=800)
