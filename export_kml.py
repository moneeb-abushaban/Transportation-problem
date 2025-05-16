import pandas as pd
from simplekml import Kml

df = pd.read_csv("all_routes.csv")
kml = Kml()

for bus_number, group in df.groupby("bus_number"):
    coords = list(zip(group["longitude"], group["latitude"]))
    line = kml.newlinestring(name=f"Bus {bus_number}")
    line.coords = coords
    line.style.linestyle.width = 4
    line.style.linestyle.color = "ff0000ff"  # red

kml.save("all_routes.kml")
print("✅ KML saved as: all_routes.kml")
