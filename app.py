import streamlit as st
import pandas as pd
import geopandas as gpd
import folium
from folium import FeatureGroup
from streamlit.components.v1 import html as st_html

# Cargar los datos
pisos = pd.read_csv("datos/pisos_modificado.csv")
vecindario = gpd.read_file('datos/neighbourhoods.geojson')

# Convertir la columna 'coord' a geometría
pisos['geometry'] = gpd.GeoSeries.from_wkt(pisos['coord'])
gdf_pisos = gpd.GeoDataFrame(pisos, geometry='geometry')

# Configuración de la aplicación
st.title('🗺️ AirBnB en Madrid')

st.write("""
    ### Bienvenido a la aplicación de AirBnB en Madrid
    Utiliza los filtros en la barra lateral para seleccionar un barrio y el tipo de habitación.
    El mapa se actualizará automáticamente para mostrar las propiedades según tus criterios.
""")

# Sidebar para filtros
st.sidebar.header('🔍 Filtros')

neighbourhood = st.sidebar.selectbox(
    'Selecciona un barrio:',
    vecindario['neighbourhood'].unique()
)

selroom_type = st.sidebar.selectbox(
    'Selecciona el tipo de habitación:',
    gdf_pisos['room_type'].unique()
)

price_range = st.sidebar.slider(
    'Selecciona el rango de precios',
    min_value=0, max_value=1000, value=(0, 500)
)

# Filtrar los datos de pisos por el barrio seleccionado
geom = vecindario[vecindario['neighbourhood'] == neighbourhood].geometry.iloc[0]
gdf_neighbourhood = gdf_pisos[gdf_pisos.geometry.within(geom)]
filtrado = gdf_neighbourhood[(gdf_neighbourhood['room_type'] == selroom_type) &
                             (gdf_neighbourhood['price'] >= price_range[0]) &
                             (gdf_neighbourhood['price'] <= price_range[1])]

# Crear un mapa
m = folium.Map(location=[40.41678, -3.70379], zoom_start=13)

# Crear FeatureGroups para diferentes categorías de precio
categories_precio = {
    'Muy baratos': 'blue',
    'Baratos': 'green',
    'Precio medio': 'orange',
    'Caros': 'red',
    'Muy caros': 'purple'
}

# Añadir capas al mapa
for category, color in categories_precio.items():
    fg = FeatureGroup(name=category)
    filtered = filtrado[filtrado['price_category'] == category]
    
    for _, row in filtered.iterrows():
        coords = row['geometry'].coords[0]  # Obtener latitud y longitud
        
        folium.Marker(
            location=[coords[1], coords[0]],  # Folium usa [latitud, longitud]
            popup=f'<b>Price:</b> {row["price"]}<br><b>Type:</b> {row["room_type"]}',
            icon=folium.Icon(color=color, icon='info-sign')  # Cambia el icono aquí
        ).add_to(fg)
    
    fg.add_to(m)

# Añadir control de capas al mapa
folium.LayerControl().add_to(m)

# Mostrar el mapa en Streamlit
map_html = m._repr_html_()  # Convertir el mapa a HTML
st_html(map_html, height=600, scrolling=True)  # Mostrar el mapa en la aplicación
