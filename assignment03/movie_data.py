# Data interface for 'MovieLens1M' data set
import pandas as pd

user_col_names = ['UserID', 'Gender', 'Age', 'Occupation', 'Zip']
movies_col_names = ['MovieID', 'Title', 'Genres']
ratings_col_names = ['UserID', 'MovieID', 'Rating', 'Timestamp']


class MovieData:
    # load data on creation
    def __init__(self, path='./resources/ml-1m'):
        self.path = path
        self.user_df = self.__read_users_df()
        self.movies_df = self.__read_movies_df()
        self.ratings_df = self.__read_ratings_df()

    def __read_users_df(self):
        return self.__read_dat_file(self.path + "/users.dat", user_col_names)

    def __read_movies_df(self):
        return self.__read_dat_file(self.path + "/movies.dat", movies_col_names)

    def __read_ratings_df(self):
        return self.__read_dat_file(self.path + "/ratings.dat", ratings_col_names)

    # parse "CSV" file of MovieLens1M dataset
    def __read_dat_file(self, path, col_names):
        try:
            return pd.read_csv(path, sep='::', names=col_names, encoding='latin-1', engine='python')
        except:
            raise Exception('unable to read file "{0}"'.format(path))

    # get movies rated by user_id
    def get_rated_movies_df(self, user_id):
        # filter df by user_id
        filtered_df = self.ratings_df.loc[self.ratings_df['UserID'] == user_id]
        return pd.merge(filtered_df, self.movies_df, on='MovieID', how='inner')

    # get movie details (title, genres, etc.)
    def get_movie_details(self, movie_ids_df):
        return pd.merge(movie_ids_df, self.movies_df, on='MovieID', how='inner')

    def check_user_exists(self, user_id):
        return user_id in self.user_df['UserID']

    def get_movie_count(self):
        return self.movies_df.size

    def get_user_count(self):
        return self.user_df.size
