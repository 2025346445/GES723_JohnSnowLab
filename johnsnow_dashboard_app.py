import streamlit as st
import pandas as pd
import folium
from folium.plugins import MarkerCluster
import streamlit.components.v1 as components
import math

# ---------------------------------------------------
# Manual conversion from EPSG:27700 (British Grid) to WGS84
# ---------------------------------------------------
def british_to_wgs84(easting, northing):
    # Reference ellipsoid
    a = 6377563.396
    b = 6356256.909
    F0 = 0.9996012717
    lat0 = 49 * math.pi/180
    lon0 = -2 * math.pi/180
    N0 = -100000
    E0 = 400000
    e2 = (a*a - b*b) / (a*a)
    n = (a - b) / (a + b)

    lat = lat0
    M = 0

    # Iterate to find latitude
    while True:
        lat_prev = lat
        M = b * F0 * (
            (1 + n + (5/4)*n**2 + (5/4)*n**3) * (lat - lat0)
            - (3*n + 3*n**2 + (21/8)*n**3) * math.sin(lat - lat0) * math.cos(lat + lat0)
            + ((15/8)*n**2 + (15/8)*n**3) * math.sin(2*(lat - lat0)) * math.cos(2*(lat + lat0))
            - (35/24)*n**3 * math.sin(3*(lat - lat0)) * math.cos(3*(lat + lat0))
        )
        lat = (northing - N0 - M) / (a * F0) + lat
        if abs(lat - lat_prev) < 1e-10:
            break

    v = a * F0 * (1 - e2 * math.sin(lat)**2)**-0.5
    rho = a * F0 * (1 - e2) * (1 - e2 * math.sin(lat)**2)**-1.5
    eta2 = v/rho - 1

    tan_lat = math.tan(lat)
    sec_lat = 1 / math.cos(lat)

    VII = tan_lat / (2*rho*v)
    VIII = tan_lat / (24*rho*v**3) * (5 + 3*tan_lat**2 + eta2 - 9*tan_lat**2*eta2)
    IX = tan_lat / (720*rho*v**5) * (61 + 90*tan_lat**2 + 45*tan_lat**4)
    X = sec_lat / v
    XI = sec_lat / (6 * v**3) * (v/rho + 2*tan_lat**2)
    XII = sec_lat / (120 * v**5) * (5 + 28*tan_lat**2 + 24*tan_lat**4)
    XIIA = sec_lat / (5040 * v**7) * (61 + 662*tan_lat**2 + 1320*tan_lat**4 + 720*tan_lat**6)

    dE = easting - E0

    lat_wgs = lat - VII*dE**2 + VIII*dE**4 - IX*dE**6
    lon_wgs = lon0 + X*dE - XI*dE**3 + XII*dE**5 - XIIA*dE**7

    return (lat_wgs * 180/math.pi, lon_wgs * 180/math.pi)

# ---------------------------------------------------
# LOAD DATA
# ---------------------------------------------------
deaths_df = pd.read_csv("death.csv")
pumps_df = pd.read_csv("Pumps.csv")

# Convert coordinates
deaths_df["lat"], deaths_df["lon"] = zip(*deaths_df.apply(lambda r: british_to_wgs84(r["POINT_X"], r["POINT_Y"]), axis=1))
pumps_df["lat"], pumps_df["lon"] = zip(*pumps_df.apply(lambda r: british_to_wgs84(r["POINT_X"], r["POINT_Y"]), axis=1))

# ---------------------------------------------------
# STREAMLIT UI
# ---------------------------------------------------
st.set_page_config(page_title="John Snow 1854 Cholera Map", layout="wide")

st.title("🗺️ John Snow’s 1854 Cholera Map Dashboard")

st.markdown("""
This dashboard visualizes the famous 1854 cholera outbreak in Soho, London,
mapping both death cases and water pumps as originally studied by Dr. John Snow.
""")

page = st.sidebar.selectbox("Select View", ["Map", "Data Table", "Summary"])

# ---------------------------------------------------
# MAP VIEW
# ---------------------------------------------------
if page == "Map":
    st.subheader("Interactive Map")

    m = folium.Map(location=[deaths_df["lat"].mean(), deaths_df["lon"].mean()], zoom_start=17)

    # Deaths
    death_cluster = MarkerCluster(name="Cholera Deaths").add_to(m)
    for _, row in deaths_df.iterrows():
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=3,
            color="blue",
            fill=True,
            fill_opacity=0.5,
            popup=f"Deaths Count: {row.get('Count')}"
        ).add_to(death_cluster)

    # Pumps
    pump_cluster = MarkerCluster(name="Water Pumps").add_to(m)
    for _, row in pumps_df.iterrows():
        folium.Marker(
            location=[row["lat"], row["lon"]],
            popup=f"Pump ID: {row.get('Id')}",
            icon=folium.Icon(color="red", icon="tint", prefix="fa")
        ).add_to(pump_cluster)

    folium.LayerControl().add_to(m)

    components.html(m._repr_html_(), height=600)

# ---------------------------------------------------
# DATA TABLE
# ---------------------------------------------------
elif page == "Data Table":
    st.subheader("Cholera Deaths Table")
    st.dataframe(deaths_df)

    st.subheader("Water Pump Locations")
    st.dataframe(pumps_df)

# ---------------------------------------------------
# SUMMARY
# ---------------------------------------------------
elif page == "Summary":
    st.subheader("Summary Statistics")

    total_locations = len(deaths_df)
    total_deaths = deaths_df["Count"].sum()
    total_pumps = len(pumps_df)

    col1, col2, col3 = st.columns(3)
    col1.metric("Death Locations", total_locations)
    col2.metric("Deaths Count", total_deaths)
    col3.metric("Water Pumps", total_pumps)

    st.markdown("""
    **Interpretation:**

    - Most cholera deaths cluster around a specific pump.
    - This supports John Snow’s hypothesis that contaminated water spread the disease.
    - Spatial analysis helps reveal unseen patterns in epidemiology.
    """)
