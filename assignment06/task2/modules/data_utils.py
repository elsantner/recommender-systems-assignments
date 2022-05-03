import os
from pathlib import Path
import pandas as pd

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

RATING_SAMPLE_SIZE = 1000

POSTER_PREFIX = 'https://image.tmdb.org/t/p/w500'


# creates a comma-separated string from a list of dicts
def format_list(str_list):
    str_list = eval(str_list)
    listStr = ""
    for item in str_list:
        listStr = listStr + ', ' + item

    # remove first ', '
    return listStr[2:]


def get_full_poster_url(path):
    return POSTER_PREFIX + path


def read_ratings():
    # read the ratings file into a dataframe
    return pd.read_csv(os.path.join(BASE_DIR, 'modules', 'datasets', 'ratings_small.csv'),
                       sep=',', engine='python', nrows=RATING_SAMPLE_SIZE)


def get_movies_metadata(recommended_movies_list):
    # read the metadata of the movies and the credits files from the datasets
    metadataMovies = pd.read_csv(os.path.join(BASE_DIR, 'modules', 'datasets', 'movies_tmdbMeta.csv'), sep=',',
                                 engine='python', quotechar='"')

    # create a dataframe from the list of recommended movies
    df = pd.DataFrame(recommended_movies_list, columns=['movieId', 'mean_rating'])

    # change id to movie_id for easier joining
    metadataMovies.rename(columns={'id': 'movieId'}, inplace=True)

    # join the recommended movies with their metadata
    joined_df = df.join(metadataMovies, on='movieId', how='left', lsuffix='_left', rsuffix='_right')
    joined_df.rename(columns={'movieId_left': 'movieId'}, inplace=True)

    # cast and genres are lists, therefore we convert them to a comma-separated string
    joined_df['genres'] = joined_df['genres'].apply(format_list)
    joined_df['cast'] = joined_df['cast'].apply(format_list)
    joined_df['poster_path'] = joined_df['poster_path'].apply(get_full_poster_url)

    # return the dataframe
    return joined_df[["poster_path", "title", "genres", "mean_rating", "overview", "cast"]]
