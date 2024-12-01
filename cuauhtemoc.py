import streamlit as st
import leafmap.foliumap as leafmap
from pyogrio import read_dataframe
import pandas as pd
import geopandas as gpd

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
st.sidebar.info('Acercar a una colonia o seleccionar varias colonias')

# Dropdown for zooming to a single colonia
colonia = st.sidebar.selectbox(
    'Zoom a colonia (una sola)',
    ['Ninguna'] + list(cuauhtemoc['nom_colonia'].unique())
)

# Checklist for selecting multiple colonias
colonias_seleccionadas = st.sidebar.multiselect(
    'Seleccionar colonias (puede elegir varias)',
    options=list(cuauhtemoc['nom_colonia'].unique())
)

# File uploader for CSV
uploaded_file = st.sidebar.file_uploader("Carga CSV con lat y lon", type=["csv"])

# Initialize map centered on Cuauhtémoc
m = leafmap.Map(center=[19.4326, -99.1332], zoom=13)

# Conditional layer addition
if colonia == 'Ninguna' and not colonias_seleccionadas:
    # Display all colonias and all cordterritorios
    m.add_gdf(
        gdf=cuauhtemoc,
        zoom_to_layer=False,
        layer_name='Colonias',
        info_mode='on_click',
        style={'color': '#7fcdbb', 'fillOpacity': 0.3, 'weight': 0.5},
    )
elif colonia != 'Ninguna':
    # Filter and display the selected single colonia
    selected_gdf = cuauhtemoc[cuauhtemoc['nom_colonia'] == colonia]
    m.add_gdf(
        gdf=selected_gdf,
        layer_name=colonia,
        zoom_to_layer=True,
        style={'color': '#e6550d', 'fill': None, 'weight': 4},
    )
elif colonias_seleccionadas:
    # Filter and display multiple selected colonias
    selected_gdf = cuauhtemoc[cuauhtemoc['nom_colonia'].isin(colonias_seleccionadas)]
    m.add_gdf(
        gdf=selected_gdf,
        layer_name='Colonias seleccionadas',
        zoom_to_layer=True,
        style={'color': '#e6550d', 'fillOpacity': 0.3, 'weight': 0.5},
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
