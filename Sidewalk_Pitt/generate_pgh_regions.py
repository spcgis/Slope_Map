#!/usr/bin/env python3
"""
generate_pgh_regions.py

Fetches the Pittsburgh boundary via OSMnx and writes
accessmap/data/regions.geojson in the format AccessMap expects.
"""

import os
import json
import osmnx as ox
import geopandas as gpd

# 1. Fetch the Pittsburgh administrative boundary
#    (you can adjust the geocode string if you need a different area)
place_name = "Pittsburgh, Pennsylvania, USA"
print(f"Fetching boundary for {place_name}…")
gdf = ox.geocode_to_gdf(place_name)

if gdf.empty:
    raise RuntimeError(f"No boundary found for '{place_name}'")

# 2. Build the AccessMap regions feature collection
#    We assume only one feature for this place; if there are multiples,
#    you can loop over gdf.itertuples() similarly.
bounds = list(gdf.total_bounds)  # [west, south, east, north]

features = []
for _, row in gdf.iterrows():
    geom = row.geometry.__geo_interface__
    # Use a stable key; here "pa.pittsburgh"
    props = {
        "key": "pa.pittsburgh",
        "name": "Pittsburgh",
        "bounds": bounds,
        # Center the initial map view on the first coordinate of the polygon
        "lon": geom["coordinates"][0][0][0],
        "lat": geom["coordinates"][0][0][1],
        "zoom": 11
    }
    features.append({
        "type": "Feature",
        "properties": props,
        "geometry": geom
    })

regions = {
    "type": "FeatureCollection",
    "features": features
}

# 3. Write out to accessmap/data/regions.geojson
out_dir = r"C:\Users\fengy\OneDrive\Desktop\25SUMMER\SPC\Slope_Map"
if not out_dir:
    out_dir = os.path.join(os.getcwd(), "accessmap", "data")

os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "regions.geojson")

print(f"Writing AccessMap regions to {out_path}…")
with open(out_path, "w", encoding="utf-8") as f:
    json.dump(regions, f, ensure_ascii=False, indent=2)

print("Done.")
