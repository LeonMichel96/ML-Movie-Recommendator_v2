import pandas as pd
import numpy as np
from sklearn.pipeline import make_pipeline, make_union, Pipeline
from sklearn.compose import make_column_transformer, make_column_selector, ColumnTransformer
from sklearn.preprocessing import StandardScaler, FunctionTransformer, OneHotEncoder

def prepare_df(df):

# categorical encoding + scaling
    cat_transformer = Pipeline([
        ('Encoder',OneHotEncoder(handle_unknown='ignore',sparse_output=False)),
        ('Scaler', StandardScaler())
        ])

# numerical scalling
    num_transformer = Pipeline([('Scaler',StandardScaler())])

    num_columns = ['isadult', 'startyear', 'runtimeminutes', 'averagerating', 'numvotes']
    cat_columns = ['genre_name']

    preprocessor = ColumnTransformer([
    ('cat_transformer', cat_transformer, cat_columns),
    ('num_transformer',num_transformer, num_columns)],
    remainder='passthrough'
    )

    df_transformed = preprocessor.fit_transform(df)
    df_transformed = pd.DataFrame(df_transformed, columns=preprocessor.get_feature_names_out())

    df_transformed.rename(columns={
    'remainder__title_id': 'title_id',
    'remainder__titletype': 'type',
    'remainder__primarytitle':'title'
    }, inplace=True)

    return df_transformed
