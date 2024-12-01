import streamlit as st
import leafmap.foliumap as leafmap
from pyogrio import read_dataframe

# Load GeoJSON

cuauhtemoc=read_dataframe('https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/refs/heads/main/cuauhtemoc.geojson')

st.sidebar.title('About')
st.sidebar.info('Explore the Highway Statistics')
colonia = st.sidebar.selectbox('Selecciona una colonia', cuauhtemoc['nom_colonia'].unique())
#Mapa centrado en la alcaldía Cuauhtémoc

m = leafmap.Map(center=[19.4326, -99.1332], zoom=12)
m.add_gdf(
    gdf=cuauhtemoc,
    zoom_to_layer=False,
    layer_name='colonias',
    info_mode='on_click',
    style={'color': '#7fcdbb', 'fillOpacity': 0.3, 'weight': 0.5},
    )

selected_gdf = cuauhtemoc[cuauhtemoc['nom_colonia'] == colonia]

m.add_gdf(
    gdf=selected_gdf,
    layer_name='selected',
    zoom_to_layer=True,
    info_mode=None,
    style={'color': 'yellow', 'fill': None, 'weight': 2}
 )

#m.add_tile_layer(
#    url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
#    name="Google Satellite",
#    attribution="Google",
#)

m.to_streamlit(800, 600)

