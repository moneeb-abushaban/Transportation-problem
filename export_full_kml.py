import random

import pandas as pd
from simplekml import Kml


def get_color_for_bus(bus_no):
    random.seed(bus_no)
    colors = ["ff0000ff", "ff00ff00", "ffff0000", "ffffff00", "ff00ffff", "ffff00ff", "ffff9900"]
    return colors[bus_no % len(colors)]


def export_kml(factory_coord=(39.976736, 32.562732)):
    kml = Kml()

    # 1. Routes
    df_routes = pd.read_csv("all_routes.csv")
    for bus_no, group in df_routes.groupby("bus_number"):
        coords = [(lon, lat) for lat, lon in zip(group["longitude"], group["latitude"])]
        line = kml.newlinestring(name=f"Bus {bus_no}")
        line.coords = coords
        line.style.linestyle.width = 4
        line.style.linestyle.color = get_color_for_bus(bus_no)

    # 2. Pickup points
    df_pickups = pd.read_csv("pickup_points_result.csv")
    for _, row in df_pickups.iterrows():
        point = kml.newpoint(name=f"Pickup {int(row['pickup_point'])}",
                             coords=[(row["longitude"], row["latitude"])])
        point.style.iconstyle.color = "ff0000ff"
        point.style.iconstyle.scale = 1

    # 3. Employee homes + factory
    df_homes = pd.read_csv("locations_all.csv")
    for idx, row in df_homes.iterrows():
        if str(row["id"]).lower() == "factory":
            point = kml.newpoint(name="Factory", coords=[(row["longitude"], row["latitude"])])
            point.style.iconstyle.icon.href = "http://maps.google.com/mapfiles/kml/shapes/star.png"
            point.style.iconstyle.color = "ff000000"  # Black
            point.style.iconstyle.scale = 1.5
        else:
            point = kml.newpoint(name=f"Home {idx}", coords=[(row["longitude"], row["latitude"])])
            point.style.iconstyle.color = "ff999999"  # Gray
            point.style.iconstyle.scale = 0.5

    kml.save("full_transport_plan.kml")
    print("✅ KML saved as full_transport_plan.kml")


export_kml()
