import math

import pandas as pd
from k_means_constrained import KMeansConstrained


def calculate_clusters(coords_repeated, n_clusters=None):
    if n_clusters is None:
        avg_capacity = (45 + 27 + 18) / 3
        n_clusters = math.ceil(len(coords_repeated) / avg_capacity)
    clf = KMeansConstrained(n_clusters=n_clusters, size_max=45, random_state=0)
    clf.fit_predict(coords_repeated)
    return clf


class BusCollectionPointsWithBusNumberFounder:
    @staticmethod
    def run(bus_collection_points_csv, output_csv='bus_points_with_bus_numbers.csv',
            bus_stats_output='bus_employee_counts.csv'):
        df = pd.read_csv(bus_collection_points_csv)
        rows = df[['latitude', 'longitude', 'employee_count', 'pickup_point']].values
        repeated = [row for row in rows for _ in range(int(row[2]))]

        clf = calculate_clusters(repeated)
        clustered_df = pd.DataFrame(repeated, columns=['latitude', 'longitude', 'employee_count', 'pickup_point'])
        clustered_df['bus_number'] = clf.labels_

        result_df = clustered_df.groupby('pickup_point').min().reset_index()
        bus_stats = result_df.groupby('bus_number')['employee_count'].sum().reset_index()

        result_df.to_csv(output_csv, index=False)
        bus_stats.to_csv(bus_stats_output, index=False)
        return output_csv
