import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
from folium.plugins import MarkerCluster
import geopandas as gpd

# Cache GeoJSON loading
@st.cache_data
def load_colonias():
    return gpd.read_file("https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/main/cuauhtemoc.geojson")

# Load GeoJSON data
colonias = load_colonias()

# Initialize session state
if "map_center" not in st.session_state:
    st.session_state["map_center"] = [19.4326, -99.1332]
if "map_zoom" not in st.session_state:
    st.session_state["map_zoom"] = 12
if "csv_data" not in st.session_state:
    st.session_state["csv_data"] = pd.DataFrame(columns=["lat", "lon"])
if "manual_point" not in st.session_state:
    st.session_state["manual_point"] = None

st.markdown("<p style='font-family: Century Gothic; font-weight: bold;font-size: 35px; text-align: center'>Cuauhtémoc</p>", unsafe_allow_html=True)

# Sidebar for dropdown and CSV upload
st.sidebar.header("Opciones del mapa")

# Dropdown for selecting a colonia
selected_colonia = st.sidebar.selectbox('Selecciona una colonia', ['Todas'] + sorted(colonias['nom_colonia'].unique()))

# Upload CSV
uploaded_file = st.sidebar.file_uploader("Carga CSV con columnas lat y lon", type=["csv"])
if uploaded_file:
    data = pd.read_csv(uploaded_file)
    if {'lat', 'lon'}.issubset(data.columns):
        data = data.dropna(subset=['lat', 'lon'])
        data = data[(data['lat'].between(-90, 90)) & (data['lon'].between(-180, 180))]
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
if coordinates:
    try:
        lat, lon = map(float, coordinates.split(','))
        st.session_state["manual_point"] = (lat, lon)
        st.success("Punto añadido al mapa")
    except ValueError:
        st.error("Por favor ingresa coordenadas válidas en el formato: lat, lon")
else:
    st.session_state["manual_point"] = None

# Initialize the map with the last center and zoom
m = folium.Map(location=st.session_state["map_center"], zoom_start=st.session_state["map_zoom"])

# Adding tile layers
folium.TileLayer(
    tiles='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
    name='OpenStreetMap',
    control=False
).add_to(m)

folium.TileLayer(
    tiles='https://www.google.com/maps/vt?lyrs=s&x={x}&y={y}&z={z}',
    attr='Google Satellite',
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

# Add GeoJSON layer based on selection
if selected_colonia == 'Todas':
    folium.GeoJson(
        colonias,
        name='Colonias',
        tooltip=folium.GeoJsonTooltip(fields=['nom_colonia'])
    ).add_to(m)
else:
    selected_gdf = colonias[colonias['nom_colonia'] == selected_colonia]
    folium.GeoJson(
        selected_gdf,
        name='Colonias',
        tooltip=folium.GeoJsonTooltip(fields=['nom_colonia'])
    ).add_to(m)

# Add CSV points
if not st.session_state["csv_data"].empty:
    marker_cluster = MarkerCluster(name='CSV Points').add_to(m)
    for _, row in st.session_state["csv_data"].iterrows():
        folium.Marker(
            location=[row['lat'], row['lon']],
            tooltip=f"Point: {row['lat']}, {row['lon']}"
        ).add_to(marker_cluster)

# Add manual coordinate point
if st.session_state["manual_point"] is not None:
    lat, lon = st.session_state["manual_point"]
    folium.Marker(
        location=[lat, lon],
        tooltip=f"Punto: {lat}, {lon}",
        icon=folium.Icon(color='red')
    ).add_to(m)

# Add LayerControl
folium.LayerControl().add_to(m)

# Render the map and capture the state
map_data = st_folium(m, width=1000, height=800)

# Update the map center and zoom based on user interaction
if map_data and 'last_center' in map_data and 'last_zoom' in map_data:
    st.session_state["map_center"] = [map_data['last_center']['lat'], map_data['last_center']['lng']]
    st.session_state["map_zoom"] = map_data['last_zoom']
