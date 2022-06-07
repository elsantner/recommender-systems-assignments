# Data interface for 'MovieLens1M' data set
import pandas as pd

movie_columns = ['id', 'title', 'genres', 'overview', 'popularity', 'original_language', 'production_countries',
                 'release_date', 'runtime', 'cast', 'director', 'keywords']


# parse a string representation to a python list object
def parse_list(str_list):
    return eval(str_list)


def read_dat_file(path, cols=None):
    try:
        if cols is None:
            return pd.read_csv(path, sep=',', quotechar='"', engine='python', encoding='utf8')
        else:
            return pd.read_csv(path, sep=',', quotechar='"', engine='python', encoding='utf8',
                               skipinitialspace=True, usecols=cols)
    except:
        raise Exception('unable to read file "{0}"'.format(path))


class MovieData:

    # load data on creation
    def __init__(self, path='./resources'):
        self.path = path
        self.movies_df = self.__read_movies_df()
        self.ratings_df = self.__read_ratings_df()

    def __read_movies_df(self):
        df = read_dat_file(self.path + "/movies_tmdbMeta.csv", cols=movie_columns)

        df['genres'] = df['genres'].apply(parse_list)
        df['cast'] = df['cast'].apply(parse_list)
        df['production_countries'] = df['production_countries'].apply(parse_list)
        df.loc['release_date'] = pd.to_datetime(df['release_date'], errors='coerce')
        # x == x ... NaN check
        df['release_year'] = df['release_date'].apply(
            lambda x: int(str(x).split('-')[0]) if x == x else 0)
        df['release_year'] = df['release_year'].astype('int')
        df['overview'] = df['overview'].fillna('')
        return df

    def __read_ratings_df(self):
        return read_dat_file(self.path + "/ratings_small.csv")

    # get movie metadata
    def get_movie_metadata(self, movie_ids_df):
        return pd.merge(movie_ids_df, self.movies_df, on='id', how='inner')

    def get_movie_metadata_single(self, movie_id):
        return self.movies_df.loc[self.movies_df['id'] == movie_id]

    def get_movie_count(self):
        return self.movies_df.size

    def movie_exists(self, movie_id):
        return movie_id in self.movies_df['id']
