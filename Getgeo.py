import csv
import json

import pandas as pd
import requests

# Reading Data as csv
df = pd.read_csv("Employees.csv")
# print(df.head())
with open('locations.csv', 'w', newline='') as csvfile:
    spamwriter = csv.writer(csvfile, delimiter=' ',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
    spamwriter.writerow(["id,lat,lng"])
    for index, row in df.iterrows():
        print(index)
        address = str(row["AddressThree"]) + " city:" + str(row["City"]) + " " + str(row["AddressOne"]) + " " + str(
            row["AddressTwo"])
        print(address)
        parameters = {
            "key": "AIzaSyAHXJOwND71ht5U5P2TXJzIDHW2WLkosfg",
            "address": address
        }
        response = requests.get("https://maps.googleapis.com/maps/api/geocode/json", params=parameters)
        data = json.loads(response.text)
        print(json.dumps(data, indent=2))
        print("Location:")
        location = data["results"][0]["geometry"]["location"]
        print(location)
        spamwriter.writerow([str(row["id"]) + "," + str(location["lat"]) + "," + str(location["lng"])])

# Save data to csv with geo data
