import math
import random

import pandas as pd
from geopy.distance import geodesic


def total_distance(route):
    return sum(
        geodesic(route[i], route[i + 1]).meters
        for i in range(len(route) - 1)
    )


def simulated_annealing_route(route, temp=10000, cooling_rate=0.995, min_temp=0.1):
    current = route[:]
    best = current[:]
    best_cost = total_distance(best)

    while temp > min_temp:
        if len(route) <= 3:
            break  # not enough points to optimize

        i, j = sorted(random.sample(range(1, len(route) - 1), 2))
        neighbor = current[:]
        neighbor[i:j] = reversed(neighbor[i:j])
        cost = total_distance(neighbor)
        delta = cost - best_cost
        if delta < 0 or math.exp(-delta / temp) > random.random():
            current = neighbor
            if cost < best_cost:
                best = neighbor
                best_cost = cost
        temp *= cooling_rate
    return best


def optimize_routes(input_csv, factory_coord, output_file='all_routes.csv'):
    df = pd.read_csv(input_csv)
    all_routes = []

    for bus_no in df['bus_number'].unique():
        bus_stops = df[df['bus_number'] == bus_no][['latitude', 'longitude']].values.tolist()

        if len(bus_stops) == 0:
            continue

        route = [factory_coord] + bus_stops + [factory_coord]

        if len(bus_stops) >= 2:
            route = simulated_annealing_route(route)

        for lat, lon in route:
            all_routes.append({'latitude': lat, 'longitude': lon, 'bus_number': bus_no})

    all_routes_df = pd.DataFrame(all_routes)
    all_routes_df.to_csv(output_file, index=False)
