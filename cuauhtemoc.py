import streamlit as st
import pandas as pd
import leafmap.foliumap as leafmap
import geopandas as gpd
import pyogrio




#Mapa de la alcaldía cuauhtemoc
#Cargar colonias
url="https://raw.githubusercontent.com/claudiodanielpc/cuauhtemoc/refs/heads/main/cuauhtemoc.geojson"
cuauhtemoc=gpd.read_file(url,driver='pyogrio')


m = leafmap.Map(minimap_control=True,location=[19.4326, -99.1332], zoom_start=12)
#Add geojson
leafmap.add_geojson(cuauhtemoc, m, layer_name="Cuauhtemoc",fill_color="blue",fill_opacity=0.5)
m.to_streamlit(height=500)


