import streamlit as st
import geopandas as gpd
import leafmap.foliumap as leafmap
import pyogrio

# Load GeoJSON
#url = "https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/refs/heads/main/cuauhtemoc.geojson"
#uauhtemoc = gpd.read_file(url, driver="pyogrio")

st.sidebar.title('About')
st.sidebar.info('Explore the Highway Statistics')

#Mapa centrado en la alcaldía Cuauhtémoc

m = leafmap.Map(center=[19.4326, -99.1332], zoom=12)
#m.add_tile_layer(
#    url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
#    name="Google Satellite",
#    attribution="Google",
#)

m.to_streamlit()

