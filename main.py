import streamlit as st
import folium
from streamlit_folium import st_folium
import json
import os
import pandas as pd
from dotenv import load_dotenv
import utils

load_dotenv()

@st.cache_data
def load_countries_list():
    df = utils.get_all_countries_from_csv()
    return df['Countries'].tolist()

@st.cache_data
def get_geojson_data():
    local_path = os.path.join(os.path.dirname(__file__), 'world_countries.json')
    if os.path.exists(local_path):
        with open(local_path, 'r') as f:
            return json.load(f)
    
    import requests
    url = "https://raw.githubusercontent.com/python-visualization/folium/master/examples/data/world-countries.json"
    response = requests.get(url)
    return response.json()

def refresh_colors():
    st.session_state.country_colors = utils.load_country_colors()

if 'admin_authenticated' not in st.session_state:
    st.session_state.admin_authenticated = False
if 'country_colors' not in st.session_state:
    st.session_state.country_colors = utils.load_country_colors()

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

st.title("Interactive World Map")

with st.sidebar:
    st.header("Access Control")
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
    
    st.markdown("---")

nav_options = ["🗺️ Map Info"]
if st.session_state.admin_authenticated:
    nav_options.append("⚙️ Admin Panel")

selection = st.sidebar.radio("Navigation", nav_options)

if selection == "🗺️ Map Info":
    st.sidebar.subheader("Country Locator")
    all_countries = load_countries_list()
    
    default_index = 0
    if 'search_focus' in st.session_state:
        focus_val = st.session_state.search_focus
        if focus_val in all_countries:
            default_index = all_countries.index(focus_val)
    
    search_country = st.sidebar.selectbox("Search for a country:", ["None"] + all_countries, index=default_index + 1 if 'search_focus' in st.session_state else 0)
    
    if search_country == "None":
        if 'search_focus' in st.session_state:
            del st.session_state.search_focus
    else:
        st.session_state.search_focus = search_country

if selection == "⚙️ Admin Panel":
    st.sidebar.subheader("Admin Controls")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎨 Color Countries", "➕ Add Country", "➖ Remove Country", "📋 View All"])
    
    with tab1:
        st.markdown("**Select a country and set its color**")
        custom_countries = load_countries_list()
        selected_country = st.selectbox("Select country:", custom_countries, key="color_country")
        selected_color_name = st.selectbox("Set color:", list(utils.COLOR_MAPPING.keys()), key="color_select")
        
        if st.button("Apply Color", use_container_width=True, key="apply_color_btn"):
            success, msg = utils.update_country_color(selected_country, selected_color_name)
            if success:
                refresh_colors()
                st.success(msg)
            else:
                st.error(msg)
    
    with tab2:
        st.markdown("**Add a new country to the list**")
        new_country_name = st.text_input("Country Name", key="new_country_name")
        new_country_color = st.selectbox("Initial Color", list(utils.COLOR_MAPPING.keys()), key="new_country_color")
        
        if st.button("Add Country", use_container_width=True, key="add_country_btn"):
            if new_country_name.strip():
                success, msg = utils.add_country(new_country_name.strip(), new_country_color)
                if success:
                    refresh_colors()
                    st.success(msg)
                else:
                    st.error(msg)
            else:
                st.warning("Please enter a country name")
    
    with tab3:
        st.markdown("**Remove a country from the list**")
        remove_country = st.selectbox("Select country to remove:", ["None"] + load_countries_list(), key="remove_country_select")
        
        if remove_country != "None":
            st.warning(f"You are about to remove '{remove_country}' from the list")
            if st.button("Confirm Remove", use_container_width=True, key="remove_country_btn"):
                success, msg = utils.remove_country(remove_country)
                if success:
                    refresh_colors()
                    st.success(msg)
                else:
                    st.error(msg)
    
    with tab4:
        st.markdown("**All Countries and Colors**")
        df = utils.get_all_countries_from_csv()
        if not df.empty:
            df_display = df.copy()
            df_display.columns = ['Country', 'Color']
            st.dataframe(df_display, use_container_width=True)
            
            st.markdown(f"**Total: {len(df)} countries**")
        else:
            st.info("No countries in the list")
    
    st.divider()
    
    st.markdown("**Data Management**")
    
    if st.button("Migrate CSV to Supabase", use_container_width=True, help="One-time migration of countries from CSV to Supabase cloud database"):
        with st.spinner("Migrating data..."):
            count, success = utils.migrate_csv_to_supabase()
        if success:
            refresh_colors()
            st.success(f"Successfully migrated {count} countries to Supabase!")
        else:
            st.error("Migration failed. Check Supabase connection.")
    
    if st.button("Export to CSV", use_container_width=True):
        if utils.export_json_to_csv(st.session_state.country_colors):
            st.success("Exported to countries_export.csv")
        else:
            st.error("Export failed")
    
    if st.button("Clear All Colors", type="primary", use_container_width=True):
        utils.save_country_colors({})
        refresh_colors()
        st.rerun()

geojson_data = get_geojson_data()

map_center = [20, 0]
map_zoom = 2

focus_country = st.session_state.get('search_focus')

if focus_country:
    for feature in geojson_data['features']:
        if feature['properties']['name'] == focus_country:
            coords = feature['geometry']['coordinates']
            if feature['geometry']['type'] == 'Polygon':
                lon, lat = coords[0][0]
            elif feature['geometry']['type'] == 'MultiPolygon':
                lon, lat = coords[0][0][0]
            map_center = [lat, lon]
            map_zoom = 5
            break

m = folium.Map(location=map_center, zoom_start=map_zoom)

def style_function(feature):
    country_name = feature["properties"]["name"]
    is_focused = (country_name == focus_country)
    
    if country_name in st.session_state.country_colors:
        return {
            'fillColor': st.session_state.country_colors[country_name]["color"],
            'color': 'yellow' if is_focused else 'black',
            'weight': 4 if is_focused else 2.5,
            'fillOpacity': 0.9 if is_focused else 0.8,
            'stroke': True
        }
    
    return {
        'fillColor': '#FFFFFF',
        'color': 'yellow' if is_focused else 'black',
        'weight': 4 if is_focused else 1.5,
        'fillOpacity': 0.5 if is_focused else 0.2,
        'stroke': True
    }

folium.GeoJson(
    geojson_data,
    style_function=style_function,
    highlight_function=lambda x: {'weight': 4, 'fillOpacity': 0.8},
    tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['Country'])
).add_to(m)

st_folium(m, width=800, height=500)

st.markdown("### 🗺️ Color Legend")
if st.session_state.country_colors:
    cols = st.columns(len(utils.COLOR_MAPPING))
    for i, (color_name, color_hex) in enumerate(utils.COLOR_MAPPING.items()):
        with cols[i]:
            countries = [c for c, data in st.session_state.country_colors.items() if data["color_name"] == color_name]
            if countries:
                st.markdown(f"**{color_name}**")
                st.markdown(f"<div style='background-color: {color_hex}; width: 15px; height: 15px; border-radius: 50%; display: inline-block; margin-right: 5px;'></div>", unsafe_allow_html=True)
                
                for country in countries:
                    if st.button(country, key=f"legend_{country}"):
                        st.session_state.search_focus = country
                        st.rerun()
else:
    st.info("No countries colored yet")

st.sidebar.markdown("---")
st.sidebar.caption("Only administrators can modify the map colors. All users can view.")
