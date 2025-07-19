import streamlit as st
import pandas as pd
from utils.connect_db import return_df, connect_to_db, load_sql_query
from utils.prepro import prepare_df
from utils.model import pca

### Cargar Datos
connection = connect_to_db()
base_query = load_sql_query(sub_folder='sql_queries', file_name='base_query.sql')
base_df = return_df(base_query,connection)

### Aplicar preprocesamiento
prepro_df = prepare_df(base_df)

### Aplicar PCA
pca_df = pca(prepro_df)

### Página
st.title('📹 Movie Recommendator')

st.dataframe(base_df)
st.dataframe(prepro_df)
st.dataframe(pca_df)

st.write(len(base_df) == len(pca_df))
