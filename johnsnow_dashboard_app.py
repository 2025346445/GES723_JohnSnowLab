import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
from pyproj import Transformer
import streamlit.components.v1 as components

# ---------------------------------------------------
# 1. LOAD DATA
# ---------------------------------------------------
deaths_df = pd.read_csv("death.csv")
pumps_df = pd.read_csv("Pumps.csv")

# ---------------------------------------------------
# 2. TRANSFORM COORDINATES (British EPSG:27700 -> WGS84)
# ---------------------------------------------------
transformer = Transformer.from_crs("EPSG:27700", "EPSG:4326", always_xy=True)

def convert_xy_to_latlon(df, x_col="POINT_X", y_col="POINT_Y"):
    lons = []
    lats = []
    for _, row in df[[x_col, y_col]].iterrows():
        lon, lat = transformer.transform(row[x_col], row[y_col])
        lons.append(lon)
        lats.append(lat)
    df = df.copy()
    df["lon"] = lons
    df["lat"] = lats
    return df

deaths_ll = convert_xy_to_latlon(deaths_df)
pumps_ll = convert_xy_to_latlon(pumps_df)

# ---------------------------------------------------
# 3. STREAMLIT LAYOUT
# ---------------------------------------------------
st.set_page_config(page_title="John Snow Cholera Map 1854", layout="wide")

st.title("🗺️ John Snow 1854 Cholera Map Dashboard")

st.markdown("""
This dashboard visualizes the historic 1854 cholera outbreak in Soho, London, 
based on John Snow’s famous epidemiological map.

- Blue dots represent cholera death locations  
- Red markers represent water pump locations  
""")

# Sidebar navigation
page = st.sidebar.selectbox("Select View:", ["Map", "Data Table", "Summary"])

# ---------------------------------------------------
# 4. MAP VIEW
# ---------------------------------------------------
if page == "Map":
    st.subheader("Interactive Map of Cholera Deaths and Water Pumps")

    # Center map
    center_lat = deaths_ll["lat"].mean()
    center_lon = deaths_ll["lon"].mean()

    m = folium.Map(location=[center_lat, center_lon], zoom_start=17)

    # Death locations
    death_cluster = MarkerCluster(name="Cholera Deaths").add_to(m)
    for _, row in deaths_ll.iterrows():
        popup_text = f"Deaths Count: {row.get('Count', '')}"
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=3,
            color="blue",
            fill=True,
            fill_opacity=0.6,
            popup=popup_text
        ).add_to(death_cluster)

    # Water pumps
    pump_cluster = MarkerCluster(name="Water Pumps").add_to(m)
    for _, row in pumps_ll.iterrows():
        popup_text = f"Pump ID: {row.get('Id', '')}"
        folium.Marker(
            location=[row["lat"], row["lon"]],
            icon=folium.Icon(color="red", icon="tint", prefix="fa"),
            popup=popup_text
        ).add_to(pump_cluster)

    folium.LayerControl().add_to(m)

    # Render folium map
    components.html(m._repr_html_(), height=600, scrolling=False)

# ---------------------------------------------------
# 5. DATA TABLE VIEW
# ---------------------------------------------------
elif page == "Data Table":
    st.subheader("📄 Source Data Tables")
    st.write("### Cholera Deaths Data")
    st.dataframe(deaths_ll)
    st.write("### Water Pump Locations")
    st.dataframe(pumps_ll)

# ---------------------------------------------------
# 6. SUMMARY VIEW
# ---------------------------------------------------
elif page == "Summary":
    st.subheader("📊 Summary of Analysis")

    total_death_locations = len(deaths_ll)
    total_deaths = deaths_ll["Count"].sum() if "Count" in deaths_ll.columns else "N/A"
    total_pumps = len(pumps_ll)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Death Locations", total_death_locations)
    col2.metric("Total Death Count", total_deaths)
    col3.metric("Total Water Pumps", total_pumps)

    st.markdown("""
    **Brief Interpretation:**

    - Blue dots indicate the geographic distribution of cholera fatalities.
    - Red pump markers show the water sources available during the outbreak.
    - The clustering of deaths around a specific pump supports 
      John Snow’s conclusion that contaminated water was the source of the outbreak.

    This dashboard demonstrates how modern GIS and Python can recreate
    historic epidemiological analyses.
    """)
