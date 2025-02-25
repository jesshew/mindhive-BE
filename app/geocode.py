import requests
import time
import os
from dotenv import load_dotenv

# # Load environment variables from .env file
load_dotenv()
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

"""
Geocodes a given address using Google Geocoding API.

Args:
- address (str): The address to be geocoded.

Returns:
- tuple: A tuple containing latitude and longitude coordinates (lat, lng).
            Returns (None, None) if geocoding fails.
"""
# Function to perform geocoding with Google Geocoding API
def geocode_google(address):
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {
        'address': address,
        'key': GOOGLE_API_KEY
    }
    
    try:
        response = requests.get(url, params=params)
        # print(f"Request URL: {response.url}")
        # print(f"Status Code: {response.status_code}")
        # print(f"Response Text: {response.text}")
        if response.status_code == 200:
            data = response.json()
            if 'results' in data and len(data['results']) > 0:
                location = data['results'][0]['geometry']['location']
                return location.get('lat'), location.get('lng')
    except requests.RequestException as e:
        print(f"Request failed: {e}")
    return None, None

def geocode_all_outlets(outlets):
    """
    Geocodes the addresses of multiple outlets using Google Geocoding API.

    Args:
    - outlets (list of dict): A list of outlets where each outlet is a dictionary
                              containing 'name', 'address', and optionally other details.

    Returns:
    - list of dict: The list of outlets updated with 'latitude' and 'longitude' keys
                    containing the geocoded coordinates.
    """
    for outlet in outlets:
        address = outlet['address']
        lat, lon = geocode_google(address)
        outlet['latitude'] = lat
        outlet['longitude'] = lon
        print(f"Geocoded: {outlet['name']} -> Lat: {lat}, Lon: {lon}")
    return outlets

