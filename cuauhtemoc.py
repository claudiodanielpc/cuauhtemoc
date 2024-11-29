import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap

# Load GeoJSON
url = "https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/refs/heads/main/cuauhtemoc.geojson"
cuauhtemoc = gpd.read_file(url)

# Initialize session state for the map
if "map_initialized" not in st.session_state:
    # Create the base map only once
    st.session_state["map_initialized"] = True
    st.session_state["map"] = leafmap.Map(minimap_control=True, location=[19.4326, -99.1332], zoom_start=12)
    # Add static base layers
    st.session_state["map"].add_basemap("CartoDB.Positron")

# Sidebar for filtering
st.sidebar.header("Filtrar por colonia")
colonia_list = ["Todas"] + sorted(cuauhtemoc["nom_colonia"].unique())
selected_colonia = st.sidebar.selectbox("Selecciona una colonia:", colonia_list)

# Retrieve the base map from session state
m = st.session_state["map"]

# Dynamically update the layer
if selected_colonia == "Todas":
    # Add all polygons
    m.add_geojson(cuauhtemoc, layer_name="Colonias")
else:
    # Filter the GeoDataFrame for the selected colonia
    filtered_colonia = cuauhtemoc[cuauhtemoc["nom_colonia"] == selected_colonia]
    m.add_geojson(filtered_colonia, layer_name=selected_colonia)

# Display the map in Streamlit
m.to_streamlit(height=500)
