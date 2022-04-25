# Collaborative recommender implementation
import pandas as pd

import movie_data


class ContentBasedRecommender:
    __RATING_LIKE_THRESHOLD = 4

    def __init__(self, data=movie_data.MovieData(), sample_size=-1):
        self.user_profiles = {}
        self.data = data
        self.sample_size = sample_size
        # create table for fast movie popularity lookup
        self.movie_popularity_dict = self.__create_movie_popularity_dict()

        # sample random user and movie IDs to reduce computation time
        # the pivot table still contains all data entries, just the ids used in the recommendation process are sampled

        if self.sample_size == -1:
            # no sampling required
            self.__sample_movie_df = self.data.movies_df
        else:
            self.__sample_movie_df = self.data.movies_df.sample(self.sample_size)

    def __create_movie_popularity_dict(self):
        return self.data.ratings_df.groupby(['MovieID']).size().to_dict()

    def __get_popularity(self, movie_id):
        try:
            return self.movie_popularity_dict[movie_id]
        # if movie not in dict then it was never rated --> popularity 0
        except KeyError:
            return 0

    # get genre count of all liked movies (rating > 3)
    def get_user_profile(self, user_id):
        # if user_profile is already cached
        if user_id in self.user_profiles:
            return self.user_profiles[user_id]
        else:
            user_profile = {}
            # get liked movies (rating > 3)
            df_liked_movies = self.data.get_rated_movies_df(user_id, self.__RATING_LIKE_THRESHOLD)

            # raise error if user has not rated any movie
            if df_liked_movies.empty:
                raise KeyError('no ratings for user {0} found'.format(user_id))

            # count genres of liked movies
            for _, row in df_liked_movies.iterrows():
                # genres are concatenated using '|'
                for genre in str(row['Genres']).split('|'):
                    if genre in user_profile:
                        user_profile[genre] += 1
                    else:
                        user_profile[genre] = 1

            # cache user profile for faster future calls
            self.user_profiles[user_id] = user_profile
            return user_profile

    def __get_user_rating_count(self, user_profile, genre):
        try:
            return user_profile[genre]
        except KeyError:
            return 0

    def __get_genre_set(self, data_entry):
        return set(str(data_entry['Genres']).split('|'))

    # calculate similarity by simple genre overlap
    def __calculate_overlap_similarity(self, movie_genres, user_profile):
        user_genres = set(user_profile.keys())
        intersect_set = movie_genres.intersection(user_genres)

        # which percentage of the liked genres does this movie have ?
        # (results in movies with many genres being preferred)
        #return len(intersect_set) / len(user_genres)

        # alternative: which percentage of this movie's genres has the user liked ?
        # (results in mostly 1.0 similarity scores)
        return len(intersect_set) / len(movie_genres)

    # recommendations based solely on genre overlap between movies and user profile (i.e. genres the user has liked)
    def get_recommendations_overlap(self, user_id):
        similarities = []

        for _, row in self.__sample_movie_df.iterrows():
            sim_overlap = self.__calculate_overlap_similarity(self.__get_genre_set(row), self.get_user_profile(user_id))
            similarities.append([row['MovieID'], sim_overlap])

        # rank by overlap percentage
        sorted_df = pd.DataFrame(similarities, columns=['MovieID', 'overlap']) \
            .sort_values(by='overlap', ascending=False)

        return self.data.get_movie_details(sorted_df)

    # recommendations based on overlap and movie popularity (i.e. rating count)
    def get_recommendations_popularity(self, user_id):
        similarities = []
        for _, row in self.__sample_movie_df.iterrows():
            # omit movies with no overlap
            sim_overlap = self.__calculate_overlap_similarity(self.__get_genre_set(row), self.get_user_profile(user_id))
            if sim_overlap != 0:
                similarities.append([row['MovieID'], self.__get_popularity(row['MovieID']), sim_overlap])

        sorted_df = pd.DataFrame(similarities, columns=['MovieID', 'popularity', 'overlap']) \
            .sort_values(by='popularity', ascending=False)

        return self.data.get_movie_details(sorted_df)

    # recommendations based on overlap, movie popularity (i.e. rating count), and count in user profile
    def get_recommendations_count(self, user_id):
        # use popularity based recommendations as a base
        df_popularity = self.get_recommendations_popularity(user_id)
        # use popularity as base rank
        user_profile = self.get_user_profile(user_id)

        ranks = []
        for _, row in df_popularity.iterrows():
            ranks.append(self.calculate_rank_wrt_profile_rating_count(row, user_profile))
        df_popularity['rank'] = ranks

        return df_popularity.sort_values(by='rank', ascending=False)

    # calculate rank by weighting current rank with mean of genre count for profile and genre overlap
    def calculate_rank_wrt_profile_rating_count(self, row, user_profile):
        # sum up user profile genre count for genres of movie
        genre_count_multiplier = 0
        movie_genres = self.__get_genre_set(row)
        for g in movie_genres:
            genre_count_multiplier += self.__get_user_rating_count(user_profile, g)

        # mean of genre count
        genre_count_multiplier = genre_count_multiplier / len(movie_genres)

        # weight rank by overlap and genre count
        return row['popularity'] * row['overlap'] * genre_count_multiplier

