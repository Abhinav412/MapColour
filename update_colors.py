import utils

def update_colors_from_csv():
    """Read the CSV file and update the JSON file with country colors"""
    colors, success = utils.sync_csv_to_json()
    if success:
        print(f"Successfully updated {len(colors)} country colors in country_colors.json")
    else:
        print("Error updating colors")
    return success

if __name__ == "__main__":
    update_colors_from_csv()
