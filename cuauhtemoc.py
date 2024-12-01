import streamlit as st
import leafmap.foliumap as leafmap
from pyogrio import read_dataframe
import pandas as pd

# Load GeoJSON
cuauhtemoc = read_dataframe(
    'https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/refs/heads/main/cuauhtemoc.geojson')

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
    # Display all colonias if no specific selection
    m.add_gdf(
        gdf=cuauhtemoc,
        zoom_to_layer=False,
        layer_name='colonias',
        info_mode='on_click',
        style={'color': '#7fcdbb', 'fillOpacity': 0.3, 'weight': 0.5},
    )
else:
    # Display only the selected colonia
    selected_gdf = cuauhtemoc[cuauhtemoc['nom_colonia'] == colonia]
    m.add_gdf(
        gdf=selected_gdf,
        layer_name=colonia,
        zoom_to_layer=True,
        info_mode=None,
        style={'color': 'yellow', 'fill': None, 'weight': 4}
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
