# Task 3) Analyzing a movie dataset

import pandas as pd
import numpy as np

# function to convert to float
def to_float(x):
    try:
        x = float(x)
    except:
        x = np.nan
    return x


df = pd.read_csv('./resources/movies_dataset/movies_metadata.csv')
# uncomment to print all columns
# pd.set_option('display.max_columns', None)
print(type(df))

print('\nfirst movie:\n' + df.head(1).to_string())
print('\nlast movie:\n' + df.tail(1).to_string())

print('\nJumanji:\n', df.loc[df['original_title'] == 'Jumanji'])


# create sub-df for specified columns (as a copy)
# notice double '[]'
small_df = df[['title', 'release_date', 'popularity', 'revenue', 'runtime', 'genres']].copy()
# convert release_date to DateTime and update in df
# errors='coerce' ... if parse error then set result to NaN
small_df.loc['release_date'] = pd.to_datetime(small_df['release_date'], errors='coerce')
# introduce new column release_year
# parse release_date to extract release_year value via lambda function
# take yyyy of yyyy-mm-dd if not NaN, or else set to NaN
# lambda syntax:
#    lambda <arguments> : <return value if condition == True> if <condition> else <return value if condition == False>
small_df['release_year'] = small_df['release_date'].apply(lambda x: str(x).split('-')[0] if x != np.nan else np.nan)
# apply previously defined function to convert release_year to type float
small_df['release_year'] = small_df['release_year'].apply(to_float)
# explicitly set type to float
small_df['release_year'] = small_df['release_year'].astype('float')
# remove original column release_date from df
small_df = small_df.drop(columns="release_date")

print(small_df.loc[small_df['release_year'] == float(2010)]['title'].to_string())
