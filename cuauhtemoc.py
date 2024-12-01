import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
import pyogrio

# Load GeoJSON

cuauhtemoc = gpd.read_file("https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/refs/heads/main/cuauhtemoc.geojson", driver="pyogrio")

st.sidebar.title('About')
st.sidebar.info('Explore the Highway Statistics')

#Mapa centrado en la alcaldía Cuauhtémoc

m = leafmap.Map(center=[19.4326, -99.1332], zoom=12)
m.add_gdf(
    gdf=cuauhtemoc,
    zoom_to_layer=False,
    layer_name='colonias',
    info_mode='on_click',
    style={'color': '#7fcdbb', 'fillOpacity': 0.3, 'weight': 0.5},
    )



#m.add_tile_layer(
#    url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
#    name="Google Satellite",
#    attribution="Google",
#)

m.to_streamlit(800, 600)

