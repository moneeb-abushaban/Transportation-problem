import time

import openrouteservice
import pandas as pd
from simplekml import Kml

API_KEY = "WRITE YOUR OWN OPENROUTESERVICE CODE HERE"
FACTORY_COORD = (32.562732, 39.976736)  # Note: (lon, lat)

client = openrouteservice.Client(key=API_KEY)

# Load pickup points with assigned bus numbers
df = pd.read_csv("bus_points_with_bus_numbers.csv")

# Group by bus number
grouped = df.groupby("bus_number")

kml = Kml()

# Add factory point
factory_point = kml.newpoint(name="Factory", coords=[FACTORY_COORD])
factory_point.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/star.png"
factory_point.style.iconstyle.color = "ff000000"  # Black
factory_point.style.iconstyle.scale = 1.5

colors = ["ff0000ff", "ff00ff00", "ffff0000", "ffffff00", "ff00ffff", "ffff00ff", "ffff9900"]


def call_directions_with_backoff(coordinates, max_retries=5):
    wait_time = 2
    for attempt in range(max_retries):
        try:
            return client.directions(
                coordinates=coordinates,
                profile='driving-car',
                format='geojson',
                radiuses=[750] * len(coordinates)
            )
        except openrouteservice.exceptions.ApiError as e:
            if 'Rate limit exceeded' in str(e):
                print(f"Rate limit hit. Waiting {wait_time}s before retrying...")
                time.sleep(wait_time)
                wait_time *= 2  # exponential backoff
            else:
                raise
    raise Exception("Max retries exceeded for directions API call")


for i, (bus_number, group) in enumerate(grouped):
    if i > 0 and i % 10 == 0:
        print("⏳ Pausing 30s to avoid ORS rate limit...")
        time.sleep(30)
    coords = [(float(row["longitude"]), float(row["latitude"])) for _, row in group.iterrows()]

    # Remove duplicates and reorder
    coords = list(dict.fromkeys(coords))

    # Ensure route starts and ends at factory
    if coords[0] != FACTORY_COORD:
        coords.insert(0, FACTORY_COORD)
    if coords[-1] != FACTORY_COORD:
        coords.append(FACTORY_COORD)

    # Remove duplicates again after adding factory
    coords = list(dict.fromkeys(coords))

    try:
        route = call_directions_with_backoff(coords)
    except openrouteservice.exceptions.ApiError as e:
        print(f"Initial routing failed for bus {bus_number}: {e}")
        cleaned_coords = []
        for coord in coords:
            lon, lat = float(coord[0]), float(coord[1])
            try:
                client.directions(
                    coordinates=[(lon, lat), (lon, lat)],
                    profile='driving-car',
                    format='geojson',
                    radiuses=[750, 750]
                )
                cleaned_coords.append((lon, lat))
            except:
                print(f"  ⚠️ Skipping unroutable point: ({lon}, {lat})")

        if FACTORY_COORD not in cleaned_coords:
            cleaned_coords.insert(0, FACTORY_COORD)
            cleaned_coords.append(FACTORY_COORD)

        if len(cleaned_coords) < 2:
            print(f"  ❌ Not enough valid points for bus {bus_number}, skipping route.")
            continue

        try:
            route = call_directions_with_backoff(cleaned_coords)
        except Exception as final_error:
            print(f"  ❌ Final failure on bus {bus_number}: {final_error}")
            continue

    line = kml.newlinestring(name=f"Bus {bus_number}")
    line.coords = [(pt[0], pt[1]) for pt in route['features'][0]['geometry']['coordinates']]
    line.style.linestyle.width = 4
    line.style.linestyle.color = colors[bus_number % len(colors)]

    # Add pickup points for this bus
    for _, row in group.iterrows():
        point = kml.newpoint(name=f"Pickup {int(row['pickup_point'])}", coords=[(row["longitude"], row["latitude"])])
        point.style.iconstyle.color = "ff0000ff"  # Red
        point.style.iconstyle.scale = 1

    time.sleep(3)  # Global delay to avoid hitting ORS hard rate limits

# Save KML with drivable routes
kml.save("full_transport_plan_drivable.kml")
print("✅ Saved: full_transport_plan_drivable.kml")
