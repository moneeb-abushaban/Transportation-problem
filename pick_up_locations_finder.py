import numpy as np
import pandas as pd
from geopy.distance import geodesic
from sklearn.cluster import AgglomerativeClustering


class PickUpLocationsFinder:
    @staticmethod
    def run(locations_all_csv, pickup_points_output='pickup_points_result.csv',
            labeled_output='employee_cluster_map.csv'):
        df = pd.read_csv(locations_all_csv)
        coords = df[['latitude', 'longitude']].values.astype(float)

        dist_matrix = compute_distance_matrix(coords)
        clustering = AgglomerativeClustering(
            n_clusters=None,
            distance_threshold=750,
            metric='precomputed',
            linkage='complete'
        ).fit(dist_matrix)

        df['cluster'] = clustering.labels_
        clusters = df['cluster'].unique()
        centers = np.array([
            coords[df['cluster'] == i].mean(axis=0)
            for i in clusters
        ])

        cluster_sizes = df['cluster'].value_counts().sort_index()
        pickup_df = pd.DataFrame({
            'pickup_point': range(len(centers)),
            'latitude': centers[:, 0],
            'longitude': centers[:, 1],
            'employee_count': [cluster_sizes.get(i, 0) for i in range(len(centers))]
        })

        pickup_df.to_csv(pickup_points_output, index=False)
        df.to_csv(labeled_output, index=False)
        return pickup_points_output, labeled_output


def compute_distance_matrix(coords):
    size = len(coords)
    matrix = np.zeros((size, size))
    for i in range(size):
        matrix[i] = [geodesic(coords[i], coords[j]).meters if i != j else 0 for j in range(size)]
    return matrix
