import json

infile  = r"C:\Users\fengy\OneDrive\Desktop\25SUMMER\SPC\Slope_Map\Sidewalks.geojson"
outfile = r"C:\Users\fengy\OneDrive\Desktop\25SUMMER\SPC\Slope_Map\transportation.geojson"

with open(infile, 'r', encoding='utf-8') as f:
    data = json.load(f)

clean = {
    "type": "FeatureCollection",
    "$schema": "https://sidewalks.washington.edu/opensidewalks/0.2/schema.json",
    "features": []
}

for feat in data.get("features", []):
    props = feat.get("properties", {})
    geom  = feat.get("geometry", {})

    newp = {}
    eid = props.get("GlobalID") or props.get("OBJECTID")
    newp["_id"] = str(eid)

    # Safely handle None for Grade → incline
    grade = props.get("Grade")
    newp["incline"] = grade / 100.0 if grade is not None else None

    newp["width"] = props.get("Width")

    # THE FIXED LINE: coalesce None → empty string before stripping
    mat = (props.get("Material") or "").strip()
    newp["surface"] = mat.lower() if mat else "unknown"

    # Strip Z values from coordinates
    coords2d = [[lon, lat] for lon, lat, *_ in geom.get("coordinates", [])]
    newgeom = {"type": "LineString", "coordinates": coords2d}

    clean["features"].append({
        "type": "Feature",
        "properties": newp,
        "geometry": newgeom
    })

with open(outfile, 'w', encoding='utf-8') as f:
    json.dump(clean, f, ensure_ascii=False, indent=2)
