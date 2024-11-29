import streamlit as st
import pandas as pd
import leafmap.foliumap as leafmap
import geopandas as gpd
import pyogrio




#Mapa de la alcaldía cuauhtemoc


m = leafmap.Map(minimap_control=True,location=[19.4326, -99.1332], zoom_start=12)
m.add_basemap("OpenTopoMap")
m.to_streamlit(height=500)