import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import requests
from branca.colormap import linear
import os
from dotenv import load_dotenv

load_dotenv()

if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'country_colors' not in st.session_state:
    st.session_state.country_colors = {}

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

st.title("Interactive World Map")

with st.sidebar.expander("Admin Access"):
    if st.session_state.admin_authenticated:
        st.success("Logged in as Admin")
        if st.button("Logout"):
            st.session_state.admin_authenticated = False
            st.rerun()
    else:
        password = st.text_input("Admin Password", type="password")
        if st.button("Login"):
            if password == ADMIN_PASSWORD:
                st.session_state.admin_authenticated = True
                st.rerun()
            else:
                st.error("Incorrect password")

st.sidebar.header("Map Controls")

custom_countries = [
    "Austria","Belarus","Bosnia and Herzegovina","Cyprus","Czech Republic","Finland",
    "Georgia","Greece","Hungary","Ireland","Kosovo","Latvia","Luxembourg","Macedonia",
    "Malta","Montenegro","Romania","Serbia","Slovakia","Slovenia","Ukraine","Belgium",
    "Croatia","Denmark","Estonia","France","Germany","Lithuania","Norway","Portugal", 
    "Spain","Sweden","Switzerland","Netherlands","Albania","Andorra","Armenia","Azerbaijan",
    "Bulgaria","Channel Islands","Greenland","Iceland","Israel","Italy","Moldova","Monaco", 
    "Morocco","Poland","San Marino","Turkey","Indonesia","Laos","Malaysia","Mongolia","Myanmar",
    "United Kingdom","Philippines","Singapore","South Korea","Taiwan","Thailand","Vietnam","Bahrain",
    "Japan","Egypt","Jordan","Kuwait","Lebanon","Oman","Qatar","Saudi Arabia",
    "United Arab Emirates","Australia","Fiji","New Zealand"
]

@st.cache_data
def get_geojson_data():
    url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
    response = requests.get(url)
    return response.json()

geojson_data = get_geojson_data()

if st.session_state.admin_authenticated:
    st.sidebar.subheader("Edit Map Colors (Admin Only)")
    
    selected_country = st.sidebar.selectbox("Select a country:", custom_countries)
    
    color_options = {
        "Red": "#FF0000",
        "Green": "#00FF00",
        "Yellow": "#FFFF00"
    }
    selected_color_name = st.sidebar.selectbox("Select color to highlight country:", list(color_options.keys()))
    selected_color = color_options[selected_color_name]
    
    if st.sidebar.button("Apply Color"):
        st.session_state.country_colors[selected_country] = {
            "color": selected_color,
            "color_name": selected_color_name
        }
        st.success(f"Color {selected_color_name} applied to {selected_country}")
    
st.sidebar.subheader("Currently Colored Countries")
if st.session_state.country_colors:
    if st.session_state.admin_authenticated:
        edit_country = st.sidebar.selectbox("Select country to edit:", 
                                          ["None"] + list(st.session_state.country_colors.keys()))
        
        if edit_country != "None":
            col1, col2 = st.sidebar.columns(2)
            
            with col1:
                edit_color = st.selectbox(
                    "Change color:", 
                    list(color_options.keys()),
                    index=list(color_options.keys()).index(st.session_state.country_colors[edit_country]["color_name"]) 
                    if edit_country in st.session_state.country_colors else 0
                )
            
            with col2:
                if st.button("Update"):
                    st.session_state.country_colors[edit_country] = {
                        "color": color_options[edit_color],
                        "color_name": edit_color
                    }
                    st.success(f"Updated {edit_country} to {edit_color}")
                    st.rerun()
                
                if st.button("Clear"):
                    del st.session_state.country_colors[edit_country]
                    st.success(f"Cleared color for {edit_country}")
                    st.rerun()
    st.sidebar.subheader("Color Legend")
    for country, color_data in st.session_state.country_colors.items():
        color_hex = color_data["color"]
        st.sidebar.markdown(
            f"<div style='display: flex; align-items: center;'>"
            f"<div style='background-color: {color_hex}; width: 15px; height: 15px; margin-right: 8px;'></div>"
            f"<div>{country}: {color_data['color_name']}</div>"
            f"</div>",
            unsafe_allow_html=True
        )
else:
    st.sidebar.text("No countries colored yet")

if st.session_state.admin_authenticated and st.session_state.country_colors:
    if st.sidebar.button("Clear All Colors"):
        st.session_state.country_colors = {}
        st.success("All country colors cleared")
        st.rerun()

m = folium.Map(location=[20, 0], zoom_start=2)

def style_function(feature):
    country_name = feature["properties"]["name"]
    if country_name in st.session_state.country_colors:
        return {
            'fillColor': st.session_state.country_colors[country_name]["color"],
            'color': 'black',
            'weight': 2,
            'fillOpacity': 0.7
        }
    else:
        return {
            'fillColor': '#FFFFFF',
            'color': 'black',
            'weight': 1,
            'fillOpacity': 0.1
        }

folium.GeoJson(
    geojson_data,
    style_function=style_function,
    highlight_function=lambda x: {'weight': 3, 'fillOpacity': 0.7},
    tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['Country'])
).add_to(m)

if st.session_state.admin_authenticated:
    current_color_text = f"with {selected_color_name.lower()} color" if 'selected_country' in locals() and selected_country in st.session_state.country_colors else "(not yet colored)"
    st.write(f"**Currently selected:** {selected_country if 'selected_country' in locals() else 'None'} {current_color_text}")

st_folium(m, width=700, height=500)

st.sidebar.markdown("---")
st.sidebar.info("Only administrators can modify the map colors. All users can view the map.")