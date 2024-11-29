import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import geopandas as gpd
import pyogrio

# Cache the GeoJSON loading to prevent reloading
@st.cache_data
def load_colonias():
    return gpd.read_file("https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/refs/heads/main/cuauhtemoc.geojson", engine="pyogrio")

# Load GeoJSON
colonias = load_colonias()

# Initialize session state for CSV data
if "csv_data" not in st.session_state:
    st.session_state["csv_data"] = pd.DataFrame(columns=["lat", "lon"])

st.markdown("<p style='font-family: Century Gothic; font-weight: bold;font-size: 35px; text-align: center'>Cuauhtémoc</p>", unsafe_allow_html=True)

# Dropdown for selecting colonia
selected_colonia = st.selectbox('Selecciona una colonia', ['Todas'] + colonias['nom_colonia'].tolist())

# Initialize the map
m = folium.Map(location=[19.4326, -99.1332], zoom_start=12)

# Add tile layers
google_satellite = folium.TileLayer(
    tiles='https://www.google.com/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}',
    attr='Google',
    name='Google Satellite',
    overlay=False,
    control=True
)
google_satellite.add_to(m)

cartodb_positron = folium.TileLayer(
    tiles='https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png',
    attr='CartoDB',
    name='CartoDB Positron',
    overlay=False,
    control=True
).add_to(m)

# Add GeoJSON based on colonia selection
if selected_colonia == 'Todas':
    folium.GeoJson(colonias).add_to(m)
else:
    selected_gdf = colonias[colonias['nom_colonia'] == selected_colonia]
    folium.GeoJson(selected_gdf).add_to(m)

# Sidebar for CSV uploading
st.sidebar.header("Ubicación de puntos en el mapa")

# Option 1: Upload a CSV
uploaded_file = st.sidebar.file_uploader("Carga CSV con columnas lat y lon", type=["csv"])
if uploaded_file:
    # Read the uploaded CSV
    data = pd.read_csv(uploaded_file)

    # Check if required columns exist
    if {'lat', 'lon'}.issubset(data.columns):
        # Drop NaN and validate ranges
        data = data.dropna(subset=['lat', 'lon'])
        data = data[(data['lat'].between(-90, 90)) & (data['lon'].between(-180, 180))]

        if data.empty:
            st.error("El CSV no contiene coordenadas válidas.")
        else:
            st.session_state["csv_data"] = data  # Store the data in session state
            st.success("¡CSV cargado con éxito!")
    else:
        st.error("El CSV debe tener las columnas 'lat' y 'lon'.")

# Add points from session state to the map
if not st.session_state["csv_data"].empty:
    marker_cluster = MarkerCluster().add_to(m)
    for _, row in st.session_state["csv_data"].iterrows():
        folium.Marker(location=[row['lat'], row['lon']],
                      tooltip=f"Point: {row['lat']}, {row['lon']}").add_to(marker_cluster)

# Option 2: Manual Input for a Single Coordinate
st.sidebar.markdown("### Ubicación manual")
coordinates = st.sidebar.text_input("Inserta coordenadas (formato: lat, lon)")

if coordinates:
    try:
        # Split and validate input
        lat, lon = map(float, coordinates.split(','))
        folium.Marker(location=[lat, lon], tooltip=f"Punto: {lat}, {lon}").add_to(m)
        st.success("Punto añadido al mapa")
    except ValueError:
        st.error("Por favor ingresa coordenadas válidas en el formato: lat, lon")

# Add LayerControl and Render the Map
folium.LayerControl().add_to(m)
st_folium(m, width=1200, height=800)
