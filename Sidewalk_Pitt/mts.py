#!/usr/bin/env python3
import requests
import json
import os
from time import sleep

# --- Step 1: Download the GeoJSON data from ArcGIS ---
def download_arcgis_geojson(url, params):
    print("Fetching GeoJSON data from ArcGIS...")
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()
    print("Data successfully fetched.")
    return data

# --- Step 2: Convert GeoJSON to line-delimited GeoJSON ---
def convert_to_ldjson(geojson_data, output_filepath):
    print(f"Converting data to line-delimited GeoJSON and saving to {output_filepath}...")
    # Open the file for writing
    with open(output_filepath, "w", encoding="utf-8") as f:
        # Each feature is written as a separate JSON object on its own line.
        for feature in geojson_data.get("features", []):
            f.write(json.dumps(feature) + "\n")
    print("Conversion complete.")

# --- Create or update a tileset source ---
def create_or_update_source(username, source_id, filepath, access_token):
    print(f"Creating or updating tileset source {username}/{source_id}...")
    
    # Read the file content
    with open(filepath, 'rb') as f:
        files = {'file': ('data.geojson', f, 'application/json')}
        
        # Create or update the tileset source
        url = f'https://api.mapbox.com/tilesets/v1/sources/{username}/{source_id}?access_token={access_token}'
        response = requests.put(url, files=files)
        
        if response.status_code == 200:
            print("Source created/updated successfully!")
            return response.json()
        else:
            print(f"Error creating/updating source: {response.text}")
            response.raise_for_status()

# --- Create or update a tileset ---
def create_or_update_tileset(username, tileset_id, source_id, access_token):
    print(f"Creating or updating tileset {tileset_id}...")
    
    # Recipe for the tileset
    recipe = {
        "version": 1,
        "layers": {
            "sidewalks": {
                "source": f"mapbox://tileset-source/{username}/{source_id}",
                "minzoom": 12,
                "maxzoom": 18
            }
        }
    }
    
    # Create or update the tileset
    url = f'https://api.mapbox.com/tilesets/v1/{tileset_id}?access_token={access_token}'
    response = requests.post(url, json=recipe)
    
    if response.status_code in [200, 201]:
        print("Tileset created/updated successfully!")
        return response.json()
    else:
        print(f"Error creating/updating tileset: {response.text}")
        response.raise_for_status()

# --- Publish a tileset ---
def publish_tileset(tileset_id, access_token):
    print(f"Publishing tileset {tileset_id}...")
    
    # Trigger publication
    url = f'https://api.mapbox.com/tilesets/v1/{tileset_id}/publish?access_token={access_token}'
    response = requests.post(url)
    
    if response.status_code == 200:
        print("Publication started successfully!")
        return response.json()
    else:
        print(f"Error publishing tileset: {response.text}")
        response.raise_for_status()

# --- Check the processing status of a tileset ---
def check_processing_status(tileset_id, access_token):
    url = f'https://api.mapbox.com/tilesets/v1/{tileset_id}/status?access_token={access_token}'
    
    while True:
        response = requests.get(url)
        if response.status_code == 200:
            status = response.json()
            if status.get('status') == 'processing':
                print("Still processing... waiting 10 seconds")
                sleep(10)
            elif status.get('status') == 'success':
                print("Processing completed successfully!")
                return True
            else:
                print(f"Processing failed or unknown status: {status}")
                return False
        else:
            print(f"Error checking status: {response.text}")
            return False

# --- Main process ---
def main():
    # ArcGIS FeatureServer details
    arcgis_url = "https://services3.arcgis.com/MV5wh5WkCMqlwISp/ArcGIS/rest/services/SPC_Sidewalks/FeatureServer/0/query"
    params = {
        "where": "1=1",
        "outFields": "*",
        "f": "geojson"
    }

    # Filepaths and IDs
    ldjson_filepath = "sidewalks.ldgeojson"
    username = "cjaros61"
    source_id = "sidewalks-source"
    tileset_id = f"{username}.sidewalks-vector"

    # Get Mapbox access token
    access_token = os.environ.get("MAPBOX_ACCESS_TOKEN")
    if not access_token:
        print("Error: MAPBOX_ACCESS_TOKEN environment variable not set.")
        return

    try:
        # 1. Download the data
        geojson_data = download_arcgis_geojson(arcgis_url, params)

        # 2. Convert to line-delimited GeoJSON file
        convert_to_ldjson(geojson_data, ldjson_filepath)

        # 3. Create/update the tileset source
        create_or_update_source(username, source_id, ldjson_filepath, access_token)

        # 4. Create/update the tileset with recipe
        create_or_update_tileset(username, tileset_id, source_id, access_token)

        # 5. Publish the tileset
        publish_tileset(tileset_id, access_token)

        # 6. Monitor the processing status
        if check_processing_status(tileset_id, access_token):
            print("\nSuccess! Your tileset has been created and published.")
            print(f"You can now add the tileset '{tileset_id}' to your Mapbox Studio style.")
            print(f"Style URL format: mapbox://styles/{username}/your-style-id")
        else:
            print("\nThere was an issue processing your tileset. Please check the Mapbox Studio interface for more details.")

    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    main()
