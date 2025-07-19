import streamlit as st
import pandas as pd
from utils.connect_db import return_df, connect_to_db, load_sql_query

### Cargar Datos
connection = connect_to_db()
base_query = load_sql_query(sub_folder='sql_queries', file_name='base_query.sql')
base_df = return_df(base_query,connection)

### Página
st.title('📹 Movie Recommendator')

st.dataframe(base_df)
