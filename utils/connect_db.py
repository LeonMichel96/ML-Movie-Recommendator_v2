import pandas as pd
import numpy as np
import psycopg2
import os
from dotenv import load_dotenv
import streamlit as st


def connect_to_db():
    dotenv_path = os.path.join(os.getcwd(), '.env')
    load_dotenv(dotenv_path)

    port = os.environ.get('PORT')
    user = os.environ.get('USER_D')
    db = os.environ.get('DATABASE')
    password = os.environ.get('PASSWORD')
    host = os.environ.get('HOST')


    connection = psycopg2.connect(
    host= host,
    dbname = db,
    user = user,
    password = password,
    port = port)

    return connection

def run_query(query,_connection):
    cursor = _connection.cursor()
    cursor.execute(query)
    data = cursor.fetchall()
    columns = [desc[0] for desc in cursor.description]
    cursor.close()
    df = pd.DataFrame(data, columns=columns)
    return df

@st.cache_data
def return_df(query, _connection):
    df = run_query(query, _connection)
    return df

def load_sql_query(file_name, sub_folder):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    sql_path = os.path.abspath(os.path.join(script_dir, '..', sub_folder,file_name))
    with open(sql_path, 'r', encoding='utf-8') as file:
        return file.read()
