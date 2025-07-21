import streamlit as st
import pandas as pd
from utils.connect_db import return_df, connect_to_db, load_sql_query
from utils.prepro import prepare_df
from utils.model import pca, KNN, kmeans

### Funciones
# Función selección cluster
def cluster_selection(n, final_df, base_df):
    mix_df = final_df[final_df['cluster']==n]
    mix_df = mix_df[['title', 'original_index']].merge(base_df[['startyear', 'averagerating']],
                                                            left_on='original_index', right_index=True, how='left')
    mix_df.drop(columns=['original_index'], inplace=True)
    return mix_df

### Cargar Datos
connection = connect_to_db()
base_query = load_sql_query(sub_folder='sql_queries', file_name='base_query.sql')
base_df = return_df(base_query,connection)

## Preparación base_df
base_df['title_year'] = base_df['primarytitle'] + '_' + base_df['startyear'].astype(str)
base_df['title_year'] = base_df['title_year'].str.lower()

### Aplicar preprocesamiento
prepro_df = prepare_df(base_df.drop(columns=['title_year']))

### Aplicar PCA
pca_df = pca(prepro_df)

### Página
st.title('📹 Movie Recommendator')
st.info("""**Sistema de recomendación:**

- Por cada película seleccionada se recomendarán otras 10
- Las 55 películas finales serán divididas en tres distintos clusters
""")



## Selección de películas
st.subheader('Selecciona 5 Peliculas')

with st.form('Selección de películas'):
    movie_1 = st.selectbox('Selecciona una película', options=base_df['title_year'], key='1')
    movie_2 = st.selectbox('Selecciona una película', options=base_df['title_year'], key='2')
    movie_3 = st.selectbox('Selecciona una película', options=base_df['title_year'], key='3')
    movie_4 = st.selectbox('Selecciona una película', options=base_df['title_year'], key='4')
    movie_5 = st.selectbox('Selecciona una película', options=base_df['title_year'], key='5')

    submitted = st.form_submit_button("Submit")
if submitted:

# Identificar películas seleccionadas
    selected_indexes = base_df[base_df['title_year'].isin([movie_1, movie_2, movie_3, movie_4, movie_5])]
    selected_indexes = selected_indexes.index
    selection_df = pca_df.loc[selected_indexes]

# Aplicar KNN para encontrar 10 películas cercanas por selección
    recommendator_indexes = KNN(pca_df,selection_df)
    recommendator_df = pca_df.loc[recommendator_indexes].reset_index().rename(columns={'index':'original_index'})

# Aplicar KMeans para realizar clusters de recomendaciones
    final_df = kmeans(recommendator_df)

## Visualización de resultados
    st.subheader('Primer Mix de Películas 🔮')
    first_mix = cluster_selection(0,final_df, base_df)
    st.dataframe(first_mix)

    st.subheader('Segundo Mix de Películas 🍿')
    secodn_mix = cluster_selection(1,final_df, base_df)
    st.dataframe(secodn_mix)

    st.subheader('Tercer Mix de Películas 📼')
    third_mix = cluster_selection(2,final_df, base_df)
    st.dataframe(third_mix)
