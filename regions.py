import streamlit as st

REGION_MAPPING = {
    # EUROPE (European countries)
    "Albania": "Europe",
    "Andorra": "Europe",
    "Austria": "Europe",
    "Belarus": "Europe",
    "Belgium": "Europe",
    "Bosnia and Herzegovina": "Europe",
    "Bulgaria": "Europe",
    "Croatia": "Europe",
    "Cyprus": "Europe",
    "Czechia": "Europe",
    "Denmark": "Europe",
    "Estonia": "Europe",
    "Faroe Islands": "Europe",
    "Finland": "Europe",
    "France": "Europe",
    "Germany": "Europe",
    "Gibraltar": "Europe",
    "Greece": "Europe",
    "Greenland": "Europe",
    "Guernsey": "Europe",
    "Hungary": "Europe",
    "Iceland": "Europe",
    "Ireland": "Europe",
    "Isle of Man": "Europe",
    "Italy": "Europe",
    "Jersey": "Europe",
    "Kosovo": "Europe",
    "Latvia": "Europe",
    "Liechtenstein": "Europe",
    "Lithuania": "Europe",
    "Luxembourg": "Europe",
    "Malta": "Europe",
    "Moldova": "Europe",
    "Monaco": "Europe",
    "Montenegro": "Europe",
    "Netherlands": "Europe",
    "North Macedonia": "Europe",
    "Norway": "Europe",
    "Poland": "Europe",
    "Portugal": "Europe",
    "Republic of Serbia": "Europe",
    "Romania": "Europe",
    "Russia": "Europe",
    "San Marino": "Europe",
    "Slovakia": "Europe",
    "Slovenia": "Europe",
    "Spain": "Europe",
    "Sweden": "Europe",
    "Switzerland": "Europe",
    "Ukraine": "Europe",
    "United Kingdom": "Europe",
    "Vatican": "Europe",
    
    # NORTH AMERICA (USA, Canada, Mexico + Caribbean)
    "Canada": "North America",
    "Mexico": "North America",
    "United States of America": "North America",
    "Anguilla": "North America",
    "Antigua and Barbuda": "North America",
    "Aruba": "North America",
    "Bahamas": "North America",
    "Barbados": "North America",
    "British Virgin Islands": "North America",
    "Cayman Islands": "North America",
    "Cuba": "North America",
    "Curaçao": "North America",
    "Dominica": "North America",
    "Dominican Republic": "North America",
    "Grenada": "North America",
    "Haiti": "North America",
    "Jamaica": "North America",
    "Montserrat": "North America",
    "Puerto Rico": "North America",
    "Saint Kitts and Nevis": "North America",
    "Saint Lucia": "North America",
    "Saint Martin": "North America",
    "Saint Vincent and the Grenadines": "North America",
    "Sint Maarten": "North America",
    "Trinidad and Tobago": "North America",
    "Turks and Caicos Islands": "North America",
    "United States Virgin Islands": "North America",
    
    # LATIN AMERICA (Central + South America)
    "Argentina": "Latin America",
    "Belize": "Latin America",
    "Bolivia": "Latin America",
    "Brazil": "Latin America",
    "Chile": "Latin America",
    "Colombia": "Latin America",
    "Costa Rica": "Latin America",
    "Ecuador": "Latin America",
    "El Salvador": "Latin America",
    "Falkland Islands": "Latin America",
    "French Guiana": "Latin America",
    "Guatemala": "Latin America",
    "Guyana": "Latin America",
    "Honduras": "Latin America",
    "Nicaragua": "Latin America",
    "Panama": "Latin America",
    "Paraguay": "Latin America",
    "Peru": "Latin America",
    "South Georgia and the Islands": "Latin America",
    "Suriname": "Latin America",
    "Uruguay": "Latin America",
    "Venezuela": "Latin America",
    
    # OCEANIA (Australia, NZ, Pacific Islands)
    "Australia": "Oceania",
    "New Zealand": "Oceania",
    "Fiji": "Oceania",
    "Kiribati": "Oceania",
    "Marshall Islands": "Oceania",
    "Micronesia": "Oceania",
    "Nauru": "Oceania",
    "New Caledonia": "Oceania",
    "Niue": "Oceania",
    "Norfolk Island": "Oceania",
    "Northern Mariana Islands": "Oceania",
    "Palau": "Oceania",
    "Papua New Guinea": "Oceania",
    "Pitcairn Islands": "Oceania",
    "Samoa": "Oceania",
    "Solomon Islands": "Oceania",
    "Tokelau": "Oceania",
    "Tonga": "Oceania",
    "Tuvalu": "Oceania",
    "Vanuatu": "Oceania",
    "Wallis and Futuna": "Oceania",
    "American Samoa": "Oceania",
    "Cook Islands": "Oceania",
    "French Polynesia": "Oceania",
    "Guam": "Oceania",
    "Heard Island and McDonald Islands": "Oceania",
    "Indian Ocean Territories": "Oceania",
    
    # MIDDLE EAST (Western Asia - Arabian peninsula, Levant, Iran)
    "Bahrain": "Middle East",
    "Iraq": "Middle East",
    "Israel": "Middle East",
    "Jordan": "Middle East",
    "Kuwait": "Middle East",
    "Lebanon": "Middle East",
    "Oman": "Middle East",
    "Palestine": "Middle East",
    "Qatar": "Middle East",
    "Saudi Arabia": "Middle East",
    "Syria": "Middle East",
    "United Arab Emirates": "Middle East",
    "Yemen": "Middle East",
    "Iran": "Middle East",
    "Afghanistan": "Middle East",
    "Turkey": "Middle East",  # Transcontinental but often grouped with Middle East
    
    # FAR EAST (East Asia)
    "China": "Far East",
    "Japan": "Far East",
    "South Korea": "Far East",
    "North Korea": "Far East",
    "Mongolia": "Far East",
    "Taiwan": "Far East",
    "Hong Kong S.A.R": "Far East",
    "Macao S.A.R": "Far East",
    
    # CENTRAL ASIA (Stans)
    "Kazakhstan": "Central Asia",
    "Uzbekistan": "Central Asia",
    "Kyrgyzstan": "Central Asia",
    "Tajikistan": "Central Asia",
    "Turkmenistan": "Central Asia",
    
    # SOUTH EAST ASIA (ASEAN + nearby)
    "Brunei": "South East Asia",
    "Cambodia": "South East Asia",
    "Indonesia": "South East Asia",
    "Laos": "South East Asia",
    "Malaysia": "South East Asia",
    "Myanmar": "South East Asia",
    "Philippines": "South East Asia",
    "Singapore": "South East Asia",
    "Thailand": "South East Asia",
    "Timor-Leste": "South East Asia",
    "Vietnam": "South East Asia",
    
    # SOUTH ASIA (Indian subcontinent)
    "Bangladesh": "South Asia",
    "Bhutan": "South Asia",
    "India": "South Asia",
    "Maldives": "South Asia",
    "Nepal": "South Asia",
    "Pakistan": "South Asia",
    "Sri Lanka": "South Asia",
    
    # AFRICA (All African countries)
    "Algeria": "Africa",
    "Angola": "Africa",
    "Benin": "Africa",
    "Botswana": "Africa",
    "Burkina Faso": "Africa",
    "Burundi": "Africa",
    "Cabo Verde": "Africa",
    "Cameroon": "Africa",
    "Central African Republic": "Africa",
    "Chad": "Africa",
    "Comoros": "Africa",
    "Democratic Republic of the Congo": "Africa",
    "Djibouti": "Africa",
    "Egypt": "Africa",
    "Equatorial Guinea": "Africa",
    "Eritrea": "Africa",
    "Eswatini": "Africa",
    "Ethiopia": "Africa",
    "Gabon": "Africa",
    "Gambia": "Africa",
    "Ghana": "Africa",
    "Guinea": "Africa",
    "Guinea-Bissau": "Africa",
    "Ivory Coast": "Africa",
    "Kenya": "Africa",
    "Lesotho": "Africa",
    "Liberia": "Africa",
    "Libya": "Africa",
    "Madagascar": "Africa",
    "Malawi": "Africa",
    "Mali": "Africa",
    "Mauritania": "Africa",
    "Mauritius": "Africa",
    "Morocco": "Africa",
    "Mozambique": "Africa",
    "Namibia": "Africa",
    "Niger": "Africa",
    "Nigeria": "Africa",
    "Republic of the Congo": "Africa",
    "Rwanda": "Africa",
    "Sao Tome and Principe": "Africa",
    "Senegal": "Africa",
    "Seychelles": "Africa",
    "Sierra Leone": "Africa",
    "Somalia": "Africa",
    "Somaliland": "Africa",
    "South Africa": "Africa",
    "South Sudan": "Africa",
    "Sudan": "Africa",
    "Tanzania": "Africa",
    "Togo": "Africa",
    "Tunisia": "Africa",
    "Uganda": "Africa",
    "Zambia": "Africa",
    "Zimbabwe": "Africa",
    "Western Sahara": "Africa",
    "Republic of Tanzania": "Africa",
    
    # CAUCASUS (Georgia, Armenia, Azerbaijan - sometimes Europe, sometimes Asia)
    "Armenia": "Caucasus",
    "Azerbaijan": "Caucasus",
    "Georgia": "Caucasus",
    
    # UNTRACKED/TERRITORIES (Will show as "Untracked")
    "Antarctica": "Untracked",
    "Akrotiri Sovereign Base Area": "Untracked",
    "Aland": "Untracked",
    "Ashmore and Cartier Islands": "Untracked",
    "Bajo Nuevo Bank (Petrel Is.)": "Untracked",
    "Baykonur Cosmodrome": "Untracked",
    "Bir Tawil": "Untracked",
    "Brazilian Island": "Untracked",
    "British Indian Ocean Territory": "Untracked",
    "Clipperton Island": "Untracked",
    "Coral Sea Islands": "Untracked",
    "Cyprus No Mans Area": "Untracked",
    "Dhekelia Sovereign Base Area": "Untracked",
    "French Southern and Antarctic Lands": "Untracked",
    "Hong Kong S.A.R.": "Untracked",  # Already in Far East, duplicate
    "Macao S.A.R": "Untracked",  # Already in Far East, duplicate
    "Siachen Glacier": "Untracked",
    "Scarborough Reef": "Untracked",
    "Serranilla Bank": "Untracked",
    "Southern Patagonian Ice Field": "Untracked",
    "Spratly Islands": "Untracked",
    "US Naval Base Guantanamo Bay": "Untracked",
    "United States Minor Outlying Islands": "Untracked",
    "eSwatini": "Untracked",  # Duplicate entry, should be Eswatini
    "S�o Tom� and Principe": "Untracked",  # Encoding issue
}

REGION_LIST = [
    "Europe",
    "North America",
    "Latin America",
    "Oceania",
    "Middle East",
    "Far East",
    "Central Asia",
    "South East Asia",
    "South Asia",
    "Africa",
    "Caucasus",
    "Untracked"
]

def get_region(country_name):
    return REGION_MAPPING.get(country_name, "Untracked")

def get_countries_by_region(region):
    return [country for country, reg in REGION_MAPPING.items() if reg == region]

@st.cache_data(ttl=3600)
def get_all_regions_with_counts(colors_key):
    """Get region statistics with caching.
    
    Args:
        colors_key: Tuple of (country_name, color_name) pairs for caching
    """
    # Convert back to dict for processing
    colors_dict = {k: {"color_name": v} for k, v in colors_key}
    
    region_counts = {}
    for region in REGION_LIST:
        countries = get_countries_by_region(region)
        colored_countries = [c for c in countries if c in colors_dict]
        
        green = sum(1 for c in colored_countries if colors_dict.get(c, {}).get("color_name") == "Green")
        yellow = sum(1 for c in colored_countries if colors_dict.get(c, {}).get("color_name") == "Yellow")
        red = sum(1 for c in colored_countries if colors_dict.get(c, {}).get("color_name") == "Red")
        white = sum(1 for c in colored_countries if colors_dict.get(c, {}).get("color_name") == "White")
        uncolored = len(countries) - len(colored_countries)
        
        region_counts[region] = {
            "total": len(countries),
            "colored": len(colored_countries),
            "uncolored": uncolored,
            "Green": green,
            "Yellow": yellow,
            "Red": red,
            "White": white,
            "countries": colored_countries
        }
    return region_counts
