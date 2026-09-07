import json
import os
import pandas as pd
from supabase import create_client
from unidecode import unidecode

COLOR_MAPPING = {
    "Red": "#FF0000",
    "Green": "#00FF00",
    "Yellow": "#FFFF00",
    "White": "#FFFFFF"
}

NAME_NORMALIZATION_MAP = {
    "Bahamas": "The Bahamas",
    "Trinidad & Tobago": "Trinidad and Tobago",
    "Timor-Leste": "East Timor",
    "Guinea-Bissau": "Guinea Bissau",
    "Domanican Republic": "Dominican Republic",
    "San Mariono": "San Marino",
    "Swaziland": "Eswatini",
}

def get_supabase_client():
    return create_client(
        os.environ.get("SUPABASE_URL"),
        os.environ.get("SUPABASE_KEY")
    )

def get_colors_file_path():
    return os.path.join(os.path.dirname(__file__), 'country_colors.json')

def get_csv_path():
    return os.path.join(os.path.dirname(__file__), 'countries.csv')

def normalize_country_name(name):
    mapped = NAME_NORMALIZATION_MAP.get(name, name)
    return unidecode(mapped)

def get_geojson_country_names():
    geojson_path = os.path.join(os.path.dirname(__file__), 'world_countries.json')
    if os.path.exists(geojson_path):
        with open(geojson_path, 'r') as f:
            data = json.load(f)
            return set(feature['properties']['name'] for feature in data['features'])
    return set()

def country_exists_in_geojson(name):
    normalized = normalize_country_name(name)
    return normalized in get_geojson_country_names()

def load_country_colors():
    try:
        supabase = get_supabase_client()
        response = supabase.table("country_colors").select("*").execute()
        colors_dict = {}
        for row in response.data:
            original_name = row['country_name']
            unidecoded_name = unidecode(original_name)
            color_data = {
                "color": row['color_code'],
                "color_name": row['color_name']
            }
            colors_dict[original_name] = color_data
            colors_dict[unidecoded_name] = color_data
        return colors_dict
    except Exception as e:
        print(f"Error loading from Supabase: {e}")
        return {}

def save_country_colors(colors_dict):
    try:
        supabase = get_supabase_client()
        for country, data in colors_dict.items():
            supabase.table("country_colors").upsert({
                "country_name": country,
                "color_code": data["color"],
                "color_name": data["color_name"]
            }, on_conflict='country_name').execute()
        return True
    except Exception as e:
        print(f"Error saving to Supabase: {e}")
        return False

def get_all_countries_from_csv():
    try:
        df = pd.read_csv(get_csv_path())
        return df
    except Exception:
        return pd.DataFrame(columns=['Countries', 'Colour'])

def save_all_countries(df):
    df.to_csv(get_csv_path(), index=False)

def add_country(name, color_name):
    normalized_name = normalize_country_name(name)
    if color_name not in COLOR_MAPPING:
        return False, f"Invalid color: {color_name}"
    
    df = get_all_countries_from_csv()
    if normalized_name in df['Countries'].values:
        return False, f"Country '{name}' already exists"
    
    new_row = pd.DataFrame([{'Countries': normalized_name, 'Colour': color_name}])
    df = pd.concat([df, new_row], ignore_index=True)
    save_all_countries(df)
    
    try:
        supabase = get_supabase_client()
        supabase.table("country_colors").upsert({
            "country_name": normalized_name,
            "color_code": COLOR_MAPPING[color_name],
            "color_name": color_name
        }, on_conflict='country_name').execute()
    except Exception as e:
        print(f"Warning: CSV saved but Supabase sync failed: {e}")
    
    return True, f"Added '{normalized_name}' with color {color_name}"

def remove_country(name):
    normalized_name = normalize_country_name(name)
    df = get_all_countries_from_csv()
    if normalized_name not in df['Countries'].values:
        return False, f"Country '{name}' not found"
    
    df = df[df['Countries'] != normalized_name]
    save_all_countries(df)
    
    try:
        supabase = get_supabase_client()
        supabase.table("country_colors").delete().eq("country_name", normalized_name).execute()
    except Exception as e:
        print(f"Warning: CSV saved but Supabase delete failed: {e}")
    
    return True, f"Removed '{normalized_name}'"

def update_country_color(name, color_name):
    normalized_name = normalize_country_name(name)
    if color_name not in COLOR_MAPPING:
        return False, f"Invalid color: {color_name}"
    
    df = get_all_countries_from_csv()
    if normalized_name not in df['Countries'].values:
        return False, f"Country '{name}' not found"
    
    df.loc[df['Countries'] == normalized_name, 'Colour'] = color_name
    save_all_countries(df)
    
    try:
        supabase = get_supabase_client()
        supabase.table("country_colors").upsert({
            "country_name": normalized_name,
            "color_code": COLOR_MAPPING[color_name],
            "color_name": color_name
        }, on_conflict='country_name').execute()
    except Exception as e:
        print(f"Warning: CSV saved but Supabase update failed: {e}")
    
    return True, f"Updated '{normalized_name}' to {color_name}"

def migrate_csv_to_supabase():
    try:
        df = get_all_countries_from_csv()
        supabase = get_supabase_client()
        count = 0
        
        for _, row in df.iterrows():
            country = row['Countries']
            color_name = row['Colour']
            if color_name in COLOR_MAPPING:
                supabase.table("country_colors").upsert({
                    "country_name": country,
                    "color_code": COLOR_MAPPING[color_name],
                    "color_name": color_name
                }, on_conflict='country_name').execute()
                count += 1
        
        return count, True
    except Exception as e:
        return 0, False

def sync_csv_to_json():
    try:
        df = get_all_countries_from_csv()
        colors_dict = {}
        for _, row in df.iterrows():
            country = row['Countries']
            color_name = row['Colour']
            if color_name in COLOR_MAPPING:
                colors_dict[country] = {
                    "color": COLOR_MAPPING[color_name],
                    "color_name": color_name
                }
        save_country_colors(colors_dict)
        return colors_dict, True
    except Exception as e:
        return {}, False

def export_json_to_csv(colors_dict, csv_path="countries_export.csv"):
    try:
        data = []
        for country, info in colors_dict.items():
            data.append({"Countries": country, "Colour": info["color_name"]})
        df = pd.DataFrame(data)
        df.to_csv(csv_path, index=False)
        return True
    except Exception:
        return False
