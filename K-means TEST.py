import json

import pandas as pd
import requests
from haversine import haversine, Unit
from sklearn.cluster import KMeans

# Reading Data as csv
data_frame = pd.read_csv("ADRESS_INFORMATION.csv")

# Factory coordinates
factory_coordinates = (39.976745, 32.562880)

# Walking speed (km/h)
waking_speed_kmph = 5


# Function to determine if an address is in Ankara
def is_in_ankara(result) -> bool:
    is_ankara = False
    is_tr = False
    for component in result["address_components"]:
        if component["short_name"] == "Ankara":
            is_ankara = True
        if component["short_name"] == "TR":
            is_tr = True
    return is_ankara and is_tr


# Function to get location
def get_location(results, id_number):
    for result_row in results["results"]:
        if is_in_ankara(result_row):
            return result_row["geometry"]["location"]
    raise ValueError("No location in Ankara found for id " + str(id_number))


# Load filtered data and calculate distances
locations = []

for index, row in data_frame[data_frame['City'] == 'Ankara'].iterrows():
    address = str(row["AddressOne"]) + " + " + str(row["AddressTwo"]) + " + " + str(
        row["AddressThree"] or "") + " + " + str(row["City"])
    parameters = {
        "key": "AIzaSyAHXJOwND71ht5U5P2TXJzIDHW2WLkosfg",
        "address": address
    }
    response = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params=parameters)
    data = json.loads(response.text)
    try:
        location = get_location(data, row['id'])
        locations.append([row['id'], location["lat"], location["lng"]])
    except ValueError as e:
        print(str(e))

# Convert locations to DataFrame
locations_df = pd.DataFrame(locations, columns=["id", "latitude", "longitude"])

# Apply K-Means clustering
coordinates = locations_df[["latitude", "longitude"]].values
kmeans = KMeans(n_clusters=1, random_state=0).fit(coordinates)
collecting_point = kmeans.cluster_centers_[0]


# Calculate distances and times
def calculate_walking_distance(employee_coords, collecting_point):
    return haversine(employee_coords, collecting_point, unit=Unit.KILOMETERS)


def calculate_walking_time(distance_km):
    return (distance_km / 5) * 60


def get_driving_time(collecting_point, factory_coords):
    params = {
        "origins": f"{collecting_point[0]},{collecting_point[1]}",
        "destinations": f"{factory_coords[0]},{factory_coords[1]}",
        "key": "AIzaSyAHXJOwND71ht5U5P2TXJzIDHW2WLkosfg"
    }
    response = requests.get("https://maps.googleapis.com/maps/api/distancematrix/json", params=params)
    result = response.json()
    return result["rows"][0]["elements"][0]["duration"]["value"] / 60  # Convert seconds to minutes


# Filter employees within constraints
employees_within_time_limit = []
for index, row in locations_df.iterrows():
    employee_coords = (row["latitude"], row["longitude"])
    walking_distance = calculate_walking_distance(employee_coords, collecting_point)
    if walking_distance <= 0.75:  # 750 meters
        walking_time = calculate_walking_time(walking_distance)
        driving_time = get_driving_time(collecting_point, factory_coordinates)
        total_time = walking_time + driving_time
        if total_time <= 90:  # 90 minutes
            employees_within_time_limit.append(row)

# Select top 45 employees by proximity
employees_within_time_limit = sorted(employees_within_time_limit,
                                     key=lambda x: calculate_walking_distance((x["latitude"], x["longitude"]),
                                                                              collecting_point))
final_employees = []

# Add the collecting point with a blank ID as the first row
final_employees.append(["COLLECTING POINT", collecting_point[0], collecting_point[1]])

# Add the employees' id, coordinates, and the collecting point coordinates
for row in employees_within_time_limit[:45]:
    employee_data = [row['id'], row['latitude'], row['longitude'], collecting_point[0], collecting_point[1]]
    final_employees.append(employee_data)

# Save the final employee list to CSV
final_df = pd.DataFrame(final_employees,
                        columns=["id", "latitude", "longitude", "collecting_point_lat", "collecting_point_lon"])
final_df.to_csv("final_employees_new1.csv", index=False)
