import streamlit as st
import leafmap.foliumap as leafmap
from Demos.win32console_demo import coord
from pyogrio import read_dataframe
import pandas as pd
import geopandas as gpd
from select import select

# Load GeoJSON
cuauhtemoc = read_dataframe(
    'https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/refs/heads/main/cuauhtemoc.geojson')

cordterritorios = read_dataframe(
    "https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/refs/heads/main/cuadrantes_cuauhtemoc.geojson"
)

# Ensure CRS match between the two GeoDataFrames
cordterritorios = cordterritorios.to_crs(cuauhtemoc.crs)
cordterritorios = cordterritorios[['sector', 'zona', 'no_cdrn', 'geometry']]
# Sidebar configuration
st.sidebar.title('Opciones')
st.sidebar.info('Acercar a una colonia y cargar coordenadas')

# Dropdown for selecting a colonia
colonia = st.sidebar.selectbox('Zoom a colonia',
                               ['Todas las colonias'] + list(cuauhtemoc['nom_colonia'].unique()))

# File uploader for CSV
uploaded_file = st.sidebar.file_uploader("Carga CSV con lat y lon", type=["csv"])

# Initialize map centered on Cuauhtémoc
m = leafmap.Map(center=[19.4326, -99.1332], zoom=13)

# Conditional layer addition
if colonia == 'Todas las colonias':
    # Display all colonias and all cordterritorios
    m.add_gdf(
        gdf=cuauhtemoc,
        zoom_to_layer=False,
        layer_name='Colonias',
        info_mode='on_click',
        style={'color': '#7fcdbb', 'fillOpacity': 0.3, 'weight': 0.5},
    )
    # Add Cuadrantes layer with filtered popups
    m.add_gdf(
        gdf=cordterritorios,
        layer_name='Cuadrantes',
        style={'color': '#3182bd', 'fillOpacity': 0.5, 'weight': 1},
        info_mode='on_click'
    )
else:
    # Filter selected colonia
    selected_gdf = cuauhtemoc[cuauhtemoc['nom_colonia'] == colonia]

    filtered_cordterritorios = gpd.sjoin(selected_gdf, cordterritorios, predicate='contains')


    # Add selected colonia and filtered cordterritorios to the map
    m.add_gdf(
        gdf=selected_gdf,
        layer_name=colonia,
        zoom_to_layer=True,
        style={'color': '#e6550d', 'fill': None, 'weight': 4},
    )
    if not filtered_cordterritorios.empty:
        m.add_gdf(
            gdf=filtered_cordterritorios,
            layer_name='Cuadrantes dentro de colonia',
            style={'color': '#3182bd', 'fillOpacity': 0.5, 'weight': 1},
            info_mode='on_click',

        )

# Handle uploaded CSV
if uploaded_file is not None:
    # Read CSV into a DataFrame
    df = pd.read_csv(uploaded_file)

    # Check if required columns are present
    if 'lat' in df.columns and 'lon' in df.columns:
        # Drop rows with missing lat or lon
        df = df.dropna(subset=['lat', 'lon'])

        # Add circle markers using add_circle_markers_from_xy
        m.add_circle_markers_from_xy(
            data=df,
            x='lon',
            y='lat',
            layer_name='Puntos cargados',
            radius=5,  # Circle radius
            color='red',  # Circle border color
            fill=True,  # Fill the circle
            fill_color='black',  # Fill color
            fill_opacity=0.6,  # Fill opacity
        )
    else:
        st.error("El csv debe contener columnas 'lat' y 'lon'")

# Save map as HTML
html_file = "map.html"
m.to_html(outfile=html_file)

# Main menu bar: Save Button
st.markdown("### Mapa de la Alcaldía Cuauhtémoc")
with open(html_file, "r") as file:
    html_content = file.read()
    st.download_button(
        label="💾 Descargar mapa como HTML",
        data=html_content,
        file_name="mapa.html",
        mime="text/html",
    )

# Render map in Streamlit
m.to_streamlit(1000, 800)
