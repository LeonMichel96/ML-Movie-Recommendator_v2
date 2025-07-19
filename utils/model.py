import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans
from sklearn.neighbors import NearestNeighbors

def pca(df):

# instanciar pca con 20 pc´s
    pca_final = PCA(n_components=20)
    X = df.drop(columns=['title_id', 'type', 'title'])
    pca_final.fit(X)

    X_projected_final = pca_final.transform(X)
    X_projected_final = pd.DataFrame(X_projected_final, columns=[f'PC{i}' for i in range(1,21)])

    identificator_df = df[['title', 'type']]
    final_df = identificator_df.merge(X_projected_final, how='left',left_index=True, right_index=True)

    return final_df
