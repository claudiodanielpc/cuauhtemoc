import streamlit as st
import geopandas as gpd
import leafmap
import pyogrio

# Load GeoJSON
#url = "https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/refs/heads/main/cuauhtemoc.geojson"
#uauhtemoc = gpd.read_file(url, driver="pyogrio")



#Mapa centrado en la alcaldía Cuauhtémoc

m = leafmap.Map()
m.add_tile_layer(
    url="https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}",
    name="Google Satellite",
    attribution="Google",
)
m

