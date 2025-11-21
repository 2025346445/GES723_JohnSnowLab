import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
import folium
from folium.plugins import MarkerCluster

# --------------------------------------------
# LOAD DATA
# --------------------------------------------
deaths_df = pd.read_csv("death.csv")
pumps_df = pd.read_csv("Pumps.csv")

# --------------------------------------------
# STREAMLIT LAYOUT
# --------------------------------------------
st.title("🗺️ John Snow Cholera Map (1854) – Streamlit Dashboard")

st.sidebar.header("Cholera 1854 Dashboard")
page = st.sidebar.selectbox("Select view:", ["Map", "Data Table", "Summary"])

# --------------------------------------------
# PAGE 1 – MAP
# --------------------------------------------
if page == "Map":
    st.subheader("Peta Kematian Kolera & Pam Air")

    # center map around data
    center_y = deaths_df["POINT_Y"].mean()
    center_x = deaths_df["POINT_X"].mean()

    m = folium.Map(location=[center_y, center_x], zoom_start=16)

    # add deaths
    death_cluster = MarkerCluster(name="Cholera Deaths").add_to(m)
    for _, row in deaths_df.iterrows():
        folium.CircleMarker(
            location=[row["POINT_Y"], row["POINT_X"]],
            radius=3,
            color="blue",
            fill=True,
            fill_opacity=0.6,
            popup=f"Deaths: {row['Count']}"
        ).add_to(death_cluster)

    # add water pumps
    pump_cluster = MarkerCluster(name="Water Pumps").add_to(m)
    for _, row in pumps_df.iterrows():
        folium.Marker(
            location=[row["POINT_Y"], row["POINT_X"]],
            icon=folium.Icon(color="red", icon="tint", prefix="fa"),
            popup="Water Pump"
        ).add_to(pump_cluster)

    folium.LayerControl().add_to(m)

    st_folium(m, width=700, height=500)

# --------------------------------------------
# PAGE 2 – DATA TABLE
# --------------------------------------------
elif page == "Data Table":
    st.subheader("📄 Jadual Data Asal")
    st.write("### Deaths")
    st.dataframe(deaths_df)
    st.write("### Pumps")
    st.dataframe(pumps_df)

# --------------------------------------------
# PAGE 3 – SUMMARY
# --------------------------------------------
elif page == "Summary":
    st.subheader("📊 Ringkasan Analisis")
    total_deaths = deaths_df["Count"].sum()
    total_points = len(deaths_df)
    total_pumps = len(pumps_df)

    st.metric("Jumlah Lokasi Kematian", total_points)
    st.metric("Jumlah Kematian Terkumpul", total_deaths)
    st.metric("Jumlah Pam Air", total_pumps)

    st.write("""
    **Interpretasi Ringkas:**
    Kawasan dengan taburan kematian paling tinggi terletak berhampiran salah satu pam air utama,
    seiring dengan penemuan John Snow pada tahun 1854.
    """)

