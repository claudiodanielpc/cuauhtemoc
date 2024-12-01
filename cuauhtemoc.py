import streamlit as st
import leafmap.foliumap as leafmap
from pyogrio import read_dataframe
import pandas as pd

# Load GeoJSON
cuauhtemoc = read_dataframe(
    'https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/refs/heads/main/cuauhtemoc.geojson')

# Sidebar configuration
st.sidebar.title('About')
st.sidebar.info('Explore the Highway Statistics')

# Dropdown for selecting a colonia
colonia = st.sidebar.selectbox('Selecciona una colonia',
                               ['Todas las colonias'] + list(cuauhtemoc['nom_colonia'].unique()))

# File uploader for CSV
uploaded_file = st.sidebar.file_uploader("Upload a CSV with Latitude and Longitude", type=["csv"])

# Initialize map centered on Cuauhtémoc
m = leafmap.Map(center=[19.4326, -99.1332], zoom=12)

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
        style={'color': 'yellow', 'fill': None, 'weight': 2}
    )

# Handle uploaded CSV
if uploaded_file is not None:
    # Read CSV into a DataFrame
    df = pd.read_csv(uploaded_file)

    # Check if required columns are present
    if 'lat' in df.columns and 'lon' in df.columns:
        # Drop rows with missing lat or lon
        df = df.dropna(subset=['lat', 'lon'])

        # Add points from CSV to the map
        for _, row in df.iterrows():
            m.add_marker(
                location=(row['lat'], row['lon']),
                popup=str(row.to_dict()),  # Show row details as a popup
            )
    else:
        st.error("The uploaded CSV must contain 'lat' and 'lon' columns.")

# Render map in Streamlit
m.to_streamlit(1000, 800)
