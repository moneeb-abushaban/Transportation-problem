import csv
import time

import pandas as pd
import requests
from geopy.distance import geodesic

GOOGLE_API_KEY = "ADD YOUR API KEY HERE"
GEOCODE_URL = "https://maps.googleapis.com/maps/api/geocode/json"
FACTORY_COORD = (39.976736, 32.562732)


def is_in_ankara(result) -> bool:
    city_found = country_found = False
    for component in result["address_components"]:
        if "Ankara" in component["long_name"]:
            city_found = True
        if component["short_name"] == "TR":
            country_found = True
    return city_found and country_found


def get_location(results, id_number):
    best_loc = None
    min_dist = float('inf')

    for result in results.get("results", []):
        if is_in_ankara(result):
            loc = result["geometry"]["location"]
            dist = geodesic(FACTORY_COORD, (loc["lat"], loc["lng"])).km
            if dist < min_dist:
                best_loc = loc
                min_dist = dist

    if best_loc and min_dist <= 50:  # Reduced from 60 to 50 km
        return best_loc
    else:
        raise ValueError(f"No valid location within 50km for ID {id_number}")


class AnkaraEmployeeLocationsFinder:
    @staticmethod
    def run(employee_address_information_csv, output_csv):
        df = pd.read_csv(employee_address_information_csv)
        df = df[df['City'].str.lower() == 'ankara']

        with open(output_csv, 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(["id", "latitude", "longitude"])

            # Add factory as a node with ID 'Factory'
            writer.writerow(["Factory", FACTORY_COORD[0], FACTORY_COORD[1]])

            for _, row in df.iterrows():
                address = f"{row['AddressOne']}, {row['AddressTwo']}, {row['AddressThree']}, {row['City']}"
                params = {"key": GOOGLE_API_KEY, "address": address}

                for attempt in range(3):
                    response = requests.get(GEOCODE_URL, params=params)
                    data = response.json()
                    try:
                        location = get_location(data, row["id"])
                        writer.writerow([row["id"], location["lat"], location["lng"]])
                        break
                    except ValueError as e:
                        if attempt < 2:
                            time.sleep(2 ** attempt)
                        else:
                            print(f"Skipping ID {row['id']}: {e}")
                            with open('skipped_addresses.csv', 'a', newline='') as skipped:
                                log_writer = csv.writer(skipped)
                                log_writer.writerow([row['id'], row['AddressOne'], row['City']])

        return output_csv


if __name__ == '__main__':
    AnkaraEmployeeLocationsFinder.run(
        employee_address_information_csv='ADRESS_INFORMATION.csv',
        output_csv='locations_all.csv'
    )
