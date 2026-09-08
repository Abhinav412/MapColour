import streamlit as st # type: ignore
import folium # type: ignore
from streamlit_folium import st_folium # type: ignore
import json
import os
import pandas as pd
from dotenv import load_dotenv
import plotly.express as px # type: ignore
import utils
import regions

load_dotenv()

@st.cache_data(ttl=3600)
def load_countries_list():
    df = utils.get_all_countries_from_csv()
    return df['Countries'].tolist()

@st.cache_data(ttl=3600)
def get_geojson_data():
    with st.spinner("Loading map data..."):
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
if 'selected_region' not in st.session_state:
    st.session_state.selected_region = "All Regions"
if 'search_focus' not in st.session_state:
    st.session_state.search_focus = None

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD")

st.title("Interactive World Map")

st.markdown("""
<style>
    .stApp {
        background-color: #FFF8E7;
    }
    .country-link {
        display: inline-block;
        padding: 4px 8px;
        margin: 4px;
        font-size: 14px;
        font-weight: 500;
        cursor: pointer;
        text-decoration: none;
        color: inherit;
        white-space: nowrap;
    }
    .country-link:hover {
        text-decoration: underline;
    }
    .region-header { margin-top: 16px; margin-bottom: 8px; font-weight: 700; }
    .color-summary { margin-bottom: 12px; font-size: 14px; }
    .chip-container { display: flex; flex-wrap: wrap; gap: 4px; }
</style>
""", unsafe_allow_html=True)

# Handle query params for country focus from chip clicks
query_params = st.query_params
if 'focus' in query_params:
    focus_country = query_params['focus']
    if focus_country != st.session_state.get('search_focus'):
        st.session_state.search_focus = focus_country
        st.query_params.clear()
        st.rerun()

def render_sidebar():
    """Render sidebar content (not a fragment - allows reactivity)."""
    with st.sidebar:
        st.header("Access Control")
        if st.session_state.admin_authenticated:
            st.success("Logged in as Admin")
            if st.button("Logout", key="logout_btn"):
                st.session_state.admin_authenticated = False
        else:
            password = st.text_input("Admin Password", type="password", key="password_input")
            if st.button("Login", key="login_btn"):
                if password == ADMIN_PASSWORD:
                    st.session_state.admin_authenticated = True
                else:
                    st.error("Incorrect password")
        
        st.markdown("---")
        
        if st.session_state.admin_authenticated:
            st.subheader("Admin Controls")
            
            tab1, tab2, tab3, tab4 = st.tabs(["🎨 Color Countries", "➕ Add Country", "➖ Remove Country", "📋 View All"])
            
            with tab1:
                st.markdown("**Select a country and set its color**")
                custom_countries = load_countries_list()
                selected_country = st.selectbox("Select country:", custom_countries, key="color_country")
                selected_color_name = st.selectbox("Set color:", list(utils.COLOR_MAPPING.keys()), key="color_select")
                
                if st.button("Apply Color", width='stretch', key="apply_color_btn"):
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
                
                if st.button("Add Country", width='stretch', key="add_country_btn"):
                    if new_country_name.strip():
                        success, msg = utils.add_country(new_country_name.strip(), new_country_color)
                        if success:
                            st.cache_data.clear()
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
                    if st.button("Confirm Remove", width='stretch', key="remove_country_btn"):
                        success, msg = utils.remove_country(remove_country)
                        if success:
                            st.cache_data.clear()
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
                    st.dataframe(df_display, width='stretch')
                    
                    st.markdown(f"**Total: {len(df)} countries**")
                else:
                    st.info("No countries in the list")
            
            st.divider()
            
            st.markdown("**Data Management**")
            
            if st.button("Migrate CSV to Supabase", width='stretch', help="One-time migration of countries from CSV to Supabase cloud database"):
                with st.spinner("Migrating data..."):
                    count, success = utils.migrate_csv_to_supabase()
                if success:
                    refresh_colors()
                    st.success(f"Successfully migrated {count} countries to Supabase!")
                else:
                    st.error("Migration failed. Check Supabase connection.")
            
            if st.button("Export to CSV", width='stretch'):
                if utils.export_json_to_csv(st.session_state.country_colors):
                    st.success("Exported to countries_export.csv")
                else:
                    st.error("Export failed")
            
            if st.button("Clear All Colors", type="primary", width='stretch'):
                utils.save_country_colors({})
                refresh_colors()

        st.caption("Only administrators can modify the map colors. All users can view.")

# Render sidebar content
render_sidebar()

# Region Filter - MAIN LEVEL (triggers full rerun on change)
with st.sidebar:
    st.subheader("📍 Region Filter")
    
    region_options = ["All Regions"] + regions.REGION_LIST
    default_region_idx = 0
    if st.session_state.selected_region in region_options:
        default_region_idx = region_options.index(st.session_state.selected_region)
    
    selected_region = st.selectbox(
        "Select Region:", 
        region_options,
        index=default_region_idx,
        key="region_filter_main"
    )
    
    st.session_state.selected_region = selected_region

@st.cache_data(ttl=3600)
def get_region_geojson(full_geojson, region_name):
    """Return filtered GeoJSON with only region's countries."""
    if region_name == "All Regions":
        return full_geojson
    countries = set(regions.get_countries_by_region(region_name))
    return {
        "type": "FeatureCollection",
        "features": [f for f in full_geojson['features'] 
                    if f['properties']['name'] in countries]
    }

@st.cache_resource(ttl=3600)
def create_map_figure(region_geojson, country_colors, focus_country, region_name):
    """Create and return a folium map figure - memoized per region."""
    map_center = [20, 0]
    map_zoom = 2

    if focus_country:
        for feature in region_geojson['features']:
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

    region_filter_active = region_name != "All Regions"
    
    def style_function(feature):
        country_name = feature["properties"]["name"]
        is_focused = (country_name == focus_country)
        
        if region_filter_active:
            # For filtered regions, all features are already in the region
            pass
        
        if country_name in country_colors:
            return {
                'fillColor': country_colors[country_name]["color"],
                'color': 'grey' if is_focused else 'black',
                'weight': 2.5 if is_focused else 1.0,
                'fillOpacity': 0.9 if is_focused else 0.8,
                'stroke': True
            }
        
        return {
            'fillColor': '#FFFFFF',
            'color': 'grey' if is_focused else 'black',
            'weight': 2.5 if is_focused else 0.6,
            'fillOpacity': 0.5 if is_focused else 0.2,
            'stroke': True
        }

    folium.GeoJson(
        region_geojson,
        style_function=style_function,
        highlight_function=lambda x: {'weight': 2, 'fillOpacity': 0.8},
        tooltip=folium.GeoJsonTooltip(fields=['name'], aliases=['Country'])
    ).add_to(m)
    
    return m

@st.fragment
def map_fragment():
    geojson_data = get_geojson_data()
    selected_region = st.session_state.get('selected_region', 'All Regions')
    
    # Filter GeoJSON by region for performance
    region_geojson = get_region_geojson(geojson_data, selected_region)
    
    m = create_map_figure(
        region_geojson,
        st.session_state.country_colors,
        st.session_state.get('search_focus'),
        selected_region
    )

    st_folium(m, width='stretch', height=500, returned_objects=[])

def render_country_chips(region_name, countries, color_name, color_hex, color_emoji):
    """Render country names as plain text links without colored backgrounds."""
    if not countries:
        return
    
    # Build HTML links without chip styling - just emoji + country name
    chips_html = ''.join([
        f'<a href="?focus={country}" class="country-link">{color_emoji} {country}</a>'
        for country in countries
    ])
    
    container_html = f'<div class="chip-container">{chips_html}</div>'
    st.markdown(container_html, unsafe_allow_html=True)

def render_region_section(region_name, data):
    """Render a complete region section with color summary and country chips."""
    st.markdown(f'<div class="region-header">{region_name} ({data["colored"]}/{data["total"]} colored)</div>', unsafe_allow_html=True)
    
    # Color summary badges
    st.markdown(f'<div class="color-summary">🟢 {data["Green"]}  🟡 {data["Yellow"]}  🔴 {data["Red"]}  ⚪ {data["White"]}</div>', unsafe_allow_html=True)
    
    colored_countries = data["countries"]
    if not colored_countries:
        st.info("No colored countries in this region")
        return
    
    # Group by color: Green → Yellow → Red → White
    color_groups = {
        "Green": (sorted([c for c in colored_countries if st.session_state.country_colors.get(c, {}).get("color_name") == "Green"]), "🟢"),
        "Yellow": (sorted([c for c in colored_countries if st.session_state.country_colors.get(c, {}).get("color_name") == "Yellow"]), "🟡"),
        "Red": (sorted([c for c in colored_countries if st.session_state.country_colors.get(c, {}).get("color_name") == "Red"]), "🔴"),
        "White": (sorted([c for c in colored_countries if st.session_state.country_colors.get(c, {}).get("color_name") == "White"]), "⚪"),
    }
    
    for color_name, (countries, color_emoji) in color_groups.items():
        if countries:
            render_country_chips(region_name, countries, color_name, utils.COLOR_MAPPING[color_name], color_emoji)
    
    st.divider()

@st.fragment
def statistics_fragment():
    st.markdown("## 🌍 Region Statistics")
    
    # Create cache key from country_colors
    colors_key = tuple(sorted((k, v.get("color_name", "")) for k, v in st.session_state.country_colors.items()))
    region_counts = regions.get_all_regions_with_counts(colors_key)
    selected_region = st.session_state.get('selected_region', 'All Regions')
    
    if selected_region != "All Regions":
        # Show ONLY the selected region
        data = region_counts[selected_region]
        if data["colored"] > 0:
            render_region_section(selected_region, data)
        else:
            st.info(f"No colored countries in {selected_region}")
    else:
        # Show ALL regions with colored countries, expanded
        regions_with_data = [(r, region_counts[r]) for r in regions.REGION_LIST if region_counts[r]["colored"] > 0]
        
        if regions_with_data:
            for region_name, data in regions_with_data:
                render_region_section(region_name, data)
        else:
            st.info("No colored countries in any region yet")

# Stacked layout: Map on top, Statistics below
map_fragment()
statistics_fragment()