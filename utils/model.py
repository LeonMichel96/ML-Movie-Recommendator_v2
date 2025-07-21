import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors

# Modelo PCA
def pca(df):
    pca_final = PCA(n_components=20)
    X = df.drop(columns=['title_id', 'type', 'title'])
    pca_final.fit(X)

    X_projected_final = pca_final.transform(X)
    X_projected_final = pd.DataFrame(X_projected_final, columns=[f'PC{i}' for i in range(1,21)])

    identificator_df = df[['title', 'type']]
    final_df = identificator_df.merge(X_projected_final, how='left',left_index=True, right_index=True)

    return final_df

# Modelo KNN
def KNN(x_projected, selected_df):
    knn = NearestNeighbors(n_neighbors=11)
    knn.fit(x_projected.drop(columns=['title', 'type']))
    nearest_indexes = knn.kneighbors(selected_df.drop(columns=['title', 'type']), return_distance=False)

    expanded_indexes = []
    for neighbor in nearest_indexes:
        for index_num in neighbor:
            expanded_indexes.append(index_num)
    return expanded_indexes

# Modelo KMeans
def kmeans(df):
    km = KMeans(n_clusters=3)
    km.fit(df.drop(columns=['title', 'type', 'original_index']))

    labels = pd.DataFrame(km.labels_, columns=['cluster'])
    km_df = pd.merge(df, labels, left_index=True, right_index=True, how='left')
    return km_df
