import streamlit as st
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import folium
from folium.plugins import MarkerCluster
from streamlit_folium import st_folium


# ==============================

# ==============================
@st.cache_data
def load_data():

   
    deaths_df = pd.read_csv("death.csv")
    pumps_df  = pd.read_csv("Pumps.csv")

   
    deaths_gdf = gpd.GeoDataFrame(
        deaths_df,
        geometry=gpd.points_from_xy(deaths_df["POINT_X"], deaths_df["POINT_Y"]),
        crs="EPSG:27700"
    )

    pumps_gdf = gpd.GeoDataFrame(
        pumps_df,
        geometry=gpd.points_from_xy(pumps_df["POINT_X"], pumps_df["POINT_Y"]),
        crs="EPSG:27700"
    )

    
    deaths_wgs = deaths_gdf.to_crs(epsg=4326)
    pumps_wgs  = pumps_gdf.to_crs(epsg=4326)

    return deaths_wgs, pumps_wgs


# ==============================
# Main App
# ==============================
def main():

    st.set_page_config(page_title="John Snow 1854 Dashboard", layout="wide")

    st.title("John Snow's Cholera Dashboard, 1854")

    st.markdown("""
   John Snow's map is used to create an interactive representation of cholera death cases from 1854.

    - Blue dot = death location 
    - Red triangle = water pump location 
    """)

    # -------- Load data ----------
    deaths_gdf, pumps_gdf = load_data()

    # -------- Sidebar ------------
    st.sidebar.header("Map Settings")

    show_deaths = st.sidebar.checkbox("Show deaths", value=True)
    show_pumps  = st.sidebar.checkbox("Show water pump", value=True)

   
    if "Count" in deaths_gdf.columns:
        max_count = int(deaths_gdf["Count"].max())
        min_count = st.sidebar.slider(
            "Minimum Count:",
            1,
            max_count,
            1
        )
        deaths_plot = deaths_gdf[deaths_gdf["Count"] >= min_count].copy()
    else:
        deaths_plot = deaths_gdf.copy()

    
    center_x = deaths_plot.geometry.x.mean()
    center_y = deaths_plot.geometry.y.mean()

    m = folium.Map(location=[center_y, center_x], zoom_start=17)

  
    if show_deaths:
        cluster = MarkerCluster().add_to(m)
        for _, row in deaths_plot.iterrows():
            popup = f"ID: {row.get('Id', '')}"
            if "Count" in row:
                popup += f"<br>Count: {row['Count']}"
            folium.CircleMarker(
                [row.geometry.y, row.geometry.x],
                radius=3,
                fill=True,
                fill_opacity=0.7,
                popup=folium.Popup(popup, max_width=200)
            ).add_to(cluster)

   
    if show_pumps:
        for _, row in pumps_gdf.iterrows():
            popup = f"Pump ID: {row.get('Id', '')}"
            folium.Marker(
                [row.geometry.y, row.geometry.x],
                icon=folium.Icon(color="red", icon="tint", prefix="fa"),
                popup=popup
            ).add_to(m)

    st.subheader("Interactive Map")
    st_folium(m, width=900, height=600)

    
    st.subheader("Source Data")

    col1, col2 = st.columns(2)

    col1.write("Deaths:")
    col1.dataframe(deaths_gdf.drop(columns="geometry").head())

    col2.write("Water pumps:")
    col2.dataframe(pumps_gdf.drop(columns="geometry").head())


if __name__ == "__main__":
    main()
