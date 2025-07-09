import os
import gzip
import pandas as pd
import numpy as np
import sqlite3
import psycopg2
from psycopg2 import sql, Error
from dotenv import load_dotenv
from sqlalchemy import create_engine


base_folder = os.getcwd()
data_sources = os.path.join(base_folder, 'data_sources')
raw_files = os.path.join(data_sources, 'raw_files')
extracted_files = os.path.join(data_sources, 'extracted_files')
print('variable folders done')

load_dotenv()
user = os.getenv('USER_D')
db_name = os.getenv('DATABASE')
host = os.getenv('HOST')
port = os.getenv('PORT')
password = os.getenv('PASSWORD')
print('variable env done')

### Extraction
files_zipped =['title.ratings.tsv.gz', 'title.basics.tsv.gz', 'title.crew.tsv.gz', 'name.basics.tsv.gz']

# first check if there is already data downloaded
files_in_folder = os.listdir(extracted_files)

if 'title.ratings.tsv' in files_in_folder and 'title.basics.tsv' in files_in_folder \
    and 'title.crew.tsv' in files_in_folder and 'name.basics.tsv' in files_in_folder:
    df_ratings = pd.read_csv(os.path.join(extracted_files, 'title.ratings.tsv'), sep= '\t')
    df_basics = pd.read_csv(os.path.join(extracted_files, 'title.basics.tsv'), sep= '\t')
    df_crew = pd.read_csv(os.path.join(extracted_files, 'title.crew.tsv'), sep= '\t')
    df_names = pd.read_csv(os.path.join(extracted_files, 'name.basics.tsv'), sep= '\t')

# ff the data has not been downloaded, perform extraction
else:
    for file in files_zipped:
        # Extract zipped content
        gzipped_file_path = os.path.join(base_folder, raw_files, file)

        with gzip.open(gzipped_file_path, 'rt') as gzipped_file:
        # Specify the path to the extracted TSV file (remove '.gz' extension)
            extracted_file_path = os.path.join(extracted_files, file[:-3])

        # Write the extracted content to the TSV file
            with open(extracted_file_path, 'w') as extracted_file:
                extracted_file.write(gzipped_file.read())

            if file == 'title.ratings.tsv.gz':
                df_ratings = pd.read_csv(extracted_file_path, sep='\t')
            elif file == 'title.crew.tsv.gz':
                df_crew = pd.read_csv(extracted_file_path, sep='\t')
            elif file == 'name.basics.tsv.gz':
                df_names = pd.read_csv(extracted_file_path, sep='\t')
            else:
                df_basics = pd.read_csv(extracted_file_path, sep='\t')


### Cleaning
## Titles DF

# consider only movies
df_basics = df_basics[df_basics['titleType']=='movie']

# drop Original Title and end year
df_basics.drop(columns=['originalTitle', 'endYear'], inplace= True)

# drop rows with Start year, run time minutes and genres null
df_basics = df_basics[df_basics['startYear']!="\\N"]
df_basics = df_basics[df_basics['runtimeMinutes']!="\\N"]
df_basics = df_basics[df_basics['genres']!="\\N"]

# convert startYear, runtimeMinutes  columns to integer
df_basics['startYear']=df_basics['startYear'].astype('int32')
df_basics['runtimeMinutes']=df_basics['runtimeMinutes'].astype('int32')

# consider just movies filmed between 1970 and 2022
df_basics= df_basics[(df_basics['startYear']>1970) & (df_basics['startYear']<2023)]

# change /N to NaN
df_basics.replace('\\N', np.nan, inplace=True)

# rename column
df_basics.rename(columns={'tconst': 'title_id'}, inplace=True)

# remove nulls in names
df_basics = df_basics[df_basics['primaryTitle'].notna()]

# linking tables (many to many relationships)
# create a DataFrame for the linking table (title_id, genre_name)
df_movie_genres_exploded = df_basics[['title_id', 'genres']].copy()
df_movie_genres_exploded['genres_list'] = df_movie_genres_exploded['genres'].apply(lambda x: x.split(','))
df_movie_genres_exploded = df_movie_genres_exploded.explode('genres_list')
df_movie_genres_exploded = df_movie_genres_exploded.rename(columns={'genres_list': 'genre_name'})
df_movie_genres_exploded = df_movie_genres_exploded[['title_id', 'genre_name']]
df_movie_genres_exploded['genre_name'] = df_movie_genres_exploded['genre_name'].str.strip()
df_movie_genres_exploded.reset_index(drop=True, inplace=True)

# create a DataFrame for unique genres (genre_id, genre_name)
unique_genres = df_movie_genres_exploded['genre_name'].unique()
df_genres_table = pd.DataFrame(unique_genres, columns=['genre_name'])

# drop genres from df_basics
df_basics.drop(columns=['genres'], inplace=True)

## Crew DF
# drop writers
df_crew.drop(columns=['writers'], inplace= True)

# change /N to NaN
df_crew.replace('\\N', np.nan, inplace=True)

# rename columns
df_crew.rename(columns={'directors': 'name_id',
                        'tconst': 'title_id'}, inplace=True)

# modify to get a df with titles duplicated for each director
df_crew['name_id'] = df_crew['name_id'].astype(str)
df_crew['name_id_list'] = df_crew['name_id'].apply(lambda x: x.split(','))
df_crew = df_crew.explode('name_id_list').drop(columns=['name_id'])
df_crew.rename(columns={'name_id_list': 'name_id'}, inplace=True)

# ensure director IDs are stripped of whitespace if any
df_crew['name_id'] = df_crew['name_id'].str.strip()

df_crew.reset_index(drop=True, inplace=True)

## Names DF
# rename column of directors for later merge
df_names = df_names.rename(columns={'nconst':'name_id'})
df_names.drop(columns=['deathYear', 'primaryProfession', 'knownForTitles'], inplace= True)

# change /N to NaN
df_names.replace('\\N', np.nan, inplace=True)

# drop null names
df_names = df_names[df_names['primaryName'].notna()]

## Ratings DF
# change /N to NaN
df_ratings.replace('\\N', np.nan, inplace=True)

# rename column
df_ratings.rename(columns={'tconst': 'title_id'}, inplace=True)

print('Cleaning done')

### Load Data
## Creation of SQL tables in supabase


conn = psycopg2.connect(
    dbname=db_name,
    user=user,
    password=password,
    host=host,
    port=port
)
cursor = conn.cursor()

print("connected to project database")

sql_schema_query = """
DROP TABLE IF EXISTS titles_genres;
DROP TABLE IF EXISTS ratings;
DROP TABLE IF EXISTS crew;
DROP TABLE IF EXISTS titles;
DROP TABLE IF EXISTS genres;
DROP TABLE IF EXISTS names;

CREATE TABLE names (
    name_id VARCHAR(50) NOT NULL,
    primaryName VARCHAR(256) NOT NULL,
    birthYear INT,
    PRIMARY KEY (name_id)
);

CREATE TABLE genres (
    genre_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (genre_name)
);

CREATE TABLE titles (
    title_id VARCHAR(50) NOT NULL,
    titleType VARCHAR(50) NOT NULL,
    primaryTitle VARCHAR(300) NOT NULL,
    isAdult INT,
    startYear INT,
    runtimeMinutes INT,
    PRIMARY KEY (title_id)
);

CREATE TABLE crew (
    title_id VARCHAR(50) NOT NULL,
    name_id VARCHAR(50) NOT NULL,
    PRIMARY KEY (title_id, name_id),
    FOREIGN KEY (title_id) REFERENCES titles (title_id),
    FOREIGN KEY (name_id) REFERENCES names (name_id)
);

CREATE TABLE ratings (
    title_id VARCHAR(50) NOT NULL,
    averageRating FLOAT NOT NULL,
    numVotes INT NOT NULL,
    PRIMARY KEY (title_id),
    FOREIGN KEY (title_id) REFERENCES titles (title_id)
);

CREATE TABLE titles_genres (
    title_id VARCHAR(50) NOT NULL,
    genre_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (title_id, genre_name),
    FOREIGN KEY (title_id) REFERENCES titles (title_id),
    FOREIGN KEY (genre_name) REFERENCES genres (genre_name)
);
"""

try:
    for stmt in sql_schema_query.strip().split(';'):
        if stmt.strip():
            cursor.execute(stmt)
    conn.commit()
    print("Tables created")
except psycopg2.Error as e:
    print(f"Error creating tables: {e}")
    conn.rollback()
finally:
    cursor.close()
    conn.close()
print('Connection closed')

## Data Insertion

engine = create_engine(f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}')

# Insertar data
df_names.to_sql('names', engine, if_exists='append', index=False)
df_genres_table.to_sql('genres', engine, if_exists='append', index=False)
df_basics.to_sql('titles', engine, if_exists='append', index=False)
df_crew.to_sql('crew', engine, if_exists='append', index=False)
df_movie_genres_exploded.to_sql('titles_genres', engine, if_exists='append', index=False)
df_ratings.to_sql('ratings', engine, if_exists='append', index=False)

print("Inserions completed successfully")
