import pandas as pd
import json
import os

def update_colors_from_csv():
    """Read the CSV file and update the JSON file with country colors"""
    try:
        df = pd.read_csv("countries.csv")
        color_mapping = {
            "Red": "#FF0000",
            "Green": "#00FF00",
            "Yellow": "#FFFF00"
        }
        colors_dict = {}
        for _, row in df.iterrows():
            country = row['Countries']
            color_name = row['Colour']
            if color_name in color_mapping:
                colors_dict[country] = {
                    "color": color_mapping[color_name],
                    "color_name": color_name
                }
        with open('country_colors.json', 'w') as f:
            json.dump(colors_dict, f)
        
        print(f"Successfully updated {len(colors_dict)} country colors in country_colors.json")
        return True
    except Exception as e:
        print(f"Error updating colors: {e}")
        return False

if __name__ == "__main__":
    update_colors_from_csv()