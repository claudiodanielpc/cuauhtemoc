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


# Load GeoJSON data
colonias = load_colonias()

# Initialize session state for CSV data
if "csv_data" not in st.session_state:
    st.session_state["csv_data"] = pd.DataFrame(columns=["lat", "lon"])

# App layout
st.markdown(
    "<p style='font-family: Century Gothic; font-weight: bold;font-size: 35px; text-align: center'>Cuauhtémoc</p>",
    unsafe_allow_html=True)

# Sidebar for dropdown and CSV upload
st.sidebar.header("Opciones del mapa")

# Dropdown for selecting a colonia
selected_colonia = st.sidebar.selectbox(
    'Selecciona una colonia', ['Todas'] + colonias['nom_colonia'].tolist()
)

# Upload CSV
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
st.sidebar.markdown("### Ubicación manual")
coordinates = st.sidebar.text_input("Inserta coordenadas (formato: lat, lon)")

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

# Add GeoJSON layer dynamically based on colonia selection
if selected_colonia == "Todas":
    folium.GeoJson(colonias).add_to(m)
else:
    selected_gdf = colonias[colonias['nom_colonia'] == selected_colonia]
    folium.GeoJson(selected_gdf).add_to(m)

# Add CSV points dynamically
if not st.session_state["csv_data"].empty:
    marker_cluster = MarkerCluster().add_to(m)
    for _, row in st.session_state["csv_data"].iterrows():
        folium.Marker(location=[row["lat"], row["lon"]], tooltip=f"Point: {row['lat']}, {row['lon']}").add_to(
            marker_cluster)

# Add manual coordinate point
if coordinates:
    try:
        lat, lon = map(float, coordinates.split(","))
        folium.Marker(location=[lat, lon], tooltip=f"Punto: {lat}, {lon}").add_to(m)
        st.success("Punto añadido al mapa")
    except ValueError:
        st.error("Por favor ingresa coordenadas válidas en el formato: lat, lon")

# Add LayerControl
folium.LayerControl().add_to(m)

# Render the map
map_data = st_folium(m, width=1000, height=800)
